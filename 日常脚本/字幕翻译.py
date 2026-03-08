#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
字幕翻译工具 - 使用DeepSeek API
支持SRT、ASS、VTT格式，自动识别语言并翻译
"""

import sys
import os
import re
import json
from pathlib import Path
from typing import List, Tuple, Optional
from dataclasses import dataclass
from datetime import timedelta

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QFileDialog, QComboBox, QProgressBar,
    QTextEdit, QGroupBox, QLineEdit, QMessageBox, QSpinBox
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QSettings
from PyQt6.QtGui import QFont, QPalette, QColor

import requests


# ==================== 配置管理 ====================

class ConfigManager:
    """配置管理器 - 用于保存和读取用户设置"""

    def __init__(self):
        # 使用QSettings来保存配置
        self.settings = QSettings("SubtitleTranslator", "Settings")

    def save_api_key(self, api_key: str):
        """保存API Key"""
        self.settings.setValue("api_key", api_key)
        self.settings.sync()

    def load_api_key(self) -> str:
        """读取API Key"""
        return self.settings.value("api_key", "", type=str)

    def save_last_settings(self, target_language: str, batch_size: int):
        """保存上次的设置"""
        self.settings.setValue("target_language", target_language)
        self.settings.setValue("batch_size", batch_size)
        self.settings.sync()

    def load_last_settings(self) -> tuple:
        """读取上次的设置"""
        target_language = self.settings.value("target_language", "中文", type=str)
        batch_size = self.settings.value("batch_size", 10, type=int)
        return target_language, batch_size


# ==================== 数据结构 ====================

@dataclass
class SubtitleBlock:
    """字幕块数据结构"""
    index: int
    start_time: str
    end_time: str
    text: str
    original_format: str  # 保存原始格式信息(如ASS的样式)


# ==================== 字幕解析器 ====================

class SubtitleParser:
    """字幕文件解析器"""

    @staticmethod
    def parse_srt(content: str) -> List[SubtitleBlock]:
        """解析SRT格式字幕"""
        blocks = []
        # 分割字幕块
        subtitle_blocks = re.split(r'\n\s*\n', content.strip())

        for block in subtitle_blocks:
            lines = block.strip().split('\n')
            if len(lines) < 3:
                continue

            try:
                index = int(lines[0].strip())
                time_line = lines[1].strip()
                text = '\n'.join(lines[2:])

                # 解析时间戳 (00:00:20,000 --> 00:00:24,400)
                time_match = re.match(
                    r'(\d{2}:\d{2}:\d{2},\d{3})\s*-->\s*(\d{2}:\d{2}:\d{2},\d{3})',
                    time_line)
                if time_match:
                    start_time, end_time = time_match.groups()
                    blocks.append(SubtitleBlock(
                        index=index,
                        start_time=start_time,
                        end_time=end_time,
                        text=text,
                        original_format='srt'
                    ))
            except (ValueError, IndexError):
                continue

        return blocks

    @staticmethod
    def parse_ass(content: str) -> List[SubtitleBlock]:
        """解析ASS/SSA格式字幕"""
        blocks = []
        lines = content.split('\n')

        # 找到Events部分
        in_events = False
        format_line = None

        for line in lines:
            line = line.strip()

            if line.startswith('[Events]'):
                in_events = True
                continue

            if in_events:
                if line.startswith('Format:'):
                    format_line = line[7:].strip()
                    continue

                if line.startswith('Dialogue:'):
                    if not format_line:
                        continue

                    # 解析对话行
                    dialogue_data = line[9:].strip()
                    parts = dialogue_data.split(',', 9)

                    if len(parts) >= 10:
                        start_time = parts[1].strip()
                        end_time = parts[2].strip()
                        text = parts[9].strip()

                        # 移除ASS特殊标记 (如 {\pos(x,y)})
                        text = re.sub(r'\{[^}]+\}', '', text)

                        blocks.append(SubtitleBlock(
                            index=len(blocks) + 1,
                            start_time=start_time,
                            end_time=end_time,
                            text=text,
                            original_format='ass'
                        ))

        return blocks

    @staticmethod
    def parse_vtt(content: str) -> List[SubtitleBlock]:
        """解析VTT格式字幕"""
        blocks = []
        # 移除WEBVTT头
        content = re.sub(r'^WEBVTT[^\n]*\n', '', content, flags=re.MULTILINE)

        subtitle_blocks = re.split(r'\n\s*\n', content.strip())

        for idx, block in enumerate(subtitle_blocks, 1):
            lines = block.strip().split('\n')
            if len(lines) < 2:
                continue

            # VTT可能有标识符行,也可能没有
            time_line_idx = 0
            if '-->' not in lines[0]:
                time_line_idx = 1

            if time_line_idx >= len(lines):
                continue

            time_line = lines[time_line_idx].strip()
            text = '\n'.join(lines[time_line_idx + 1:])

            # 解析时间戳 (00:00:20.000 --> 00:00:24.400)
            time_match = re.match(
                r'(\d{2}:\d{2}:\d{2}\.\d{3})\s*-->\s*(\d{2}:\d{2}:\d{2}\.\d{3})',
                time_line)
            if time_match:
                start_time, end_time = time_match.groups()
                blocks.append(SubtitleBlock(
                    index=idx,
                    start_time=start_time,
                    end_time=end_time,
                    text=text,
                    original_format='vtt'
                ))

        return blocks

    @staticmethod
    def auto_detect_format(content: str) -> Optional[str]:
        """自动检测字幕格式"""
        if content.strip().startswith('WEBVTT'):
            return 'vtt'
        elif '[Script Info]' in content or 'Dialogue:' in content:
            return 'ass'
        elif re.search(r'\d+\s*\n\d{2}:\d{2}:\d{2},\d{3}\s*-->', content):
            return 'srt'
        return None


# ==================== 字幕生成器 ====================

class SubtitleGenerator:
    """字幕文件生成器"""

    @staticmethod
    def generate_srt(blocks: List[SubtitleBlock]) -> str:
        """生成SRT格式字幕"""
        lines = []
        for block in blocks:
            lines.append(str(block.index))
            lines.append(f"{block.start_time} --> {block.end_time}")
            lines.append(block.text)
            lines.append('')
        return '\n'.join(lines)

    @staticmethod
    def generate_ass(blocks: List[SubtitleBlock], header: str = '') -> str:
        """生成ASS格式字幕"""
        if not header:
            # 使用默认ASS头
            header = """[Script Info]
