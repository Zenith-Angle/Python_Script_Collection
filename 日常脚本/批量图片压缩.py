import os
import threading
import multiprocessing
from multiprocessing import Manager
import queue
import time
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
from PIL import Image
from io import BytesIO
import logging
import datetime  # 用于格式化剩余时间

# 配置日志记录
logging.basicConfig(
    filename='compression_errors.log',
    level=logging.ERROR,
    format='%(asctime)s:%(levelname)s:%(message)s'
)


def compress_image(input_image_path, output_image_path, max_size=None):
    """
    根据指定的方法压缩图像，同时尽可能减少对图像内容的损失。
    只处理JPG/JPEG和PNG格式，其他格式则直接复制。
    """
    try:
        with Image.open(input_image_path) as img:
            img.verify()  # 检查图像是否是有效的
        with Image.open(input_image_path) as img:
            ext = os.path.splitext(input_image_path)[1].lower()
            format = img.format

            # 只处理JPG/JPEG和PNG格式，其他格式直接复制
            if format not in ['JPEG', 'PNG']:
                img.save(output_image_path, format=format, optimize=True)
                return

            # 如果存在Alpha通道，转换为RGB模式
            if img.mode in ('RGBA', 'LA', 'P'):
                img = img.convert('RGB')

            # 根据最大文件大小调整质量
            if max_size is not None:
                quality = 95
                min_quality = 10

                while quality >= min_quality:
                    img_bytes = BytesIO()
                    try:
                        img.save(img_bytes, format=format, quality=quality, optimize=True)
                    except Exception as e:
                        logging.error(f"保存图像到内存时出错：{e}")
                        return
                    size = img_bytes.tell()

                    if size <= max_size or quality == min_quality:
                        with open(output_image_path, 'wb') as f:
                            f.write(img_bytes.getvalue())
                        break
                    quality -= 5
            else:
                # 直接保存图像
                img.save(output_image_path, format=format, optimize=True)
    except Exception as e:
        logging.error(f"处理图像 {input_image_path} 时出错：{e}")


def compress_task(args):
    """
    压缩单张图像。此函数不直接更新进度队列，而是返回结果。
    """
    image_file, input_dir, input_basename, output_dir, max_size_user_defined, scaling_factor = args
    try:
        rel_path = os.path.relpath(os.path.dirname(image_file), input_dir)
        # 在输出目录中加入输入目录的名称作为最外层结构
        output_root = os.path.join(output_dir, input_basename, rel_path)
        if not os.path.exists(output_root):
            os.makedirs(output_root)
        output_file_path = os.path.join(output_root, os.path.basename(image_file))

        if scaling_factor is not None:
            # 'scale' option: set max_size proportionally
            original_size = os.path.getsize(image_file)
            max_size = scaling_factor * original_size
        else:
            # 'size' option: user-defined max_size
            max_size = max_size_user_defined

        compress_image(image_file, output_file_path, max_size)
        return 1  # 表示成功压缩一张图片
    except Exception as e:
        logging.error(f"压缩图片 {image_file} 时出错：{e}")
        return 0  # 表示压缩失败


def compression_process(image_files, input_dir, input_basename, output_dir,
                        max_size_user_defined, scaling_factor, progress_queue,
                        pause_event, stop_event):
    """
    压缩进程的主函数，使用多进程池并行压缩图片。
    """
    num_workers = multiprocessing.cpu_count()  # 自动检测核心数
    args_list = [
        (image_file, input_dir, input_basename, output_dir, max_size_user_defined,
         scaling_factor)
        for image_file in image_files
    ]

    with multiprocessing.Pool(processes=num_workers) as pool:
        for result in pool.imap_unordered(compress_task, args_list):
            if stop_event.is_set():
                pool.terminate()
                break
            while pause_event.is_set():
                if stop_event.is_set():
                    pool.terminate()
                    break
                else:
                    time.sleep(0.1)
            progress_queue.put(result)
        progress_queue.put('done')


def start_compression_thread():
    """
    在新线程中启动压缩过程。
    """
    threading.Thread(target=start_compression, daemon=True).start()


