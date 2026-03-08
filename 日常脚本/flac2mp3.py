#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
音乐格式转换器 V3.2 - 极速版
使用直接 FFmpeg 调用，避免重复启动进程
大幅提升批量转换速度
"""

import os
import sys
import threading
import subprocess
import platform
from pathlib import Path
from tkinter import Tk, Frame, Label, Button, Entry, StringVar, IntVar, DoubleVar
from tkinter import filedialog, messagebox, ttk, Toplevel
from tkinter.scrolledtext import ScrolledText
import json

# 不再依赖 pydub，直接使用 FFmpeg
SUPPORTED_INPUT_FORMATS = ['.mp3', '.wav', '.flac', '.ogg', '.m4a', '.aac', '.wma',
                           '.opus']
SUPPORTED_OUTPUT_FORMATS = ['mp3', 'wav', 'flac', 'ogg', 'm4a', 'aac', 'opus']


class FFmpegConfig:
    """FFmpeg配置管理类"""

    def __init__(self):
        """初始化配置"""
        self.config_file = Path.home() / '.music_converter_config.json'
        self.ffmpeg_path = None
        self.ffprobe_path = None
        self.load_config()

    def load_config(self):
        """加载配置文件"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    self.ffmpeg_path = config.get('ffmpeg_path')
                    self.ffprobe_path = config.get('ffprobe_path')
        except Exception as e:
            print(f"加载配置失败: {e}")

    def save_config(self):
        """保存配置文件"""
        try:
            config = {
                'ffmpeg_path': self.ffmpeg_path,
                'ffprobe_path': self.ffprobe_path
            }
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            print(f"保存配置失败: {e}")

    def auto_detect_ffmpeg(self):
        """自动检测ffmpeg路径"""
        # 先尝试运行 ffmpeg 命令
        try:
            result = subprocess.run(['ffmpeg', '-version'],
                                    capture_output=True,
                                    text=True,
                                    timeout=5)
            if 'ffmpeg version' in result.stdout.lower():
                self.ffmpeg_path = 'ffmpeg'  # 在 PATH 中
                self.ffprobe_path = 'ffprobe'
                self.save_config()
                return True
        except:
            pass

        # 搜索常见路径
        common_paths = self._get_common_paths()

        for base_path in common_paths:
            ffmpeg_exe = base_path / (
                'ffmpeg.exe' if platform.system() == 'Windows' else 'ffmpeg')
            ffprobe_exe = base_path / (
                'ffprobe.exe' if platform.system() == 'Windows' else 'ffprobe')

            if ffmpeg_exe.exists():
                self.ffmpeg_path = str(ffmpeg_exe)
                self.ffprobe_path = str(ffprobe_exe) if ffprobe_exe.exists() else None
                self.save_config()
                return True

        return False

    def _get_common_paths(self):
        """获取常见的ffmpeg安装路径"""
        paths = []

        if platform.system() == 'Windows':
            paths.extend([
                Path('C:/ffmpeg/bin'),
                Path('C:/Program Files/ffmpeg/bin'),
                Path('C:/Program Files (x86)/ffmpeg/bin'),
                Path(os.environ.get('LOCALAPPDATA', '')) / 'ffmpeg/bin',
            ])
        elif platform.system() == 'Darwin':
            paths.extend([
                Path('/usr/local/bin'),
                Path('/opt/homebrew/bin'),
                Path('/usr/bin'),
            ])
        else:
            paths.extend([
                Path('/usr/bin'),
                Path('/usr/local/bin'),
                Path('/opt/ffmpeg/bin'),
            ])

        return [p for p in paths if p.exists()]

    def set_ffmpeg_path(self, path):
        """手动设置ffmpeg路径"""
        path = Path(path)

        if path.is_dir():
            ffmpeg_exe = path / (
                'ffmpeg.exe' if platform.system() == 'Windows' else 'ffmpeg')
            if ffmpeg_exe.exists():
                path = ffmpeg_exe
            else:
                return False, "所选目录中未找到ffmpeg可执行文件"

        if not path.exists():
            return False, "文件不存在"

        if not self._verify_ffmpeg(str(path)):
            return False, "这不是有效的ffmpeg可执行文件"

        self.ffmpeg_path = str(path)

        ffprobe = path.parent / (
            'ffprobe.exe' if platform.system() == 'Windows' else 'ffprobe')
        if ffprobe.exists():
            self.ffprobe_path = str(ffprobe)

        self.save_config()
        return True, "ffmpeg路径设置成功"

    def _verify_ffmpeg(self, path):
        """验证ffmpeg可执行文件"""
        try:
            result = subprocess.run([path, '-version'],
                                    capture_output=True,
                                    text=True,
                                    timeout=5)
            return 'ffmpeg version' in result.stdout.lower()
        except Exception:
            return False

    def is_configured(self):
        """检查是否已配置"""
        if not self.ffmpeg_path:
            return False

        # 如果是 'ffmpeg' (在 PATH 中)，检查是否能运行
        if self.ffmpeg_path == 'ffmpeg':
            try:
                subprocess.run(['ffmpeg', '-version'],
                               capture_output=True,
                               timeout=5)
                return True
            except:
                return False

        # 否则检查文件是否存在
        return Path(self.ffmpeg_path).exists()


