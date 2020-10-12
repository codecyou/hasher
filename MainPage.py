from view import *


class MainPage(object):
    def __init__(self, master=None):
        self.root = master  # 定义内部变量root
        # 设置窗口大小
        winWidth = 650
        winHeight = 600
        # 获取屏幕分辨率
        screenWidth = self.root.winfo_screenwidth()
        screenHeight = self.root.winfo_screenheight()

        x = int((screenWidth - winWidth) / 2)
        y = int((screenHeight - winHeight) / 2)

        # 设置窗口初始位置在屏幕居中
        self.root.geometry("%sx%s+%s+%s" % (winWidth, winHeight, x, y))
        self.page = None  # 用于标记功能界面
        self.createPage()

    def createPage(self):
        self.calHashPage = CalHashFrame(self.root)
        self.aboutPage = AboutFrame(self.root)
        self.calHashPage.pack()  # 默认操作界面
        menubar = tk.Menu(self.root)
        menubar.add_command(label='操作', command=self.calHash)
        menubar.add_command(label="关于", command=self.aboutDisp)
        self.root['menu'] = menubar  # 设置菜单栏

    def calHash(self):
        self.calHashPage.pack()
        self.aboutPage.pack_forget()

    def aboutDisp(self):
        self.calHashPage.pack_forget()
        self.aboutPage.pack()