def start_compression():
    global compression_process_info, start_time, processed_count
    input_dir = input_dir_var.get()
    output_dir = output_dir_var.get()
    compression_option = compression_option_var.get()

    if not input_dir or not output_dir:
        messagebox.showwarning("警告", "请指定输入和输出文件夹！")
        return

    if compression_option == 'size':
        # 处理最大文件大小
        try:
            max_size_mb = float(max_size_var.get())
            max_size = max_size_mb * 1024 * 1024  # 转换为字节
            scaling_factor = None
        except ValueError:
            messagebox.showerror("错误", "请输入有效的最大文件大小！")
            return
    elif compression_option == 'scale':
        # 处理比例压缩，设置max_size为比例乘以原始文件大小
        scaling_factor_str = scaling_factor_var.get()
        scaling_factor_dict = {
            "1/2": 0.5,
            "1/3": 1 / 3,
            "1/4": 0.25,
            "1/5": 0.2,
            "1/10": 0.1,
        }
        scaling_factor = scaling_factor_dict.get(scaling_factor_str)
        if scaling_factor is None:
            messagebox.showerror("错误", "请选择有效的比例！")
            return
        max_size = None
    else:
        messagebox.showerror("错误", "请选择压缩方式！")
        return

    # 获取输入目录的名称，用于在输出目录中创建最外层结构
    input_basename = os.path.basename(os.path.normpath(input_dir))

    # 获取所有待处理的图片文件（只处理JPG/JPEG和PNG）
    image_files = []
    supported_extensions = ['.jpg', '.jpeg', '.png']
    for dirpath, dirs, files in os.walk(input_dir):
        for file in files:
            ext = os.path.splitext(file)[1].lower()
            if ext in supported_extensions:
                image_files.append(os.path.join(dirpath, file))

    total_files = len(image_files)
    if total_files == 0:
        messagebox.showinfo("提示", "输入文件夹中没有找到支持的图片格式（JPG/JPEG/PNG）！")
        return

    # 初始化进度条和状态标签
    root.after(0, lambda: progress_bar.config(maximum=total_files, value=0))
    root.after(0, lambda: progress_label_var.set("正在压缩..."))
    root.after(0, lambda: remaining_time_var.set("剩余时间：计算中..."))

    # 禁用开始按钮，启用暂停按钮
    root.after(0, lambda: start_button.config(state='disabled'))
    root.after(0, lambda: pause_button.config(state='normal'))
    root.after(0, lambda: continue_button.config(state='disabled'))
    root.after(0, lambda: end_button.config(state='disabled'))

    # 创建进度队列和控制事件
    manager = Manager()
    progress_queue = manager.Queue()
    pause_event = manager.Event()
    stop_event = manager.Event()

    # 创建并启动压缩进程
    p = multiprocessing.Process(target=compression_process, args=(
        image_files, input_dir, input_basename, output_dir,
        max_size if compression_option == 'size' else None,
        scaling_factor if compression_option == 'scale' else None, progress_queue,
        pause_event, stop_event
    ))
    p.start()

    # 初始化开始时间和已处理计数
    start_time = time.time()
    processed_count = 0

    # 定义进度更新函数
    def update_progress():
        global processed_count
        try:
            while True:
                progress = progress_queue.get_nowait()
                if progress == 'done':
                    progress_label_var.set("压缩完成！")
                    progress_bar['value'] = total_files
                    remaining_time_var.set("剩余时间：00:00:00")
                    messagebox.showinfo("完成", "图片压缩已完成！")
                    # 重置按钮状态
                    start_button.config(state='normal')
                    pause_button.config(state='disabled')
                    continue_button.config(state='disabled')
                    end_button.config(state='disabled')
                    return
                else:
                    progress_bar['value'] += progress
                    processed_count += progress
                    current = progress_bar['value']

                    # 计算经过的时间
                    elapsed_time = time.time() - start_time
                    if processed_count > 0:
                        # 计算处理速率（图片/秒）
                        rate = processed_count / elapsed_time
                        # 计算剩余图片数
                        remaining = total_files - processed_count
                        # 预测剩余时间（秒）
                        remaining_time = remaining / rate if rate > 0 else 0
                    else:
                        remaining_time = 0

                    # 格式化剩余时间为 hh:mm:ss
                    remaining_time_str = str(
                        datetime.timedelta(seconds=int(remaining_time)))

                    progress_label_var.set(f"正在压缩：{current}/{total_files}")
                    remaining_time_var.set(f"剩余时间：{remaining_time_str}")
        except queue.Empty:
            pass
        if p.is_alive():
            root.after(100, update_progress)
        else:
            # 如果进程已经结束但没有发送'done'
            progress_label_var.set("压缩完成！")
            progress_bar['value'] = total_files
            remaining_time_var.set("剩余时间：00:00:00")
            messagebox.showinfo("完成", "图片压缩已完成！")
            # 重置按钮状态
            start_button.config(state='normal')
            pause_button.config(state='disabled')
            continue_button.config(state='disabled')
            end_button.config(state='disabled')

    # 启动进度更新
    root.after(100, update_progress)

    # 将进程和控制事件存储在全局变量中，以便暂停和结束
    compression_process_info = {
        'process': p,
        'pause_event': pause_event,
        'stop_event': stop_event
    }


