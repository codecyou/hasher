import tkinter as tk
from tkinter import ttk
from tkinter.filedialog import askdirectory, askopenfilename, asksaveasfilename
import windnd
from tkinter import scrolledtext
import hash_core
import threading


class CalHashFrame(tk.Frame):  # 继承Frame类
    """计算文件hash值"""
    def __init__(self, master=None):
        tk.Frame.__init__(self, master)
        self.root = master  # 定义内部变量root
        self.dir_path = tk.StringVar()
        self.mode = tk.BooleanVar()  # True 对比目录 False 对比文件
        self.upper = tk.BooleanVar()  # True 大写 False 小写
        self.vars = []
        self.result = {}
        self.algors = ['sha1', 'sha256', 'md5',	"sha224", "sha512", "sha384"]  # 算法
        for i in range(len(self.algors)):
            self.vars.append(tk.StringVar())  # 获取复选框变量
        self.createPage()

    def cal_hash(self, path_list):
        self.pb1["value"] = 0
        self.pb1["maximum"] = 0  # 总项目数
        self.pb2["value"] = 0
        self.pb2["maximum"] = 0  # 总项目数

        args = []  # 存放要计算的算法
        for temp in self.vars:
            if temp:
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
        t.start()

    def selectPath(self):
        if self.mode.get():
            path_ = askdirectory()
        else:
            path_ = askopenfilename()
        self.dir_path.set(path_)

    def run(self):
        T = threading.Thread(target=self.cal_hash, args=([self.dir_path.get(), ],))
        T.start()

    def windndGet(self):
        windnd.hook_dropfiles(self.root, func=self.dragged_files)

    def toupper(self):
        # content = self.scr.get(1.0, "end")
        # self.scr.delete(1.0, "end")
        # self.scr.insert("end", content.upper())
        self.scr.delete(1.0, "end")
        for file in self.result:
            self.scr.insert("end", '%s:\t%s\n' % ("File", file))
            for item in self.result[file]:
                info_str = "%s:\t%s" % (item, self.result[file][item])
                self.scr.insert("end", '%s\n' % info_str.upper())
            self.scr.insert("end", "\n")

    def tolower(self):
        self.scr.delete(1.0, "end")
        for file in self.result:
            self.scr.insert("end", '%s:\t%s\n' % ("File", file))
            for item in self.result[file]:
                info_str = "%s:\t%s" % (item, self.result[file][item])
                self.scr.insert("end", '%s\n' % info_str.lower())
            self.scr.insert("end", "\n")

    def writehash(self):
        hash_path = asksaveasfilename()
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
        tk.Label(self, text='计算hash界面', font=('Arial', 12), width=50, height=2).grid(row=0, column=1, columnspan=7, stick=tk.W, pady=10)
        ttk.Label(self, text='文件路径: ').grid(row=1, stick=tk.W, pady=10)
        ttk.Entry(self, textvariable=self.dir_path, width=60).grid(row=1, column=1, columnspan=6, stick=tk.EW)
        ttk.Button(self, text="浏览", command=self.selectPath).grid(row=1, column=7)

        ttk.Label(self, text='浏览模式: ').grid(row=2, stick=tk.W, pady=10)
        ttk.Radiobutton(self, text="目录", variable=self.mode, value=True).grid(column=1, row=2, sticky=tk.W)
        ttk.Radiobutton(self, text="文件", variable=self.mode, value=False).grid(column=2, row=2, sticky=tk.W)
        self.mode.set(True)

        ttk.Label(self, text='算法: ').grid(row=3, stick=tk.W)
        col = 1
        row = 3
        for index, item in enumerate(self.vars):
            value = self.algors[index]
            if index < 3:
                item.set(value)
            else:
                item.set('')
            cb = ttk.Checkbutton(self, text=value, variable=item, onvalue=value, offvalue='')
            cb.grid(column=col, row=row, stick=tk.W, ipadx=5)
            col += 1

        ttk.Radiobutton(self, text="大写", variable=self.upper, value=True, command=self.toupper).grid(row=2, column=5, sticky=tk.EW)
        ttk.Radiobutton(self, text="小写", variable=self.upper, value=False, command=self.tolower).grid(row=2, column=6, sticky=tk.W)
        self.upper.set(False)
        # ttk.Button(self, text='转换大写', command=self.toupper).grid(row=9, column=1, stick=tk.E, pady=10)
        # ttk.Button(self, text='转换小写', command=self.tolower).grid(row=9, column=2, stick=tk.EW, pady=10)
        ttk.Button(self, text='清除', command=self.clear).grid(row=9, column=5, stick=tk.E, pady=10)
        ttk.Button(self, text='保存', command=self.writehash).grid(row=9, column=6, stick=tk.EW, pady=10)
        ttk.Button(self, text='计算', command=self.run).grid(row=9, column=7, stick=tk.E, pady=10)
        ttk.Label(self, text='进度: ').grid(row=10, stick=tk.W)
        ttk.Label(self, text='完成: ').grid(row=11, stick=tk.W, pady=5)
        self.pb1 = ttk.Progressbar(self, orient="horizontal", length=400, value=0, mode="determinate")
        self.pb1.grid(row=10, column=1, columnspan=7, stick=tk.EW)
        self.pb2 = ttk.Progressbar(self, orient="horizontal", length=400, value=0, mode="determinate")
        self.pb2.grid(row=11, column=1, columnspan=7, stick=tk.EW, pady=5)

        scrolW = 50
        scrolH = 20
        self.scr = scrolledtext.ScrolledText(self, width=scrolW, height=scrolH, wrap=tk.WORD)
        self.scr.grid(column=0, row=12, sticky='WE', columnspan=8)

        windnd.hook_dropfiles(self.root, func=self.dragged_files)


class AboutFrame(tk.Frame):  # 继承Frame类
    def __init__(self, master=None):
        tk.Frame.__init__(self, master)
        self.root = master  # 定义内部变量root
        self.createPage()

    def createPage(self):
        tk.Label(self, text='关于界面', font=('Arial', 12), width=50, height=2).pack()
        ttk.Label(self, text=".....还没想好.....").pack()
