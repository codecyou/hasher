import tkinter as tk
from tkinter import ttk
from tkinter.filedialog import askopenfilename, asksaveasfilename
import windnd
from tkinter import scrolledtext
from tkinter import messagebox as mBox
import hash_core
import threading


class CalHashFrame(tk.Frame):  # 继承Frame类
    """计算文件hash值"""
    def __init__(self, master=None):
        tk.Frame.__init__(self, master)
        self.root = master  # 定义内部变量root
        self.winWidth = 650  # 窗口宽度
        self.winHeight = 500  # 窗口高度
        # 设置窗口大小
        self.set_window()

        self.upper = tk.BooleanVar()  # True 大写 False 小写
        self.vars = []  # 复选框变量
        self.result = {}  # 计算结果
        self.algors = ['sha1', 'sha256', 'md5',	"sha224", "sha512", "sha384"]  # 算法
        self.search_str = tk.StringVar()  # 搜索字符串
        # 校对字符串
        self.str1 = tk.StringVar()
        self.str2 = tk.StringVar()
        self.ignore_case_flag = tk.BooleanVar()  # True 忽略大小写 False 严格大小写
        self.ignore_space_flag = tk.BooleanVar()  # True 忽略空格 False 严格空格
        self.only_char_flag = tk.BooleanVar()  # True 只匹配字符内容，忽略所有空格换行，包括字符串中的 False 严格空格
        for i in range(len(self.algors)):
            self.vars.append(tk.StringVar())  # 获取复选框变量
        self.createPage()

    def set_window(self):
        """设置窗口大小"""
        # 获取屏幕分辨率
        screenWidth = self.root.winfo_screenwidth()
        screenHeight = self.root.winfo_screenheight()
        x = int((screenWidth - self.winWidth) / 2)
        y = int((screenHeight - self.winHeight) / 2)
        # 设置窗口初始位置在屏幕居中
        self.root.geometry("%sx%s+%s+%s" % (self.winWidth, self.winHeight, x, y))

    def cal_hash(self, path_list):
        self.pb1["value"] = 0
        self.pb1["maximum"] = 0  # 总项目数
        self.pb2["value"] = 0
        self.pb2["maximum"] = 0  # 总项目数

        args = []  # 存放要计算的算法
        for temp in self.vars:
            if temp.get():
                args.append(temp.get())
        self.pb2["maximum"] = len(path_list)  # 总项目数
        for item in path_list:
            temp_result = hash_core.cal_hash_by_path(item, args, self)
            self.pb2["value"] += 1
            self.result.update(temp_result)
        print("所有项目计算完成！")

    def dragged_files(self, files):
        path_list = []
        for item in files:
            dir_path = item.decode("gbk")
            path_list.append(dir_path)
        t = threading.Thread(target=self.cal_hash, args=(path_list,))
        t.setDaemon(True)
        t.start()

    def selectPath(self):
        """浏览文件计算hash值"""
        path_ = askopenfilename()
        t = threading.Thread(target=self.cal_hash, args=([path_, ],))
        t.setDaemon(True)
        t.start()

    def windndGet(self):
        windnd.hook_dropfiles(self.root, func=self.dragged_files)

    def changeCase(self):
        """切换大小写"""
        self.scr.delete(1.0, "end")
        for file in self.result:
            self.scr.insert("end", '%s:\t%s\n' % ("文件", file))
            for item in self.result[file]:
                if item == "size":
                    info_str = "%s:\t%s" % ("大小", self.result[file][item])
                elif item == "mtime":
                    info_str = "%s:\t%s" % ("修改时间", self.result[file][item])
                elif item == "version":
                    info_str = "%s:\t%s" % ("文件版本", self.result[file][item])
                else:
                    info_str = "%s:\t%s" % (item, self.result[file][item])
                # 修改大小写
                if self.upper.get() is True:
                    self.scr.insert("end", '%s\n' % info_str.upper())
                else:
                    self.scr.insert("end", '%s\n' % info_str.lower())
            self.scr.insert("end", "\n")
        self.scr.see("end")

    def writehash(self):
        hash_path = asksaveasfilename(filetypes=[('文本文件', '.txt'), ])
        if hash_path:
            if not hash_path.endswith(".txt"):
                hash_path += ".txt"
            hash_core.writeHash(hash_path, self.scr.get(1.0, "end"))

    def clear(self):
        """用于清除数据"""
        self.pb1["value"] = 0
        self.pb1["maximum"] = 0  # 总项目数
        self.pb2["value"] = 0
        self.pb2["maximum"] = 0  # 总项目数
        self.scr.delete(1.0, 'end')  # 清空文本区
        self.result.clear()

    def createPage(self):
        # 计算hash值
        self.f_hash = ttk.Frame(self)  # hash模块
        self.f_check = ttk.Frame(self)  # 校对字符串模块
        self.f_algo = ttk.Frame(self.f_hash)   # 算法
        self.f_option = ttk.Frame(self.f_hash)  # 选项
        self.f_content = ttk.Frame(self.f_hash)  # 显示内容
        self.f_bottom = ttk.Frame(self.f_hash)  # 查找/校对字符串
        self.f_hash.pack()
        # self.f_check.pack()
        # self.f_algo.pack()
        # self.f_option.pack()
        # self.f_content.pack()
        self.f_algo.grid(row=0, stick=tk.EW)
        self.f_option.grid(row=2, stick=tk.EW)
        self.f_content.grid(row=3, stick=tk.EW)
        self.f_bottom.grid(row=4, stick=tk.EW)
        ttk.Label(self.f_algo, text='算法: ').grid(row=1, stick=tk.W)
        col = 1
        row = 1
        for index, item in enumerate(self.vars):
            value = self.algors[index]
            if index < 3:
                item.set(value)
            else:
                item.set('')
            cb = ttk.Checkbutton(self.f_algo, text=value, variable=item, onvalue=value, offvalue='')
            cb.grid(column=col, row=row, stick=tk.W, ipadx=5)
            col += 1
        ttk.Label(self.f_option, text='显示: ').grid(row=4, stick=tk.W)
        ttk.Radiobutton(self.f_option, text="大写", variable=self.upper, value=True, command=self.changeCase).grid(row=4, column=1, sticky=tk.EW)
        ttk.Radiobutton(self.f_option, text="小写", variable=self.upper, value=False, command=self.changeCase).grid(row=4, column=2, sticky=tk.W)
        self.upper.set(False)
        ttk.Label(self.f_option, text="", width=34).grid(row=4, column=3, sticky=tk.EW)  # 用于调整布局，空标签，无意义
        ttk.Button(self.f_option, text='浏览', command=self.selectPath).grid(row=4, column=4, stick=tk.E, pady=10)
        ttk.Button(self.f_option, text='清除', command=self.clear).grid(row=4, column=5, stick=tk.E, pady=10)
        ttk.Button(self.f_option, text='保存', command=self.writehash).grid(row=4, column=6, stick=tk.E, pady=10)
        ttk.Label(self.f_content, text='进度: ').grid(row=0, stick=tk.W)
        ttk.Label(self.f_content, text='完成: ').grid(row=1, stick=tk.W, pady=5)
        self.pb1 = ttk.Progressbar(self.f_content, orient="horizontal", length=600, value=0, mode="determinate")
        self.pb1.grid(row=0, column=1, stick=tk.EW)
        self.pb2 = ttk.Progressbar(self.f_content, orient="horizontal", length=600, value=0, mode="determinate")
        self.pb2.grid(row=1, column=1, stick=tk.EW, pady=5)

        scrolW = 80
        scrolH = 25
        self.scr = scrolledtext.ScrolledText(self.f_content, width=scrolW, height=scrolH, wrap=tk.WORD)
        self.scr.grid(column=0, row=2, columnspan=2, sticky='WE')
        ttk.Entry(self.f_bottom, textvariable=self.search_str, width=65).grid(row=2, column=0, stick=tk.EW)
        ttk.Button(self.f_bottom, text="查找", command=self.search).grid(row=2, column=1, sticky='E')
        self.btn_check = ttk.Button(self.f_bottom, text="校对字符串", command=self.show_check)
        self.btn_check.grid(row=2, column=2, sticky='E', pady=5)

        windnd.hook_dropfiles(self.root, func=self.dragged_files)  # 监听文件拖拽操作

        # 校对字符串
        ttk.Label(self.f_check, text='字符串1: ').grid(row=1, stick=tk.W, pady=5)
        ttk.Entry(self.f_check, textvariable=self.str1, width=80).grid(row=1, column=1, columnspan=9, stick=tk.EW)
        ttk.Label(self.f_check, text='字符串2: ').grid(row=2, stick=tk.W, pady=5)
        ttk.Entry(self.f_check, textvariable=self.str2, width=80).grid(row=2, column=1, columnspan=9, stick=tk.EW)

        ttk.Label(self.f_check, text='设置模式: ').grid(row=3, stick=tk.W, pady=5)
        ttk.Checkbutton(self.f_check, text="忽略大小写差异", variable=self.ignore_case_flag, onvalue=True, offvalue=False).grid(column=1,
                                                                                                                 row=3,
                                                                                                                 sticky=tk.W)
        ttk.Checkbutton(self.f_check, text="忽略字符串前后空格", variable=self.ignore_space_flag, onvalue=True, offvalue=False).grid(column=2,
                                                                                                                    row=3,
                                                                                                                    sticky=tk.W)
        ttk.Checkbutton(self.f_check, text="忽略所有空格", variable=self.only_char_flag, onvalue=True, offvalue=False).grid(column=3, row=3,
                                                                                                              sticky=tk.W)
        self.ignore_case_flag.set(True)  # 默认忽略大小写
        self.ignore_space_flag.set(True)  # 默认忽略前后空格
        self.only_char_flag.set(False)
        ttk.Button(self.f_check, text='清除', command=self.clear_check).grid(row=3, column=8, stick=tk.E, pady=5)
        ttk.Button(self.f_check, text='比对', command=self.run_check).grid(row=3, column=9, stick=tk.E, pady=5)
        tk.Label(self.f_check, text='比对结果：').grid(row=4, stick=tk.W, pady=10)  # 用于展示比对结果
        self.l_result = tk.Label(self.f_check, text='待比对！', background="white")  # 用于展示比对结果
        self.l_result.grid(row=4, column=1, columnspan=9, stick=tk.EW, pady=10)

    def search(self):
        """用于从计算结果中搜索指定字符串"""
        content = self.scr.get(1.0, tk.END)
        search_str = self.search_str.get()  # 要搜索的字符串
        if self.upper.get() is True:
            search_str = search_str.upper()
        else:
            search_str = search_str.lower()
        print("search_str", search_str)
        count = content.count(search_str)

        if not count:
            # 未搜索到
            self.scr.delete(1.0, tk.END)
            self.scr.insert(tk.END, content)
            # print("tk.END: ", tk.END)
            self.scr.see(tk.END)
            mBox.showinfo("完成", "未搜索到匹配结果！")
        else:
            # 搜索字符串在content中
            if content:
                self.scr.delete(1.0, tk.END)
                strs = content.split(search_str)
                i = 0
                for item in strs:
                    self.scr.insert(tk.END, item)
                    i += 1
                    if i <= count:
                        self.scr.insert(tk.END, search_str, "tag")  # 匹配到的内容 “tag”标签标记后面做格式
                self.scr.tag_config('tag', background='RoyalBlue', foreground="white")
                self.scr.see(tk.END)
                mBox.showinfo("完成", "一共搜索到%s处！" % count)

    def clear_check(self):
        """用于清除数据"""
        self.str1.set("")
        self.str2.set("")
        self.l_result["background"] = "white"
        self.l_result["text"] = "待比对！"

    def show_check(self):
        """用于校对字符串模块的显示及隐藏"""
        if self.btn_check["text"] == "校对字符串":
            self.btn_check.config(text="隐藏校对模块")
            self.winHeight = 630
            self.root.geometry("%sx%s" % (self.winWidth, self.winHeight))
            self.f_check.pack()
        else:
            self.btn_check.config(text="校对字符串")
            self.f_check.pack_forget()
            self.winHeight = 500
            self.root.geometry("%sx%s" % (self.winWidth, self.winHeight))

    def run_check(self):
        self.l_result["background"] = "white"
        self.l_result["text"] = "待比对！"
        t = threading.Thread(target=self.check_txt)
        t.setDaemon(True)
        t.start()

    def check_txt(self):
        """
        用于比较文本内容
        :return: True 内容一致  False 内容不一致
        """
        text1 = self.str1.get()
        text2 = self.str2.get()
        new_text1 = text1
        new_text2 = text2
        if self.ignore_space_flag.get():
            new_text1 = text1.strip()
            new_text2 = text2.strip()
        if self.ignore_case_flag.get():
            try:
                if self.upper.get():
                    new_text1 = new_text1.upper()
                    new_text2 = new_text2.upper()
                else:
                    new_text1 = new_text1.lower()
                    new_text2 = new_text2.lower()
            except Exception as e:
                print(e)
        if self.only_char_flag.get():
            new_text1 = ''.join(new_text1.split())  # 不设置切割符的话默认是按照所有空字符切
            new_text2 = ''.join(new_text2.split())
        print(text1, '>>>', new_text1)
        print(text2, '>>>', new_text2)
        if new_text1 == new_text2:
            print("内容一致！")
            self.l_result["background"] = "green"
            self.l_result["text"] = "字符串内容一致！"
            return True
        else:
            # self.l_result["background"] = "red"
            self.l_result["background"] = "#ff5151"
            self.l_result["text"] = "字符串内容不一致！"
            print("内容不一致！")
            return False