def pause_compression():
    """
    暂停压缩任务的函数。
    """
    if compression_process_info:
        compression_process_info['pause_event'].set()
        progress_label_var.set("已暂停")
        remaining_time_var.set("剩余时间：已暂停")
        # 更改按钮状态
        pause_button.config(state='disabled')
        continue_button.config(state='normal')
        end_button.config(state='normal')


def continue_compression():
    """
    继续压缩任务的函数。
    """
    if compression_process_info:
        compression_process_info['pause_event'].clear()
        progress_label_var.set("正在压缩...")
        remaining_time_var.set("剩余时间：计算中...")
        # 更改按钮状态
        pause_button.config(state='normal')
        continue_button.config(state='disabled')
        end_button.config(state='normal')


def end_compression():
    """
    结束压缩任务的函数。
    """
    if compression_process_info:
        compression_process_info['stop_event'].set()
        compression_process_info['process'].terminate()
        compression_process_info['process'].join()
        progress_label_var.set("已结束")
        remaining_time_var.set("剩余时间：已结束")
        progress_bar['value'] = 0
        # 重置按钮状态
        start_button.config(state='normal')
        pause_button.config(state='disabled')
        continue_button.config(state='disabled')
        end_button.config(state='disabled')


def select_input_dir():
    """
    选择输入文件夹的函数。
    """
    dir_path = filedialog.askdirectory()
    if dir_path:
        input_dir_var.set(dir_path)


def select_output_dir():
    """
    选择输出文件夹的函数。
    """
    dir_path = filedialog.askdirectory()
    if dir_path:
        output_dir_var.set(dir_path)


def update_compression_option():
    """
    根据压缩选项启用或禁用输入控件。
    """
    option = compression_option_var.get()
    if option == 'size':
        max_size_entry.config(state='normal')
        scaling_factor_combo.config(state='disabled')
    elif option == 'scale':
        max_size_entry.config(state='disabled')
        scaling_factor_combo.config(state='readonly')