Title: Translated Subtitle
ScriptType: v4.00+

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Arial,20,&H00FFFFFF,&H000000FF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,2,2,2,10,10,10,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

        lines = [header]
        for block in blocks:
            lines.append(
                f"Dialogue: 0,{block.start_time},{block.end_time},Default,,0,0,0,,{block.text}")

        return '\n'.join(lines)

    @staticmethod
    def generate_vtt(blocks: List[SubtitleBlock]) -> str:
        """生成VTT格式字幕"""
        lines = ['WEBVTT', '']
        for block in blocks:
            lines.append(f"{block.start_time} --> {block.end_time}")
            lines.append(block.text)
            lines.append('')
        return '\n'.join(lines)


# ==================== DeepSeek翻译器 ====================

class DeepSeekTranslator:
    """DeepSeek API翻译器"""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.api_url = "https://api.deepseek.com/v1/chat/completions"
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }

    def detect_language(self, text: str) -> str:
        """检测文本语言"""
        prompt = f"""请识别以下文本的语言,只回答语言名称(如:中文、英文、日文、韩文等),不要有其他内容:

{text[:500]}"""

        try:
            response = self._call_api(prompt, max_tokens=50)
            language = response.strip()
            return language
        except Exception as e:
            print(f"语言检测失败: {e}")
            return "未知"

    def translate_batch(self, texts: List[str], target_language: str,
                        source_language: str = "自动检测") -> List[str]:
        """批量翻译文本 - 提高token使用效率"""
        if not texts:
            return []

        # 构建批量翻译prompt - 使用序号标记
        text_list = []
        for idx, text in enumerate(texts, 1):
            text_list.append(f"[{idx}] {text}")

        combined_text = "\n".join(text_list)

        prompt = f"""请将以下字幕翻译为{target_language}。

要求:
1. 保持原文的语气和风格
2. 字幕翻译要简洁自然
3. 按照原序号格式返回,每行格式为: [序号] 翻译内容
4. 不要添加任何解释或额外内容

原文:
{combined_text}

翻译:"""

        try:
            response = self._call_api(prompt, max_tokens=len(combined_text) * 3)

            # 解析返回的翻译结果
            translations = []
            for line in response.strip().split('\n'):
                line = line.strip()
                if not line:
                    continue

                # 匹配 [序号] 内容 格式
                match = re.match(r'\[(\d+)\]\s*(.+)', line)
                if match:
                    translations.append(match.group(2))

            # 如果解析失败,尝试按行分割
            if len(translations) != len(texts):
                translations = [line.strip() for line in response.strip().split('\n') if
                                line.strip()]

            # 确保返回数量匹配
            if len(translations) < len(texts):
                translations.extend([''] * (len(texts) - len(translations)))

            return translations[:len(texts)]

        except Exception as e:
            print(f"批量翻译失败: {e}")
            return ['[翻译失败]'] * len(texts)

    def _call_api(self, prompt: str, max_tokens: int = 4000) -> str:
        """调用DeepSeek API"""
        data = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "max_tokens": max_tokens,
            "temperature": 0.3  # 降低随机性,提高翻译一致性
        }

        response = requests.post(
            self.api_url,
            headers=self.headers,
            json=data,
            timeout=60
        )

        if response.status_code != 200:
            raise Exception(f"API调用失败: {response.status_code} - {response.text}")

        result = response.json()
        return result['choices'][0]['message']['content']