class FFmpegSetupDialog:
    """FFmpeg设置对话框"""

    def __init__(self, parent, config):
        """初始化对话框"""
        self.config = config
        self.result = False

        self.dialog = Toplevel(parent)
        self.dialog.title("FFmpeg 配置")
        self.dialog.geometry("650x450")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        self.dialog.resizable(False, False)

        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - 325
        y = (self.dialog.winfo_screenheight() // 2) - 225
        self.dialog.geometry(f"650x450+{x}+{y}")

        self.dialog.configure(bg='#f5f6fa')

        self.create_widgets()

    def create_widgets(self):
        """创建对话框组件"""
        header_frame = Frame(self.dialog, bg='#4834d4', height=80)
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)

        title_label = Label(header_frame, text="⚙️ FFmpeg 配置向导",
                            font=('Microsoft YaHei UI', 20, 'bold'),
                            bg='#4834d4', fg='white')
        title_label.pack(expand=True)

        content_frame = Frame(self.dialog, bg='#f5f6fa', padx=30, pady=20)
        content_frame.pack(fill='both', expand=True)

        info_frame = Frame(content_frame, bg='white', relief='flat', bd=0)
        info_frame.pack(fill='x', pady=(0, 20))

        info_inner = Frame(info_frame, bg='#e8f4f8', padx=20, pady=15)
        info_inner.pack(fill='x', padx=2, pady=2)

        info_text = (
            "🎵 程序需要 FFmpeg 来处理音频文件\n\n"
            "您可以：\n"
            "  • 点击「自动检测」让程序查找 FFmpeg\n"
            "  • 点击「手动选择」指定 FFmpeg 位置\n"
            "  • 如果未安装，请先下载安装 FFmpeg"
        )

        info_label = Label(info_inner, text=info_text,
                           font=('Microsoft YaHei UI', 10),
                           bg='#e8f4f8', fg='#2c3e50',
                           justify='left')
        info_label.pack(anchor='w')

        path_frame = Frame(content_frame, bg='white', relief='flat', bd=0)
        path_frame.pack(fill='x', pady=(0, 20))

        path_inner = Frame(path_frame, bg='#f8f9fa', padx=20, pady=15)
        path_inner.pack(fill='x', padx=2, pady=2)

        Label(path_inner, text="📁 当前 FFmpeg 路径:",
              font=('Microsoft YaHei UI', 10, 'bold'),
              bg='#f8f9fa', fg='#2c3e50').pack(anchor='w')

        self.path_var = StringVar()
        if self.config.ffmpeg_path:
            self.path_var.set(self.config.ffmpeg_path)
        else:
            self.path_var.set("未配置")

        path_display = Label(path_inner, textvariable=self.path_var,
                             font=('Consolas', 9),
                             bg='#f8f9fa', fg='#6c757d',
                             wraplength=570, justify='left')
        path_display.pack(anchor='w', pady=(8, 0))

        button_frame = Frame(content_frame, bg='#f5f6fa')
        button_frame.pack(fill='x', pady=(0, 15))

        style = ttk.Style()
        style.configure('Modern.TButton',
                        font=('Microsoft YaHei UI', 11),
                        padding=10)

        auto_btn = ttk.Button(button_frame, text="🔍 自动检测",
                              command=self.auto_detect,
                              style='Modern.TButton')
        auto_btn.pack(side='left', expand=True, fill='x', padx=(0, 10))

        manual_btn = ttk.Button(button_frame, text="📁 手动选择",
                                command=self.manual_select,
                                style='Modern.TButton')
        manual_btn.pack(side='left', expand=True, fill='x')

        download_frame = Frame(content_frame, bg='#fff3cd', relief='flat', bd=0)
        download_frame.pack(fill='x', pady=(0, 20))

        download_inner = Frame(download_frame, bg='#fff3cd', padx=20, pady=15)
        download_inner.pack(fill='x', padx=2, pady=2)

        Label(download_inner, text="💡 如需下载 FFmpeg:",
              font=('Microsoft YaHei UI', 10, 'bold'),
              bg='#fff3cd', fg='#856404').pack(anchor='w')

        link_text = "https://ffmpeg.org/download.html"
        link_label = Label(download_inner, text=link_text,
                           font=('Microsoft YaHei UI', 9, 'underline'),
                           bg='#fff3cd', fg='#0066cc',
                           cursor='hand2')
        link_label.pack(anchor='w', pady=(5, 0))
        link_label.bind('<Button-1>', lambda e: self.open_url(link_text))

        bottom_frame = Frame(content_frame, bg='#f5f6fa')
        bottom_frame.pack(side='bottom', fill='x')

        self.ok_btn = ttk.Button(bottom_frame, text="✓ 确定",
                                 command=self.on_ok,
                                 style='Modern.TButton',
                                 state='disabled' if not self.config.is_configured() else 'normal')
        self.ok_btn.pack(side='right', padx=(10, 0))

        cancel_btn = ttk.Button(bottom_frame, text="✗ 取消",
                                command=self.on_cancel,
                                style='Modern.TButton')
        cancel_btn.pack(side='right')

    def auto_detect(self):
        """自动检测ffmpeg"""
        if self.config.auto_detect_ffmpeg():
            self.path_var.set(self.config.ffmpeg_path)
            self.ok_btn.config(state='normal')
            messagebox.showinfo("成功",
                                f"✓ 已自动检测到 FFmpeg:\n\n{self.config.ffmpeg_path}",
                                parent=self.dialog)
        else:
            messagebox.showwarning("未找到",
                                   "✗ 未能自动检测到 FFmpeg\n\n请手动选择或先安装 FFmpeg",
                                   parent=self.dialog)

    def manual_select(self):
        """手动选择ffmpeg"""
        filetypes = []
        if platform.system() == 'Windows':
            filetypes = [("可执行文件", "*.exe"), ("所有文件", "*.*")]
        else:
            filetypes = [("所有文件", "*")]

        filepath = filedialog.askopenfilename(
            title="选择 FFmpeg 可执行文件",
            filetypes=filetypes,
            parent=self.dialog
        )

        if filepath:
            success, message = self.config.set_ffmpeg_path(filepath)
            if success:
                self.path_var.set(self.config.ffmpeg_path)
                self.ok_btn.config(state='normal')
                messagebox.showinfo("成功", f"✓ {message}", parent=self.dialog)
            else:
                messagebox.showerror("错误", f"✗ {message}", parent=self.dialog)

    def open_url(self, url):
        """打开URL"""
        import webbrowser
        webbrowser.open(url)

    def on_ok(self):
        """确定按钮"""
        if self.config.is_configured():
            self.result = True
            self.dialog.destroy()
        else:
            messagebox.showwarning("警告", "请先配置 FFmpeg 路径", parent=self.dialog)

    def on_cancel(self):
        """取消按钮"""
        self.result = False
        self.dialog.destroy()

    def show(self):
        """显示对话框并等待结果"""
        self.dialog.wait_window()
        return self.result


