import os
import shutil
import json
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from tkinter import font as tkfont
import threading


class FileOrganizerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("智能文件归类工具")
        self.root.geometry("900x700")
        self.root.resizable(True, True)

        # 设置主题颜色
        self.colors = {
            'bg': '#f5f6fa',
            'primary': '#4834d4',
            'secondary': '#686de0',
            'success': '#26de81',
            'danger': '#fc5c65',
            'text': '#2f3640',
            'white': '#ffffff',
            'border': '#dfe4ea'
        }

        self.root.configure(bg=self.colors['bg'])

        # 默认文件类型分类
        self.default_file_types = {
            'Compressed': ['zip', 'rar', 'r0*', 'r1*', 'arj', 'gz', 'sit', 'sitx', 'sea', 'ace', 'bz2', '7z'],
            'Documents': ['doc', 'pdf', 'ppt', 'pps', 'docx', 'pptx', 'xlsx', 'xls', 'txt', 'rtf', 'md', 'csv'],
            'Music': ['mp3', 'wav', 'wma', 'mpa', 'ram', 'ra', 'aac', 'aif', 'm4a', 'tsa', 'flac'],
            'Application': ['exe', 'msi', 'apk'],
            'Video': ['avi', 'mpg', 'mpe', 'mpeg', 'asf', 'wmv', 'mov', 'qt', 'rm', 'mp4', 'flv', 'm4v', 'webm', 'ogv',
                      'ogg', 'mkv', 'ts', 'tsv'],
            'Torrent': ['torrent', 'magnet'],
            'EBook': ['epub', 'mobi', 'azw3', 'azw', 'fb2', 'ibook', 'lit', 'prc'],
            'Picture': ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'tiff', 'tif', 'svg', 'psd', 'webp'],
            'GeoFile': ['shp', 'geojson', 'kml', 'kmz', 'gpx', 'tif', 'tiff', 'dem', 'asc', 'dbf']
        }

        # 加载或使用默认配置
        self.file_types = self.load_config()

        # 创建界面
        self.create_widgets()

    def load_config(self):
        """加载保存的配置"""
        try:
            if os.path.exists('file_organizer_config.json'):
                with open('file_organizer_config.json', 'r', encoding='utf-8') as f:
                    return json.load(f)
        except:
            pass
        return self.default_file_types.copy()

    def save_config(self):
        """保存配置到文件"""
        try:
            with open('file_organizer_config.json', 'w', encoding='utf-8') as f:
                json.dump(self.file_types, f, indent=4, ensure_ascii=False)
            messagebox.showinfo("成功", "配置已保存!")
        except Exception as e:
            messagebox.showerror("错误", f"保存配置失败: {str(e)}")

    def create_widgets(self):
        """创建所有界面组件"""
        # 标题框架
        title_frame = tk.Frame(self.root, bg=self.colors['primary'], height=80)
        title_frame.pack(fill='x', pady=(0, 20))
        title_frame.pack_propagate(False)

        title_label = tk.Label(
            title_frame,
            text="📁 智能文件归类工具",
            font=('微软雅黑', 24, 'bold'),
            bg=self.colors['primary'],
            fg=self.colors['white']
        )
        title_label.pack(expand=True)

        # 主容器
        main_container = tk.Frame(self.root, bg=self.colors['bg'])
        main_container.pack(fill='both', expand=True, padx=20, pady=0)

        # 路径选择区域
        self.create_path_section(main_container)

        # 分类设置区域
        self.create_category_section(main_container)

        # 操作按钮区域
        self.create_action_buttons(main_container)

        # 日志区域
        self.create_log_section(main_container)

    def create_path_section(self, parent):
        """创建路径选择区域"""
        path_frame = tk.LabelFrame(
            parent,
            text="📂 选择文件夹",
            font=('微软雅黑', 12, 'bold'),
            bg=self.colors['white'],
            fg=self.colors['text'],
            relief='flat',
            borderwidth=2
        )
        path_frame.pack(fill='x', pady=(0, 15))

        inner_frame = tk.Frame(path_frame, bg=self.colors['white'])
        inner_frame.pack(fill='x', padx=15, pady=15)

        self.path_var = tk.StringVar(value=r"C:\Users\25830\Downloads")

        path_entry = tk.Entry(
            inner_frame,
            textvariable=self.path_var,
            font=('微软雅黑', 11),
            relief='flat',
            bg='#f8f9fa',
            fg=self.colors['text'],
            insertbackground=self.colors['primary']
        )
        path_entry.pack(side='left', fill='x', expand=True, ipady=8, padx=(0, 10))

        browse_btn = tk.Button(
            inner_frame,
            text="浏览",
            command=self.browse_folder,
            font=('微软雅黑', 10, 'bold'),
            bg=self.colors['secondary'],
            fg=self.colors['white'],
            relief='flat',
            cursor='hand2',
            padx=20,
            pady=8
        )
        browse_btn.pack(side='right')

        # 鼠标悬停效果
        browse_btn.bind('<Enter>', lambda e: browse_btn.config(bg=self.colors['primary']))
        browse_btn.bind('<Leave>', lambda e: browse_btn.config(bg=self.colors['secondary']))

    def create_category_section(self, parent):
        """创建分类设置区域"""
        category_frame = tk.LabelFrame(
            parent,
            text="🏷️ 文件分类设置",
            font=('微软雅黑', 12, 'bold'),
            bg=self.colors['white'],
            fg=self.colors['text'],
            relief='flat',
            borderwidth=2
        )
        category_frame.pack(fill='both', expand=True, pady=(0, 15))

        # 工具栏
        toolbar = tk.Frame(category_frame, bg=self.colors['white'])
        toolbar.pack(fill='x', padx=15, pady=(15, 10))

        add_btn = tk.Button(
            toolbar,
            text="➕ 添加分类",
            command=self.add_category,
            font=('微软雅黑', 9, 'bold'),
            bg=self.colors['success'],
            fg=self.colors['white'],
            relief='flat',
            cursor='hand2',
            padx=15,
            pady=5
        )
        add_btn.pack(side='left', padx=(0, 10))

        edit_btn = tk.Button(
            toolbar,
            text="✏️ 编辑选中",
            command=self.edit_category,
            font=('微软雅黑', 9, 'bold'),
            bg=self.colors['secondary'],
            fg=self.colors['white'],
            relief='flat',
            cursor='hand2',
            padx=15,
            pady=5
        )
        edit_btn.pack(side='left', padx=(0, 10))

        delete_btn = tk.Button(
            toolbar,
            text="🗑️ 删除选中",
            command=self.delete_category,
            font=('微软雅黑', 9, 'bold'),
            bg=self.colors['danger'],
            fg=self.colors['white'],
            relief='flat',
            cursor='hand2',
            padx=15,
            pady=5
        )
        delete_btn.pack(side='left', padx=(0, 10))

        reset_btn = tk.Button(
            toolbar,
            text="🔄 恢复默认",
            command=self.reset_categories,
            font=('微软雅黑', 9, 'bold'),
            bg='#95a5a6',
            fg=self.colors['white'],
            relief='flat',
            cursor='hand2',
            padx=15,
            pady=5
        )
        reset_btn.pack(side='left')

        # 列表框架
        list_frame = tk.Frame(category_frame, bg=self.colors['white'])
        list_frame.pack(fill='both', expand=True, padx=15, pady=(0, 15))

        # Treeview样式
        style = ttk.Style()
        style.theme_use('clam')
        style.configure(
            'Custom.Treeview',
            background='#f8f9fa',
            foreground=self.colors['text'],
            fieldbackground='#f8f9fa',
            borderwidth=0,
            font=('微软雅黑', 10)
        )
        style.configure('Custom.Treeview.Heading', font=('微软雅黑', 10, 'bold'))
        style.map('Custom.Treeview', background=[('selected', self.colors['secondary'])])

        # 滚动条
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side='right', fill='y')

        # Treeview
        self.category_tree = ttk.Treeview(
            list_frame,
            columns=('category', 'extensions'),
            show='headings',
            yscrollcommand=scrollbar.set,
            style='Custom.Treeview',
            height=8
        )

        self.category_tree.heading('category', text='分类名称')
        self.category_tree.heading('extensions', text='文件扩展名')
        self.category_tree.column('category', width=150, anchor='w')
        self.category_tree.column('extensions', width=500, anchor='w')

        self.category_tree.pack(side='left', fill='both', expand=True)
        scrollbar.config(command=self.category_tree.yview)

        # 加载分类数据
        self.refresh_category_list()

    def create_action_buttons(self, parent):
        """创建操作按钮区域"""
        button_frame = tk.Frame(parent, bg=self.colors['bg'])
        button_frame.pack(fill='x', pady=(0, 15))

        start_btn = tk.Button(
            button_frame,
            text="▶️ 开始整理",
            command=self.start_organizing,
            font=('微软雅黑', 12, 'bold'),
            bg=self.colors['success'],
            fg=self.colors['white'],
            relief='flat',
            cursor='hand2',
            padx=30,
            pady=12
        )
        start_btn.pack(side='left', expand=True, fill='x', padx=(0, 10))

        save_btn = tk.Button(
            button_frame,
            text="💾 保存配置",
            command=self.save_config,
            font=('微软雅黑', 12, 'bold'),
            bg=self.colors['secondary'],
            fg=self.colors['white'],
            relief='flat',
            cursor='hand2',
            padx=30,
            pady=12
        )
        save_btn.pack(side='left', expand=True, fill='x')

        # 鼠标悬停效果
        start_btn.bind('<Enter>', lambda e: start_btn.config(bg='#20bf6b'))
        start_btn.bind('<Leave>', lambda e: start_btn.config(bg=self.colors['success']))
        save_btn.bind('<Enter>', lambda e: save_btn.config(bg=self.colors['primary']))
        save_btn.bind('<Leave>', lambda e: save_btn.config(bg=self.colors['secondary']))

    def create_log_section(self, parent):
        """创建日志区域"""
        log_frame = tk.LabelFrame(
            parent,
            text="📋 操作日志",
            font=('微软雅黑', 12, 'bold'),
            bg=self.colors['white'],
            fg=self.colors['text'],
            relief='flat',
            borderwidth=2
        )
        log_frame.pack(fill='both', expand=True)

        self.log_text = scrolledtext.ScrolledText(
            log_frame,
            font=('Consolas', 9),
            bg='#2d3436',
            fg='#00ff00',
            relief='flat',
            wrap='word',
            height=8
        )
        self.log_text.pack(fill='both', expand=True, padx=15, pady=15)

    def browse_folder(self):
        """浏览文件夹"""
        folder = filedialog.askdirectory()
        if folder:
            self.path_var.set(folder)
            self.log(f"已选择文件夹: {folder}")

    def refresh_category_list(self):
        """刷新分类列表"""
        # 清空现有项
        for item in self.category_tree.get_children():
            self.category_tree.delete(item)

        # 添加所有分类
        for category, extensions in self.file_types.items():
            ext_str = ', '.join(extensions)
            self.category_tree.insert('', 'end', values=(category, ext_str))

    def add_category(self):
        """添加新分类"""
        dialog = tk.Toplevel(self.root)
        dialog.title("添加分类")
        dialog.geometry("400x200")
        dialog.configure(bg=self.colors['white'])
        dialog.transient(self.root)
        dialog.grab_set()

        # 居中显示
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")

        tk.Label(dialog, text="分类名称:", font=('微软雅黑', 10), bg=self.colors['white']).pack(pady=(20, 5))
        name_entry = tk.Entry(dialog, font=('微软雅黑', 10), width=30)
        name_entry.pack(pady=5)

        tk.Label(dialog, text="扩展名 (用逗号分隔):", font=('微软雅黑', 10), bg=self.colors['white']).pack(pady=(10, 5))
        ext_entry = tk.Entry(dialog, font=('微软雅黑', 10), width=30)
        ext_entry.pack(pady=5)

        def save_category():
            name = name_entry.get().strip()
            extensions = [ext.strip() for ext in ext_entry.get().split(',') if ext.strip()]

            if not name or not extensions:
                messagebox.showwarning("警告", "请填写完整信息!")
                return

            self.file_types[name] = extensions
            self.refresh_category_list()
            self.log(f"已添加分类: {name}")
            dialog.destroy()

        tk.Button(
            dialog,
            text="确定",
            command=save_category,
            font=('微软雅黑', 10, 'bold'),
            bg=self.colors['success'],
            fg=self.colors['white'],
            relief='flat',
            cursor='hand2',
            padx=20,
            pady=5
        ).pack(pady=20)

    def edit_category(self):
        """编辑选中的分类"""
        selected = self.category_tree.selection()
        if not selected:
            messagebox.showwarning("警告", "请先选择要编辑的分类!")
            return

        item = self.category_tree.item(selected[0])
        old_name = item['values'][0]
        old_extensions = self.file_types[old_name]

        dialog = tk.Toplevel(self.root)
        dialog.title("编辑分类")
        dialog.geometry("400x200")
        dialog.configure(bg=self.colors['white'])
        dialog.transient(self.root)
        dialog.grab_set()

        # 居中显示
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")

        tk.Label(dialog, text="分类名称:", font=('微软雅黑', 10), bg=self.colors['white']).pack(pady=(20, 5))
        name_entry = tk.Entry(dialog, font=('微软雅黑', 10), width=30)
        name_entry.insert(0, old_name)
        name_entry.pack(pady=5)

        tk.Label(dialog, text="扩展名 (用逗号分隔):", font=('微软雅黑', 10), bg=self.colors['white']).pack(pady=(10, 5))
        ext_entry = tk.Entry(dialog, font=('微软雅黑', 10), width=30)
        ext_entry.insert(0, ', '.join(old_extensions))
        ext_entry.pack(pady=5)

        def save_changes():
            new_name = name_entry.get().strip()
            extensions = [ext.strip() for ext in ext_entry.get().split(',') if ext.strip()]

            if not new_name or not extensions:
                messagebox.showwarning("警告", "请填写完整信息!")
                return

            # 删除旧分类
            if old_name in self.file_types:
                del self.file_types[old_name]

            # 添加新分类
            self.file_types[new_name] = extensions
            self.refresh_category_list()
            self.log(f"已更新分类: {new_name}")
            dialog.destroy()

        tk.Button(
            dialog,
            text="保存",
            command=save_changes,
            font=('微软雅黑', 10, 'bold'),
            bg=self.colors['secondary'],
            fg=self.colors['white'],
            relief='flat',
            cursor='hand2',
            padx=20,
            pady=5
        ).pack(pady=20)

    def delete_category(self):
        """删除选中的分类"""
        selected = self.category_tree.selection()
        if not selected:
            messagebox.showwarning("警告", "请先选择要删除的分类!")
            return

        item = self.category_tree.item(selected[0])
        category = item['values'][0]

        if messagebox.askyesno("确认", f"确定要删除分类 '{category}' 吗?"):
            del self.file_types[category]
            self.refresh_category_list()
            self.log(f"已删除分类: {category}")

    def reset_categories(self):
        """恢复默认分类"""
        if messagebox.askyesno("确认", "确定要恢复默认分类设置吗?\n这将清除所有自定义分类!"):
            self.file_types = self.default_file_types.copy()
            self.refresh_category_list()
            self.log("已恢复默认分类设置")

    def log(self, message):
        """添加日志信息"""
        self.log_text.insert('end', f"{message}\n")
        self.log_text.see('end')
        self.root.update()

    def organize_files(self, source_folder):
        """整理文件"""
        if not os.path.exists(source_folder):
            self.log(f"❌ 错误: 文件夹不存在: {source_folder}")
            messagebox.showerror("错误", "指定的文件夹不存在!")
            return

        self.log(f"开始整理文件夹: {source_folder}")
        moved_count = 0

        for category, extensions in self.file_types.items():
            # 创建目标文件夹
            target_folder = os.path.join(source_folder, category)
            os.makedirs(target_folder, exist_ok=True)

            # 移动文件
            for ext in extensions:
                try:
                    # 处理通配符 *
                    if '*' in ext:
                        files = [f for f in os.listdir(source_folder)
                                 if f.startswith(ext.replace('*', '')) and
                                 os.path.isfile(os.path.join(source_folder, f))]
                    else:
                        files = [f for f in os.listdir(source_folder)
                                 if f.endswith(f'.{ext}') and
                                 os.path.isfile(os.path.join(source_folder, f))]

                    for file in files:
                        source_file = os.path.join(source_folder, file)
                        target_file = os.path.join(target_folder, file)

                        # 避免移动到自己
                        if os.path.dirname(source_file) == target_folder:
                            continue

                        # 如果目标文件已存在,添加序号
                        if os.path.exists(target_file):
                            base, extension = os.path.splitext(file)
                            counter = 1
                            while os.path.exists(target_file):
                                target_file = os.path.join(target_folder, f"{base}_{counter}{extension}")
                                counter += 1

                        try:
                            shutil.move(source_file, target_file)
                            self.log(f"✅ 已移动: {file} -> {category}")
                            moved_count += 1
                        except Exception as e:
                            self.log(f"❌ 移动失败: {file} - {str(e)}")

                except Exception as e:
                    self.log(f"❌ 处理扩展名 {ext} 时出错: {str(e)}")

        self.log(f"整理完成! 共移动 {moved_count} 个文件")
        messagebox.showinfo("完成", f"文件整理完成!\n共移动 {moved_count} 个文件")

    def start_organizing(self):
        """开始整理文件(在新线程中执行)"""
        source_folder = self.path_var.get().strip()

        if not source_folder:
            messagebox.showwarning("警告", "请先选择文件夹!")
            return

        # 清空日志
        self.log_text.delete(1.0, 'end')

        # 在新线程中执行整理操作
        thread = threading.Thread(target=self.organize_files, args=(source_folder,), daemon=True)
        thread.start()


def main():
    """主函数"""
    root = tk.Tk()
    app = FileOrganizerGUI(root)

    # 设置窗口图标(如果有的话)
    try:
        root.iconbitmap('icon.ico')
    except:
        pass

    # 居中显示窗口
    root.update_idletasks()
    x = (root.winfo_screenwidth() // 2) - (root.winfo_width() // 2)
    y = (root.winfo_screenheight() // 2) - (root.winfo_height() // 2)
    root.geometry(f"+{x}+{y}")

    root.mainloop()


if __name__ == "__main__":
    main()