# ==================== 翻译线程 ====================

class TranslationThread(QThread):
    """翻译工作线程"""

    progress_updated = pyqtSignal(int, str)  # 进度百分比, 状态信息
    translation_completed = pyqtSignal(str)  # 完成信号,传递输出文件路径
    translation_failed = pyqtSignal(str)  # 失败信号,传递错误信息
    status_message = pyqtSignal(str)  # 状态消息信号（不改变进度条）

    def __init__(self, input_file: str, output_file: str, api_key: str,
                 target_language: str, batch_size: int):
        super().__init__()
        self.input_file = input_file
        self.output_file = output_file
        self.api_key = api_key
        self.target_language = target_language
        self.batch_size = batch_size
        self.is_paused = False  # 暂停标志
        self.is_stopped = False  # 停止标志

    def pause(self):
        """暂停翻译"""
        self.is_paused = True

    def resume(self):
        """继续翻译"""
        self.is_paused = False

    def stop(self):
        """停止翻译"""
        self.is_stopped = True
        self.is_paused = False

    def run(self):
        """执行翻译任务"""
        try:
            # 读取文件
            self.status_message.emit("正在读取字幕文件...")
            with open(self.input_file, 'r', encoding='utf-8') as f:
                content = f.read()

            if self.is_stopped:
                return

            # 检测格式
            self.status_message.emit("正在检测字幕格式...")
            subtitle_format = SubtitleParser.auto_detect_format(content)
            if not subtitle_format:
                raise Exception("无法识别字幕格式,支持SRT、ASS、VTT格式")

            # 解析字幕
            self.status_message.emit(f"正在解析{subtitle_format.upper()}格式字幕...")
            if subtitle_format == 'srt':
                blocks = SubtitleParser.parse_srt(content)
            elif subtitle_format == 'ass':
                blocks = SubtitleParser.parse_ass(content)
            else:  # vtt
                blocks = SubtitleParser.parse_vtt(content)

            if not blocks:
                raise Exception("未能解析到有效字幕内容")

            if self.is_stopped:
                return

            # 语言检测
            self.status_message.emit("正在检测源语言...")
            translator = DeepSeekTranslator(self.api_key)
            sample_text = '\n'.join([b.text for b in blocks[:5]])
            detected_language = translator.detect_language(sample_text)
            self.status_message.emit(f"检测到源语言: {detected_language}")

            if self.is_stopped:
                return

            # 初始化进度条为0，开始翻译
            self.progress_updated.emit(0, f"开始翻译 {len(blocks)} 条字幕...")
            total_blocks = len(blocks)
            translated_blocks = []

            # 批量翻译
            for i in range(0, total_blocks, self.batch_size):
                # 检查是否停止
                if self.is_stopped:
                    self.translation_failed.emit("翻译已取消")
                    return

                # 检查是否暂停
                while self.is_paused and not self.is_stopped:
                    self.msleep(100)  # 暂停时每100ms检查一次

                if self.is_stopped:
                    self.translation_failed.emit("翻译已取消")
                    return

                batch = blocks[i:i + self.batch_size]
                texts = [b.text for b in batch]

                # 翻译当前批次
                translations = translator.translate_batch(texts, self.target_language,
                                                          detected_language)

                # 更新字幕块
                for block, translation in zip(batch, translations):
                    block.text = translation
                    translated_blocks.append(block)

                # 更新进度（0-100%，只反映翻译进度）
                completed = i + len(batch)
                progress_percent = int((completed / total_blocks) * 100)

                self.progress_updated.emit(
                    progress_percent,
                    f"正在翻译: {completed}/{total_blocks} 条字幕"
                )

            if self.is_stopped:
                self.translation_failed.emit("翻译已取消")
                return

            # 生成输出文件
            self.status_message.emit("正在生成翻译后的字幕文件...")
            if subtitle_format == 'srt':
                output_content = SubtitleGenerator.generate_srt(translated_blocks)
            elif subtitle_format == 'ass':
                # 保留原始ASS头部
                header_match = re.search(r'^(.*?\[Events\]\s*\n.*?Format:.*?\n)', content,
                                         re.DOTALL)
                header = header_match.group(1) if header_match else ''
                output_content = SubtitleGenerator.generate_ass(translated_blocks, header)
            else:  # vtt
                output_content = SubtitleGenerator.generate_vtt(translated_blocks)

            # 写入文件
            with open(self.output_file, 'w', encoding='utf-8') as f:
                f.write(output_content)

            self.progress_updated.emit(100, "翻译完成!")
            self.translation_completed.emit(self.output_file)

        except Exception as e:
            self.translation_failed.emit(str(e))