class DirectFFmpegConverter:
    """直接使用 FFmpeg 命令行的转换器 - 极速版"""

    def __init__(self, ffmpeg_config):
        """初始化转换器"""
        self.config = ffmpeg_config
        self.ffmpeg_cmd = self.config.ffmpeg_path

    def get_audio_files(self, directory):
        """获取目录中的音频文件（只扫描当前目录）"""
        audio_files = []
        directory = Path(directory)

        if not directory.exists():
            return audio_files

        for file_path in directory.iterdir():
            if file_path.is_file() and file_path.suffix.lower() in SUPPORTED_INPUT_FORMATS:
                audio_files.append(file_path)

        return sorted(audio_files)

    def convert_audio(self, input_file, output_format, output_dir=None,
                      bitrate='192k', callback=None):
        """使用 FFmpeg 直接转换音频 - 一次调用完成"""
        try:
            input_path = Path(input_file)

            if not input_path.exists():
                raise FileNotFoundError(f"输入文件不存在: {input_path}")

            if output_dir is None:
                output_dir = input_path.parent
            else:
                output_dir = Path(output_dir)
                output_dir.mkdir(parents=True, exist_ok=True)

            output_filename = f"{input_path.stem}.{output_format}"
            output_path = output_dir / output_filename

            counter = 1
            while output_path.exists():
                output_filename = f"{input_path.stem}_{counter}.{output_format}"
                output_path = output_dir / output_filename
                counter += 1

            if callback:
                callback(f"正在转换: {input_path.name}")

            # 构建 FFmpeg 命令
            cmd = [
                self.ffmpeg_cmd,
                '-i', str(input_path.absolute()),
                '-y',  # 覆盖输出文件
                '-hide_banner',  # 隐藏版本信息
                '-loglevel', 'error',  # 只显示错误
            ]

            # 根据输出格式设置参数
            if output_format == 'mp3':
                cmd.extend(['-codec:a', 'libmp3lame', '-b:a', bitrate])
            elif output_format == 'wav':
                cmd.extend(['-codec:a', 'pcm_s16le'])
            elif output_format == 'flac':
                cmd.extend(['-codec:a', 'flac'])
            elif output_format == 'ogg':
                cmd.extend(['-codec:a', 'libvorbis', '-b:a', bitrate])
            elif output_format == 'opus':
                cmd.extend(['-codec:a', 'libopus', '-b:a', bitrate])
            elif output_format in ['m4a', 'aac']:
                cmd.extend(['-codec:a', 'aac', '-b:a', bitrate])

            cmd.append(str(output_path.absolute()))

            # 执行 FFmpeg 命令
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=3600,  # 1小时超时
                creationflags=subprocess.CREATE_NO_WINDOW if platform.system() == 'Windows' else 0
            )

            if result.returncode == 0:
                if callback:
                    callback(f"✓ 完成: {output_filename}")
                return str(output_path)
            else:
                error_msg = result.stderr if result.stderr else "未知错误"
                if callback:
                    callback(f"✗ FFmpeg 错误: {error_msg[:100]}")
                return None

        except subprocess.TimeoutExpired:
            if callback:
                callback(f"✗ 超时: {input_path.name} (转换时间超过1小时)")
            return None
        except Exception as e:
            if callback:
                callback(f"✗ 错误: {input_path.name} - {str(e)}")
            return None