def main():
    global root, input_dir_var, output_dir_var, compression_option_var
    global max_size_var, scaling_factor_var
    global max_size_entry, scaling_factor_combo
    global progress_label_var, progress_label
    global progress_bar, remaining_time_var, remaining_time_label
    global start_button, pause_button, continue_button, end_button
    global compression_process_info
    global start_time, processed_count

    # 初始化全局变量
    compression_process_info = None
    start_time = None
    processed_count = 0

    # 创建主窗口
    root = tk.Tk()
    root.title("图片压缩工具")
    root.geometry("600x550")  # 调整窗口大小以适应所有控件
    root.resizable(False, False)

    # 应用 ttk 样式
    style = ttk.Style()
    try:
        style.theme_use('vista')  # 尝试使用 'vista' 主题，其他可选 'clam', 'default' 等
    except:
        pass  # 如果主题不可用，使用默认主题

    # 主框架，添加边距
    main_frame = ttk.Frame(root, padding="10 10 10 10")  # 减少边距
    main_frame.pack(fill='both', expand=True)

    # 标题标签
    title_label = ttk.Label(main_frame, text="图片压缩工具",
                            font=("Helvetica", 16, "bold"))
    title_label.pack(pady=(0, 10))  # 顶部间距减小

    # 分隔线
    separator = ttk.Separator(main_frame, orient='horizontal')
    separator.pack(fill='x', pady=5)

    # 中心内容框架
    content_frame = ttk.Frame(main_frame)
    content_frame.pack(expand=True, fill='both')

    # 输入文件夹选择
    input_dir_var = tk.StringVar()
    input_frame = ttk.Frame(content_frame)
    input_frame.pack(fill='x', pady=5)

    ttk.Label(input_frame, text="输入文件夹：").pack(side='left', padx=(0, 5))
    input_entry = ttk.Entry(input_frame, textvariable=input_dir_var, width=40)
    input_entry.pack(side='left', fill='x', expand=True, padx=(0, 5))
    ttk.Button(input_frame, text="选择", command=select_input_dir).pack(side='left')

    # 输出文件夹选择
    output_dir_var = tk.StringVar()
    output_frame = ttk.Frame(content_frame)
    output_frame.pack(fill='x', pady=5)

    ttk.Label(output_frame, text="输出文件夹：").pack(side='left', padx=(0, 5))
    output_entry = ttk.Entry(output_frame, textvariable=output_dir_var, width=40)
    output_entry.pack(side='left', fill='x', expand=True, padx=(0, 5))
    ttk.Button(output_frame, text="选择", command=select_output_dir).pack(side='left')

    # 分隔线
    separator2 = ttk.Separator(content_frame, orient='horizontal')
    separator2.pack(fill='x', pady=10)

    # 压缩选项
    compression_option_var = tk.StringVar(value='size')
    option_frame = ttk.Frame(content_frame)
    option_frame.pack(fill='x', pady=5)

    ttk.Label(option_frame, text="压缩方式：").pack(side='left', padx=(0, 10))
    size_radiobutton = ttk.Radiobutton(option_frame, text='按最大文件大小压缩',
                                       variable=compression_option_var,
                                       value='size', command=update_compression_option)
    size_radiobutton.pack(side='left', padx=5)
    scale_radiobutton = ttk.Radiobutton(option_frame, text='按比例压缩',
                                        variable=compression_option_var,
                                        value='scale', command=update_compression_option)
    scale_radiobutton.pack(side='left', padx=5)

    # 参数设置框架
    param_frame = ttk.Frame(content_frame)
    param_frame.pack(fill='x', pady=5)

    # 最大文件大小输入
    max_size_var = tk.StringVar(value="1")  # 默认1MB
    max_size_label = ttk.Label(param_frame, text="最大文件大小（MB）：")
    max_size_label.grid(row=0, column=0, padx=5, pady=5, sticky='e')
    max_size_entry = ttk.Entry(param_frame, textvariable=max_size_var, width=20)
    max_size_entry.grid(row=0, column=1, padx=5, pady=5, sticky='w')

    # 缩放比例下拉框
    scaling_factor_var = tk.StringVar(value="1/2")
    scaling_factor_label = ttk.Label(param_frame, text="比例：")
    scaling_factor_label.grid(row=1, column=0, padx=5, pady=5, sticky='e')
    scaling_options = ["1/2", "1/3", "1/4", "1/5", "1/10"]
    scaling_factor_combo = ttk.Combobox(param_frame, textvariable=scaling_factor_var,
                                        values=scaling_options,
                                        width=17, state='disabled')
    scaling_factor_combo.grid(row=1, column=1, padx=5, pady=5, sticky='w')

    # 分隔线
    separator3 = ttk.Separator(content_frame, orient='horizontal')
    separator3.pack(fill='x', pady=10)

    # 进度条和状态标签
    progress_frame = ttk.Frame(content_frame)
    progress_frame.pack(fill='x', pady=5)

    progress_label_var = tk.StringVar(value="等待开始...")
    progress_label = ttk.Label(progress_frame, textvariable=progress_label_var)
    progress_label.pack(anchor='w')

    progress_bar = ttk.Progressbar(progress_frame, orient='horizontal', length=500,
                                   mode='determinate')
    progress_bar.pack(fill='x', pady=5)

    remaining_time_var = tk.StringVar(value="剩余时间：N/A")
    remaining_time_label = ttk.Label(progress_frame, textvariable=remaining_time_var)
    remaining_time_label.pack(anchor='w')

    # 分隔线
    separator4 = ttk.Separator(content_frame, orient='horizontal')
    separator4.pack(fill='x', pady=10)

    # 按钮区域
    button_frame = ttk.Frame(content_frame)
    button_frame.pack(pady=10)

    # 开始按钮
    start_button = ttk.Button(button_frame, text="开始压缩",
                              command=start_compression_thread)
    start_button.grid(row=0, column=0, padx=5, pady=5)

    # 暂停、继续和结束按钮
    pause_button = ttk.Button(button_frame, text="暂停", command=pause_compression,
                              state='disabled')
    continue_button = ttk.Button(button_frame, text="继续", command=continue_compression,
                                 state='disabled')
    end_button = ttk.Button(button_frame, text="结束", command=end_compression,
                            state='disabled')

    pause_button.grid(row=0, column=1, padx=5, pady=5)
    continue_button.grid(row=0, column=2, padx=5, pady=5)
    end_button.grid(row=0, column=3, padx=5, pady=5)

    # 调整所有控件的边距
    for child in param_frame.winfo_children():
        child.grid_configure(padx=5, pady=5)

    def on_closing():
        """
        处理窗口关闭事件，确保所有子进程被终止。
        """
        if compression_process_info and compression_process_info['process'].is_alive():
            if messagebox.askokcancel("退出", "压缩任务正在进行，确定要退出吗？"):
                compression_process_info['stop_event'].set()
                compression_process_info['process'].terminate()
                compression_process_info['process'].join()
                root.destroy()
        else:
            root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_closing)

    root.mainloop()