# ==================== 主窗口 ====================

class SubtitleTranslatorGUI(QMainWindow):
    """字幕翻译工具主窗口"""

    def __init__(self):
        super().__init__()
        self.translation_thread = None
        self.config_manager = ConfigManager()  # 添加配置管理器
        self.init_ui()
        self.load_saved_settings()  # 加载保存的设置

    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle("字幕翻译工具 - DeepSeek")
        # 修改默认大小，增加高度，并设置窗口显示尺寸
        self.setMinimumSize(800, 700)
        self.resize(900, 750)  # 设置默认启动大小

        # 设置现代化样式
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #cccccc;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
            QLineEdit, QComboBox, QSpinBox {
                padding: 8px;
                border: 1px solid #cccccc;
                border-radius: 4px;
                background-color: white;
                font-size: 13px;
            }
            QTextEdit {
                border: 1px solid #cccccc;
                border-radius: 4px;
                background-color: white;
                font-size: 12px;
            }
            QProgressBar {
                border: 1px solid #cccccc;
                border-radius: 5px;
                text-align: center;
                height: 25px;
                font-weight: bold;
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
                border-radius: 4px;
            }
            QLabel {
                font-size: 13px;
            }
        """)

        # 中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # 标题
        title_label = QLabel("🎬 字幕翻译工具")
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title_label)

        # API设置组
        api_group = QGroupBox("API 设置")
        api_layout = QHBoxLayout()
        api_layout.addWidget(QLabel("DeepSeek API Key:"))
        self.api_key_input = QLineEdit()
        self.api_key_input.setPlaceholderText("请输入您的 DeepSeek API Key")
        self.api_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        api_layout.addWidget(self.api_key_input)
        api_group.setLayout(api_layout)
        main_layout.addWidget(api_group)

        # 文件选择组
        file_group = QGroupBox("文件选择")
        file_layout = QVBoxLayout()

        # 输入文件
        input_layout = QHBoxLayout()
        input_layout.addWidget(QLabel("输入文件:"))
        self.input_file_label = QLineEdit()
        self.input_file_label.setReadOnly(True)
        self.input_file_label.setPlaceholderText("支持 SRT、ASS、VTT 格式")
        input_layout.addWidget(self.input_file_label)
        self.select_input_btn = QPushButton("选择文件")
        self.select_input_btn.clicked.connect(self.select_input_file)
        input_layout.addWidget(self.select_input_btn)
        file_layout.addLayout(input_layout)

        # 输出文件
        output_layout = QHBoxLayout()
        output_layout.addWidget(QLabel("输出文件:"))
        self.output_file_label = QLineEdit()
        self.output_file_label.setReadOnly(True)
        self.output_file_label.setPlaceholderText("自动生成或手动选择")
        output_layout.addWidget(self.output_file_label)
        self.select_output_btn = QPushButton("选择位置")
        self.select_output_btn.clicked.connect(self.select_output_file)
        output_layout.addWidget(self.select_output_btn)
        file_layout.addLayout(output_layout)

        file_group.setLayout(file_layout)
        main_layout.addWidget(file_group)

        # 翻译设置组
        translate_group = QGroupBox("翻译设置")
        translate_layout = QHBoxLayout()

        translate_layout.addWidget(QLabel("目标语言:"))
        self.target_language_combo = QComboBox()
        self.target_language_combo.addItems([
            "中文", "英文", "日文", "韩文", "法文", "德文",
            "西班牙文", "俄文", "阿拉伯文", "泰文"
        ])
        translate_layout.addWidget(self.target_language_combo)

        translate_layout.addWidget(QLabel("批量大小:"))
        self.batch_size_spinbox = QSpinBox()
        self.batch_size_spinbox.setRange(1, 100)  # 范围1-100
        self.batch_size_spinbox.setValue(10)
        self.batch_size_spinbox.setToolTip(
            "每次翻译的字幕条数,增大可提高效率但可能降低准确性\n可直接输入数字")
        self.batch_size_spinbox.setButtonSymbols(QSpinBox.ButtonSymbols.UpDownArrows)
        self.batch_size_spinbox.setKeyboardTracking(True)
        # 关键：设置为可编辑
        self.batch_size_spinbox.setMinimumWidth(80)
        translate_layout.addWidget(self.batch_size_spinbox)

        translate_layout.addStretch()
        translate_group.setLayout(translate_layout)
        main_layout.addWidget(translate_group)

        # 进度显示
        progress_group = QGroupBox("翻译进度")
        progress_layout = QVBoxLayout()

        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        progress_layout.addWidget(self.progress_bar)

        self.status_label = QLabel("就绪")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        progress_layout.addWidget(self.status_label)

        progress_group.setLayout(progress_layout)
        main_layout.addWidget(progress_group)

        # 日志显示
        log_group = QGroupBox("运行日志")
        log_layout = QVBoxLayout()
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMinimumHeight(180)  # 增加最小高度从150到180
        log_layout.addWidget(self.log_text)
        log_group.setLayout(log_layout)
        main_layout.addWidget(log_group)

        # 控制按钮组（开始翻译和暂停/继续）
        button_layout = QHBoxLayout()

        # 开始翻译按钮
        self.translate_btn = QPushButton("🚀 开始翻译")
        self.translate_btn.setMinimumHeight(45)
        self.translate_btn.clicked.connect(self.start_translation)
        button_layout.addWidget(self.translate_btn)

        # 暂停/继续按钮
        self.pause_btn = QPushButton("⏸ 暂停")
        self.pause_btn.setMinimumHeight(45)
        self.pause_btn.setEnabled(False)  # 初始禁用
        self.pause_btn.clicked.connect(self.toggle_pause)
        self.pause_btn.setStyleSheet("""
            QPushButton {
                background-color: #FF9800;
                color: white;
            }
            QPushButton:hover {
                background-color: #F57C00;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
        """)
        button_layout.addWidget(self.pause_btn)

        main_layout.addLayout(button_layout)

        # 添加说明
        info_label = QLabel("💡 提示: 批量大小可直接输入数字。建议值: 5-15")
        info_label.setStyleSheet("color: #666; font-size: 11px;")
        info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(info_label)

    def select_input_file(self):
        """选择输入文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "选择字幕文件",
            "",
            "字幕文件 (*.srt *.ass *.ssa *.vtt);;所有文件 (*.*)"
        )

        if file_path:
            self.input_file_label.setText(file_path)
            self.log(f"已选择输入文件: {file_path}")

            # 自动生成输出文件名
            if not self.output_file_label.text():
                input_path = Path(file_path)
                output_path = input_path.parent / f"{input_path.stem}_translated{input_path.suffix}"
                self.output_file_label.setText(str(output_path))

    def select_output_file(self):
        """选择输出文件"""
        input_file = self.input_file_label.text()
        if not input_file:
            QMessageBox.warning(self, "警告", "请先选择输入文件!")
            return

        input_path = Path(input_file)
        default_name = f"{input_path.stem}_translated{input_path.suffix}"

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "选择输出位置",
            str(input_path.parent / default_name),
            f"字幕文件 (*{input_path.suffix});;所有文件 (*.*)"
        )

        if file_path:
            self.output_file_label.setText(file_path)
            self.log(f"已选择输出文件: {file_path}")

    def start_translation(self):
        """开始翻译"""
        # 验证输入
        api_key = self.api_key_input.text().strip()
        if not api_key:
            QMessageBox.warning(self, "警告", "请输入 DeepSeek API Key!")
            return

        input_file = self.input_file_label.text()
        if not input_file or not os.path.exists(input_file):
            QMessageBox.warning(self, "警告", "请选择有效的输入文件!")
            return

        output_file = self.output_file_label.text()
        if not output_file:
            QMessageBox.warning(self, "警告", "请选择输出位置!")
            return

        # 保存API Key和设置
        self.config_manager.save_api_key(api_key)
        self.config_manager.save_last_settings(
            self.target_language_combo.currentText(),
            self.batch_size_spinbox.value()
        )

        # 更新按钮状态
        self.translate_btn.setEnabled(False)
        self.select_input_btn.setEnabled(False)
        self.select_output_btn.setEnabled(False)
        self.pause_btn.setEnabled(True)  # 启用暂停按钮
        self.pause_btn.setText("⏸ 暂停")

        # 清空日志和进度
        self.log_text.clear()
        self.progress_bar.setValue(0)

        self.log("=" * 50)
        self.log("开始翻译任务")
        self.log(f"输入: {input_file}")
        self.log(f"输出: {output_file}")
        self.log(f"目标语言: {self.target_language_combo.currentText()}")
        self.log(f"批量大小: {self.batch_size_spinbox.value()}")
        self.log("=" * 50)

        # 创建翻译线程
        self.translation_thread = TranslationThread(
            input_file=input_file,
            output_file=output_file,
            api_key=api_key,
            target_language=self.target_language_combo.currentText(),
            batch_size=self.batch_size_spinbox.value()
        )

        # 连接信号
        self.translation_thread.progress_updated.connect(self.update_progress)
        self.translation_thread.status_message.connect(self.update_status_only)  # 新增：状态消息
        self.translation_thread.translation_completed.connect(self.translation_completed)
        self.translation_thread.translation_failed.connect(self.translation_failed)

        # 启动线程
        self.translation_thread.start()

    def update_progress(self, progress: int, status: str):
        """更新进度"""
        self.progress_bar.setValue(progress)
        self.status_label.setText(status)
        self.log(status)

    def update_status_only(self, status: str):
        """只更新状态信息，不改变进度条"""
        self.status_label.setText(status)
        self.log(status)

    def toggle_pause(self):
        """切换暂停/继续状态"""
        if not self.translation_thread:
            return

        if self.pause_btn.text() == "⏸ 暂停":
            # 暂停
            self.translation_thread.pause()
            self.pause_btn.setText("▶ 继续")
            self.status_label.setText("已暂停")
            self.log("⏸ 翻译已暂停")
        else:
            # 继续
            self.translation_thread.resume()
            self.pause_btn.setText("⏸ 暂停")
            self.status_label.setText("继续翻译...")
            self.log("▶ 继续翻译")

    def translation_completed(self, output_file: str):
        """翻译完成"""
        self.log("=" * 50)
        self.log("✅ 翻译成功完成!")
        self.log(f"输出文件: {output_file}")
        self.log("=" * 50)

        # 恢复按钮
        self.translate_btn.setEnabled(True)
        self.select_input_btn.setEnabled(True)
        self.select_output_btn.setEnabled(True)
        self.pause_btn.setEnabled(False)  # 禁用暂停按钮
        self.pause_btn.setText("⏸ 暂停")  # 重置文本

        QMessageBox.information(
            self,
            "翻译完成",
            f"字幕翻译成功!\n\n输出文件:\n{output_file}"
        )

    def translation_failed(self, error: str):
        """翻译失败"""
        self.log("=" * 50)
        self.log(f"❌ 翻译失败: {error}")
        self.log("=" * 50)

        # 恢复按钮
        self.translate_btn.setEnabled(True)
        self.select_input_btn.setEnabled(True)
        self.select_output_btn.setEnabled(True)
        self.pause_btn.setEnabled(False)  # 禁用暂停按钮
        self.pause_btn.setText("⏸ 暂停")  # 重置文本

        QMessageBox.critical(
            self,
            "翻译失败",
            f"翻译过程中发生错误:\n\n{error}"
        )

    def log(self, message: str):
        """添加日志"""
        self.log_text.append(message)
        # 自动滚动到底部
        self.log_text.verticalScrollBar().setValue(
            self.log_text.verticalScrollBar().maximum()
        )

    def load_saved_settings(self):
        """加载保存的设置"""
        # 加载API Key
        saved_api_key = self.config_manager.load_api_key()
        if saved_api_key:
            self.api_key_input.setText(saved_api_key)

        # 加载上次的设置
        target_language, batch_size = self.config_manager.load_last_settings()

        # 设置目标语言
        index = self.target_language_combo.findText(target_language)
        if index >= 0:
            self.target_language_combo.setCurrentIndex(index)

        # 设置批量大小
        self.batch_size_spinbox.setValue(batch_size)


# ==================== 主程序 ====================

def main():
    """主程序入口"""
    app = QApplication(sys.argv)

    # 设置应用程序信息
    app.setApplicationName("字幕翻译工具")
    app.setOrganizationName("SubtitleTranslator")

    # 创建并显示主窗口
    window = SubtitleTranslatorGUI()
    window.show()

    sys.exit(app.exec())


if __name__ == '__main__':
    main()