class ModernMusicConverterGUI:
    """现代化音乐转换器GUI界面 V3.2 极速版"""

    def __init__(self, root):
        """初始化GUI"""
        self.root = root
        self.root.title("音乐格式转换器 V3.2 极速版")

        self.setup_window()

        self.ffmpeg_config = FFmpegConfig()

        if not self.ffmpeg_config.is_configured():
            if not self.show_ffmpeg_setup():
                messagebox.showwarning("警告", "未配置 FFmpeg，程序将退出")
                sys.exit(0)
        else:
            if not self.ffmpeg_config.is_configured():
                messagebox.showwarning("警告", "之前配置的 FFmpeg 路径已失效，请重新配置")
                if not self.show_ffmpeg_setup():
                    sys.exit(0)

        try:
            self.converter = DirectFFmpegConverter(self.ffmpeg_config)
        except Exception as e:
            messagebox.showerror("错误", f"初始化转换器失败: {str(e)}")
            sys.exit(1)

        self.input_dir = StringVar()
        self.output_dir = StringVar()
        self.output_format = StringVar(value='mp3')
        self.bitrate = StringVar(value='192k')
        self.use_custom_output = IntVar(value=0)
        self.progress_var = DoubleVar()

        self.create_widgets()

        self.converting = False

    def show_ffmpeg_setup(self):
        """显示FFmpeg设置对话框"""
        dialog = FFmpegSetupDialog(self.root, self.ffmpeg_config)
        return dialog.show()

    def setup_window(self):
        """设置窗口大小和样式"""
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        if screen_width >= 3840:
            window_width, window_height = 1400, 900
            self.font_scale = 1.4
        elif screen_width >= 2560:
            window_width, window_height = 1200, 800
            self.font_scale = 1.2
        else:
            window_width, window_height = 1000, 700
            self.font_scale = 1.0

        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2

        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        self.root.minsize(900, 650)
        self.root.configure(bg='#f5f6fa')

        style = ttk.Style()
        style.theme_use('clam')

        style.configure('Title.TLabel',
                        font=('Microsoft YaHei UI', int(24 * self.font_scale), 'bold'),
                        background='#f5f6fa',
                        foreground='#2c3e50')

        style.configure('Modern.TButton',
                        font=('Microsoft YaHei UI', int(10 * self.font_scale)),
                        padding=8)

        style.configure('Primary.TButton',
                        font=('Microsoft YaHei UI', int(12 * self.font_scale), 'bold'),
                        padding=12)

    def create_widgets(self):
        """创建GUI组件"""
        self.create_header()

        main_container = Frame(self.root, bg='#f5f6fa')
        main_container.pack(fill='both', expand=True, padx=20, pady=(0, 20))

        left_panel = Frame(main_container, bg='#f5f6fa')
        left_panel.pack(side='left', fill='both', expand=True, padx=(0, 10))

        self.create_input_section(left_panel)
        self.create_output_section(left_panel)
        self.create_settings_section(left_panel)
        self.create_action_buttons(left_panel)

        right_panel = Frame(main_container, bg='#f5f6fa')
        right_panel.pack(side='right', fill='both', expand=True, padx=(10, 0))

        self.create_progress_section(right_panel)

    def create_header(self):
        """创建顶部栏"""
        header = Frame(self.root, bg='#27ae60', height=100)
        header.pack(fill='x')
        header.pack_propagate(False)

        header_content = Frame(header, bg='#27ae60')
        header_content.pack(expand=True, fill='both', padx=30)

        title_frame = Frame(header_content, bg='#27ae60')
        title_frame.pack(side='left', fill='y')

        Label(title_frame, text="⚡ 音乐格式转换器 极速版",
              font=('Microsoft YaHei UI', int(24 * self.font_scale), 'bold'),
              bg='#27ae60', fg='white').pack(anchor='w')

        Label(title_frame, text="直接调用 FFmpeg，批量转换更快速 V3.2",
              font=('Microsoft YaHei UI', int(10 * self.font_scale)),
              bg='#27ae60', fg='#ecf0f1').pack(anchor='w', pady=(5, 0))

        right_frame = Frame(header_content, bg='#27ae60')
        right_frame.pack(side='right', fill='y')

        status_frame = Frame(right_frame, bg='#229954', relief='flat')
        status_frame.pack(pady=10, padx=10)

        status_inner = Frame(status_frame, bg='#229954', padx=15, pady=8)
        status_inner.pack()

        Label(status_inner, text="✓ FFmpeg 已配置",
              font=('Microsoft YaHei UI', int(9 * self.font_scale)),
              bg='#229954', fg='white').pack(side='left', padx=(0, 10))

        settings_btn = Button(status_inner, text="⚙️ 设置",
                              font=('Microsoft YaHei UI', int(9 * self.font_scale)),
                              bg='#1e8449', fg='white',
                              relief='flat', cursor='hand2',
                              padx=15, pady=5,
                              command=self.open_ffmpeg_settings)
        settings_btn.pack(side='right')

    def create_input_section(self, parent):
        """创建输入目录选择区域"""
        section = self.create_section_frame(parent,
                                            "📂 输入目录（只处理当前目录，不含子文件夹）")

        entry_frame = Frame(section, bg='white')
        entry_frame.pack(fill='x')

        entry = Entry(entry_frame, textvariable=self.input_dir,
                      font=('Microsoft YaHei UI', int(10 * self.font_scale)),
                      bg='white', fg='#2c3e50',
                      relief='flat', bd=0)
        entry.pack(side='left', fill='both', expand=True, padx=15, pady=12)

        browse_btn = Button(entry_frame, text="浏览",
                            font=('Microsoft YaHei UI', int(10 * self.font_scale)),
                            bg='#3498db', fg='white',
                            relief='flat', cursor='hand2',
                            padx=20, pady=8,
                            command=self.browse_input_dir)
        browse_btn.pack(side='right', padx=10, pady=8)

    def create_output_section(self, parent):
        """创建输出目录选择区域"""
        section = self.create_section_frame(parent, "📁 输出目录（可选）")

        check_frame = Frame(section, bg='white')
        check_frame.pack(fill='x', padx=15, pady=(10, 5))

        check = ttk.Checkbutton(check_frame, text="使用自定义输出目录",
                                variable=self.use_custom_output,
                                command=self.toggle_output_dir)
        check.pack(anchor='w')

        entry_frame = Frame(section, bg='white')
        entry_frame.pack(fill='x')

        self.output_entry = Entry(entry_frame, textvariable=self.output_dir,
                                  font=('Microsoft YaHei UI', int(10 * self.font_scale)),
                                  bg='#ecf0f1', fg='#2c3e50',
                                  relief='flat', bd=0, state='disabled')
        self.output_entry.pack(side='left', fill='both', expand=True, padx=15, pady=12)

        self.output_btn = Button(entry_frame, text="浏览",
                                 font=('Microsoft YaHei UI', int(10 * self.font_scale)),
                                 bg='#95a5a6', fg='white',
                                 relief='flat', cursor='hand2',
                                 padx=20, pady=8, state='disabled',
                                 command=self.browse_output_dir)
        self.output_btn.pack(side='right', padx=10, pady=8)

    def create_settings_section(self, parent):
        """创建转换设置区域"""
        section = self.create_section_frame(parent, "⚙️ 转换设置")

        settings_grid = Frame(section, bg='white')
        settings_grid.pack(fill='x', padx=15, pady=15)

        Label(settings_grid, text="输出格式:",
              font=('Microsoft YaHei UI', int(10 * self.font_scale)),
              bg='white', fg='#2c3e50').grid(row=0, column=0, sticky='w', pady=5)

        format_combo = ttk.Combobox(settings_grid, textvariable=self.output_format,
                                    values=SUPPORTED_OUTPUT_FORMATS,
                                    state='readonly',
                                    font=('Microsoft YaHei UI',
                                          int(10 * self.font_scale)),
                                    width=20)
        format_combo.grid(row=0, column=1, sticky='ew', padx=(10, 0), pady=5)

        Label(settings_grid, text="比特率:",
              font=('Microsoft YaHei UI', int(10 * self.font_scale)),
              bg='white', fg='#2c3e50').grid(row=1, column=0, sticky='w', pady=5)

        bitrate_combo = ttk.Combobox(settings_grid, textvariable=self.bitrate,
                                     values=['128k', '192k', '256k', '320k'],
                                     state='readonly',
                                     font=('Microsoft YaHei UI',
                                           int(10 * self.font_scale)),
                                     width=20)
        bitrate_combo.grid(row=1, column=1, sticky='ew', padx=(10, 0), pady=5)

        tip_label = Label(settings_grid,
                          text="⚡ 极速模式：每个文件只调用一次 FFmpeg",
                          font=('Microsoft YaHei UI', int(8 * self.font_scale)),
                          bg='white', fg='#27ae60',)
                          # font=('Microsoft YaHei UI', int(8 * self.font_scale), 'bold'))
        tip_label.grid(row=2, column=0, columnspan=2, sticky='w', pady=(10, 0))

        settings_grid.columnconfigure(1, weight=1)

    def create_action_buttons(self, parent):
        """创建操作按钮"""
        button_frame = Frame(parent, bg='#f5f6fa')
        button_frame.pack(fill='x', pady=(20, 0))

        self.convert_btn = Button(button_frame, text="⚡ 极速转换",
                                  font=('Microsoft YaHei UI', int(12 * self.font_scale),
                                        'bold'),
                                  bg='#27ae60', fg='white',
                                  relief='flat', cursor='hand2',
                                  padx=20, pady=15,
                                  command=self.start_conversion)
        self.convert_btn.pack(fill='x')

    def create_progress_section(self, parent):
        """创建进度和日志区域"""
        section = self.create_section_frame(parent, "📊 转换进度", fill_height=True)

        progress_frame = Frame(section, bg='white')
        progress_frame.pack(fill='x', padx=15, pady=15)

        self.progress_bar = ttk.Progressbar(progress_frame,
                                            variable=self.progress_var,
                                            maximum=100,
                                            mode='determinate',
                                            length=400)
        self.progress_bar.pack(fill='x')

        self.progress_label = Label(progress_frame, text="就绪",
                                    font=('Microsoft YaHei UI', int(9 * self.font_scale)),
                                    bg='white', fg='#7f8c8d')
        self.progress_label.pack(pady=(8, 0))

        log_frame = Frame(section, bg='white')
        log_frame.pack(fill='both', expand=True, padx=15, pady=(0, 15))

        Label(log_frame, text="📝 转换日志:",
              font=('Microsoft YaHei UI', int(10 * self.font_scale)),
              bg='white', fg='#2c3e50').pack(anchor='w', pady=(0, 5))

        self.log_text = ScrolledText(log_frame,
                                     font=('Consolas', int(9 * self.font_scale)),
                                     bg='#f8f9fa', fg='#2c3e50',
                                     relief='flat', bd=0,
                                     wrap='word', height=15)
        self.log_text.pack(fill='both', expand=True)

        clear_btn = Button(section, text="🗑️ 清除日志",
                           font=('Microsoft YaHei UI', int(9 * self.font_scale)),
                           bg='#95a5a6', fg='white',
                           relief='flat', cursor='hand2',
                           padx=15, pady=8,
                           command=self.clear_log)
        clear_btn.pack(side='bottom', anchor='e', padx=15, pady=(0, 15))

    def create_section_frame(self, parent, title, fill_height=False):
        """创建区域框架"""
        container = Frame(parent, bg='#f5f6fa')
        if fill_height:
            container.pack(fill='both', expand=True, pady=(0, 15))
        else:
            container.pack(fill='x', pady=(0, 15))

        Label(container, text=title,
              font=('Microsoft YaHei UI', int(11 * self.font_scale), 'bold'),
              bg='#f5f6fa', fg='#2c3e50').pack(anchor='w', pady=(0, 8))

        frame = Frame(container, bg='white', relief='flat', bd=0)
        if fill_height:
            frame.pack(fill='both', expand=True)
        else:
            frame.pack(fill='x')

        shadow = Frame(container, bg='#dfe6e9', height=2)
        shadow.pack(fill='x')

        return frame

    def open_ffmpeg_settings(self):
        """打开FFmpeg设置"""
        dialog = FFmpegSetupDialog(self.root, self.ffmpeg_config)
        if dialog.show():
            messagebox.showinfo("成功", "✓ FFmpeg配置已更新")

    def browse_input_dir(self):
        """浏览输入目录"""
        directory = filedialog.askdirectory(title="选择输入目录")
        if directory:
            self.input_dir.set(directory)

    def browse_output_dir(self):
        """浏览输出目录"""
        directory = filedialog.askdirectory(title="选择输出目录")
        if directory:
            self.output_dir.set(directory)

    def toggle_output_dir(self):
        """切换输出目录状态"""
        if self.use_custom_output.get():
            self.output_entry.config(state='normal', bg='white')
            self.output_btn.config(state='normal', bg='#3498db')
        else:
            self.output_entry.config(state='disabled', bg='#ecf0f1')
            self.output_btn.config(state='disabled', bg='#95a5a6')
            self.output_dir.set('')

    def log_message(self, message):
        """添加日志消息"""
        self.log_text.insert('end', f"{message}\n")
        self.log_text.see('end')
        self.root.update_idletasks()

    def clear_log(self):
        """清除日志"""
        self.log_text.delete('1.0', 'end')

    def start_conversion(self):
        """开始转换"""
        if self.converting:
            messagebox.showwarning("警告", "转换正在进行中...")
            return

        if not self.input_dir.get():
            messagebox.showerror("错误", "请选择输入目录")
            return

        if not os.path.isdir(self.input_dir.get()):
            messagebox.showerror("错误", "输入目录不存在")
            return

        output_dir = None
        if self.use_custom_output.get():
            if not self.output_dir.get():
                messagebox.showerror("错误", "请选择输出目录")
                return
            output_dir = self.output_dir.get()

        self.converting = True
        self.convert_btn.config(text="⏸ 转换中...", state='disabled', bg='#95a5a6')
        self.progress_label.config(text="准备中...")
        self.clear_log()

        thread = threading.Thread(target=self.conversion_thread,
                                  args=(self.input_dir.get(), output_dir))
        thread.daemon = True
        thread.start()

    def conversion_thread(self, input_dir, output_dir):
        """转换线程"""
        try:
            audio_files = self.converter.get_audio_files(input_dir)

            if not audio_files:
                self.root.after(0, lambda: messagebox.showinfo("提示",
                                                               "当前目录中未找到支持的音频文件\n\n注意：程序只处理当前目录，不包含子文件夹"))
                return

            total_files = len(audio_files)
            self.root.after(0, lambda: self.log_message(f"⚡ 极速模式启动"))
            self.root.after(0, lambda: self.log_message(
                f"📁 在当前目录找到 {total_files} 个音频文件\n"))

            import time
            start_time = time.time()

            success_count = 0
            for idx, audio_file in enumerate(audio_files, 1):
                progress = (idx / total_files) * 100
                self.root.after(0, lambda p=progress: self.progress_var.set(p))
                self.root.after(0, lambda i=idx, t=total_files:
                self.progress_label.config(text=f"正在转换 {i}/{t}..."))

                result = self.converter.convert_audio(
                    audio_file,
                    self.output_format.get(),
                    output_dir,
                    self.bitrate.get(),
                    callback=lambda msg: self.root.after(0,
                                                         lambda m=msg: self.log_message(
                                                             m))
                )

                if result:
                    success_count += 1

            elapsed_time = time.time() - start_time
            avg_time = elapsed_time / total_files if total_files > 0 else 0

            self.root.after(0, lambda: self.log_message(f"\n{'=' * 50}"))
            self.root.after(0, lambda: self.log_message(f"✓ 转换完成！"))
            self.root.after(0, lambda: self.log_message(
                f"成功: {success_count}/{total_files}"))
            self.root.after(0, lambda: self.log_message(f"总耗时: {elapsed_time:.1f}秒"))
            self.root.after(0, lambda: self.log_message(f"平均每首: {avg_time:.1f}秒"))
            self.root.after(0, lambda: self.progress_label.config(
                text=f"完成 ({success_count}/{total_files})"))
            self.root.after(0, lambda: messagebox.showinfo("完成",
                                                           f"⚡ 极速转换完成！\n\n成功: {success_count}/{total_files}\n总耗时: {elapsed_time:.1f}秒\n平均: {avg_time:.1f}秒/首"))

        except Exception as e:
            self.root.after(0, lambda: self.log_message(f"✗ 错误: {str(e)}"))
            self.root.after(0, lambda: messagebox.showerror("错误",
                                                            f"转换过程中发生错误:\n{str(e)}"))

        finally:
            self.converting = False
            self.root.after(0, lambda: self.convert_btn.config(text="⚡ 极速转换",
                                                               state='normal',
                                                               bg='#27ae60'))


def main():
    """主函数"""
    root = Tk()
    app = ModernMusicConverterGUI(root)
    root.mainloop()


if __name__ == '__main__':
    main()