def pause_compression():
    """
    暂停压缩任务的函数。
    """
    if compression_process_info:
        compression_process_info['pause_event'].set()
        progress_label_var.set("已暂停")
        remaining_time_var.set("剩余时间：已暂停")
        # 更改按钮状态
        pause_button.config(state='disabled')
        continue_button.config(state='normal')
        end_button.config(state='normal')


def continue_compression():
    """
    继续压缩任务的函数。
    """
    if compression_process_info:
        compression_process_info['pause_event'].clear()
        progress_label_var.set("正在压缩...")
        remaining_time_var.set("剩余时间：计算中...")
        # 更改按钮状态
        pause_button.config(state='normal')
        continue_button.config(state='disabled')
        end_button.config(state='normal')


def end_compression():
    """
    结束压缩任务的函数。
    """
    if compression_process_info:
        compression_process_info['stop_event'].set()
        compression_process_info['process'].terminate()
        compression_process_info['process'].join()
        progress_label_var.set("已结束")
        remaining_time_var.set("剩余时间：已结束")
        progress_bar['value'] = 0
        # 重置按钮状态
        start_button.config(state='normal')
        pause_button.config(state='disabled')
        continue_button.config(state='disabled')
        end_button.config(state='disabled')


def select_input_dir():
    """
    选择输入文件夹的函数。
    """
    dir_path = filedialog.askdirectory()
    if dir_path:
        input_dir_var.set(dir_path)


def select_output_dir():
    """
    选择输出文件夹的函数。
    """
    dir_path = filedialog.askdirectory()
    if dir_path:
        output_dir_var.set(dir_path)


def update_compression_option():
    """
    根据压缩选项启用或禁用输入控件。
    """
    option = compression_option_var.get()
    if option == 'size':
        max_size_entry.config(state='normal')
        scaling_factor_combo.config(state='disabled')
    elif option == 'scale':
        max_size_entry.config(state='disabled')
        scaling_factor_combo.config(state='readonly')


if __name__ == '__main__':
    multiprocessing.freeze_support()  # 防止在Windows上打包时出现问题
    main()
