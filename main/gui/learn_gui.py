import sys
import wx
import wx.grid
from wx.grid import GridTableBase

class FrameBase(wx.Frame):
    session = {}
    def __init__(self,title,size):
        super().__init__(parent=None, title=title, size=size,
                         style=wx.DEFAULT_FRAME_STYLE ^ wx.MAXIMIZE_BOX)

        self.Center()
        self.contentpanel = wx.Panel(parent=self)
        icon = wx.Icon("../res/icon/task_item.jpg",wx.BITMAP_TYPE_JPEG)
        self.SetIcon(icon)

        # 设定窗口大小，这里设置了相同的最大和最小值，也就是固定了窗口大小。
        # 因为上面的窗口风格了保留了wx.RESIZE_BORDER，所以这里用另外一个放来来保证大小不可调整
        # 这样做有一点不好，就是鼠标放在窗口边缘，会变成调整窗口大小的样子，但是拉不动窗口
        self.SetSizeHints(size, size)

        self.Bind(wx.EVT_CLOSE,self.onClose)

    def onClose(self,event):
        self.Destroy()
        # sys.exit()

class LoginFrame(FrameBase):
    def __init__(self):
        super().__init__("登录",(340,230))
        # 创建界面中的控件
        username_st = wx.StaticText(self.contentpanel, label="用户名：")  # 输入框前面的提示标签
        password_st = wx.StaticText(self.contentpanel, label="密码：")
        self.username_txt = wx.TextCtrl(self.contentpanel)  # 输入框
        self.password_txt = wx.TextCtrl(self.contentpanel, style=wx.TE_PASSWORD)

        # 创建FlexGrid布局对象
        fgs = wx.FlexGridSizer(2, 2, 20, 20)  # 2行2列，行间距20，列间距20
        fgs.AddMany([
            # 下面套用了3个分隔，垂直居中，水平靠右，固定的最小尺寸
            (username_st, 1, wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_RIGHT | wx.FIXED_MINSIZE),
            # 位置居中，尺寸是膨胀
            (self.username_txt, 1, wx.CENTER | wx.EXPAND),
            (password_st, 1, wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_RIGHT | wx.FIXED_MINSIZE),
            (self.password_txt, 1, wx.CENTER | wx.EXPAND),
        ])
        # 设置FlexGrid布局对象
        fgs.AddGrowableRow(0, 1)  # 第一个0是指第一行，权重1
        fgs.AddGrowableRow(1, 1)  # 第一个1是指第二行，权重也是1
        # 上面一共就2行，用户名和密码，就是2行的空间是一样的
        fgs.AddGrowableCol(0, 1)  # 第一列，权重1，就是标签的内容
        fgs.AddGrowableCol(1, 4)  # 第二列，权重4，就是输入框，并且输入框是膨胀的应该会撑满
        # 上面2列分成5分，第一列占1/5，第二列占4/5

        # 创建按钮对象
        ok_btn = wx.Button(parent=self.contentpanel, label="确定")
        cancel_btn = wx.Button(parent=self.contentpanel, label="取消")
        # 绑定按钮事件：事件类型，绑定的事件，绑定的按钮
        self.Bind(wx.EVT_BUTTON, self.ok_btn_onclick, ok_btn)
        self.Bind(wx.EVT_BUTTON, self.cancel_btn_onclick, cancel_btn)

        # 创建水平Box布局对象，放上面的2个按钮
        box_btn = wx.BoxSizer(wx.HORIZONTAL)
        # 添加按钮控件：居中，四周都有边框，膨胀。border是设置边框的大小，实际效果没有框，但是占用空间
        box_btn.Add(ok_btn, 1, wx.CENTER | wx.ALL | wx.EXPAND, border=10)
        box_btn.Add(cancel_btn, 1, wx.CENTER | wx.ALL | wx.EXPAND, border=10)

        # 创建垂直Box，把上面的fgs对象和box_btn对象都放进来
        box_outer = wx.BoxSizer(wx.VERTICAL)
        box_outer.Add(fgs, -1, wx.CENTER | wx.ALL | wx.EXPAND, border=25)  # 权重是-1，就是不指定了
        # (wx.ALL ^ wx.TOP)这里只加3面的边框，上面就不加了
        box_outer.Add(box_btn, -1, wx.CENTER | (wx.ALL ^ wx.TOP) | wx.EXPAND, border=20)

        # 上面全部设置完成了，下面是设置Frame窗口内容面板
        self.contentpanel.SetSizer(box_outer)  # self.contentpanel 是在父类里定义的

    def ok_btn_onclick(self, event):
        username = self.username_txt.GetValue()  # 取出输入框的值
        password = self.password_txt.GetValue()
        if username in self.accounts:
            if self.accounts[username].get('pwd') == password:
                self.session['username'] = username
                print("登录成功")
                # 接下来要进入下一个Frame
                frame = ListFrame()
                frame.Show()
                self.Hide()  # 隐藏登录窗口
                return
            else:
                msg = "用户名或密码错误"
        else:
            msg = "用户名不存在"
        print(msg)
        dialog = wx.MessageDialog(self, msg, "登录失败")  # 创建对话框
        dialog.ShowModal()  # 显示对话框
        dialog.Destroy()  # 销毁对话框

    def cancel_btn_onclick(self, event):
        self.on_close(event)

COLUMN_NAMES = ["id", "数量", "奖励", "描述"]

class ListFrame(FrameBase):
    def __init__(self):
        super().__init__("任务列表",(690,600))
        self.data = {}


        splitter = wx.SplitterWindow(self.contentpanel,style=wx.SP_3DBORDER)
        self.stdTaskPanel = self._createStdTaskPanel(splitter)
        self.incommingTaskPanel = self._createIncommingTaskPanel(splitter)
        splitter.SplitVertically(self.stdTaskPanel,self.incommingTaskPanel,550)

        box_outer = wx.BoxSizer(wx.VERTICAL)
        self.contentpanel.SetSizer(box_outer)

        box_outer.Add(splitter, 1, flag=wx.EXPAND | wx.ALL, border=10)

    def setData(self,data):
        self.data = data

        # table = ListGridTable(COLUMN_NAMES, self.data)
        # # 设置网格的表格属性
        # self.grid.SetTable(table, True)
        # self.grid.Refresh()
        self.init_grid()


    def _createStdTaskPanel(self,parent):
        panel =  wx.Panel(parent=parent)

        grid = wx.grid.Grid(panel, name='grid')
        self.grid = grid

        self.Bind(wx.grid.EVT_GRID_LABEL_LEFT_CLICK,self.select_row_handler)
        self.Bind(wx.grid.EVT_GRID_CELL_LEFT_CLICK, self.select_row_handler)

        self.init_grid()  # 还是到另一个函数里去实现

        # 创建水平Box的布局管理器
        box = wx.BoxSizer()
        # 设置Box的网格grid
        box.Add(grid, 1, flag=wx.ALL|wx.EXPAND, border=5)
        panel.SetSizer(box)
        return panel

    def init_grid(self):
        """初始化网格对象"""
        # 通过网格名字获取到对象
        grid = self.FindWindowByName('grid')

        # 创建网格中所需要的表格，这里的表格是一个类
        table = ListGridTable(COLUMN_NAMES, self.data)
        # 设置网格的表格属性
        grid.SetTable(table, True)
        self.table = table

        # 获取网格行的信息对象,40是行高，每一行都是40，后面的列表是单独指定每一行的，这里是空列表
        row_size_info = wx.grid.GridSizesInfo(40, [])
        # 设置网格的行高
        grid.SetRowSizes(row_size_info)
        # 指定列宽，前面是0，后面分别指定每一列的列宽
        col_size_info = wx.grid.GridSizesInfo(0, [100, 80, 130, 200])
        grid.SetColSizes(col_size_info)
        # 设置单元格默认字体
        grid.SetDefaultCellFont(wx.Font(11, wx.FONTFAMILY_DEFAULT,
                                        wx.FONTSTYLE_NORMAL,
                                        wx.FONTWEIGHT_NORMAL,
                                        faceName="微软雅黑"))
        # 设置表格标题的默认字体
        grid.SetLabelFont(wx.Font(11, wx.FONTFAMILY_DEFAULT,
                                  wx.FONTSTYLE_NORMAL,
                                  wx.FONTWEIGHT_NORMAL,
                                  faceName="微软雅黑"))

        # 设置网格选择模式为行选择模式
        grid.SetSelectionMode(grid.wxGridSelectRows)
        # 设置网格不能通过拖动改标高度和宽度
        grid.DisableDragRowSize()
        grid.DisableDragColSize()

        # g = wx.grid.Grid()
        # g.SetDefaultC

    def _createIncommingTaskPanel(self,parent):
        panel = wx.Panel(parent=parent)

        return panel

    def select_row_handler(self, event):
        """选择的网格的行事件处理
        这里会刷新右侧面板的商品类别和名称
        """
        row_selected = event.GetRow()
        if row_selected >= 0:
            selected_data = self.data[row_selected]
            # 商品类别
            category = "商品类别：%s" % selected_data.get('category')
            category_st = self.FindWindowByName('category')
            category_st.SetLabelText(category)  # 先创建好控件，再修改或者设置label
            # 商品名称
            name = "商品名称：%s" % selected_data.get('name_cn')
            name_st = self.FindWindowByName('name')
            name_st.SetLabelText(name)

            # 刷新布局，如果更换了图片应该是要刷新的，没换图片不用刷新
            # self.right_panel.Layout()

        event.Skip()  # 事件跳过，貌似这里没什么用

class ListGridTable(GridTableBase):
    """自定义表格类
    下面分别重构了4个方法
    返回行数、列数、每个单元格的内容、列标题
    """

    def __init__(self, column_names, data):
        super().__init__()
        self.col_labels = column_names
        self.data = data

    def GetNumberRows(self):
        return len(self.data)

    def GetNumberCols(self):

        print(len(self.col_labels))
        return len(self.col_labels)

    def GetValue(self, row, col):
        products = self.data[row]
        return {
            0: products.get('id'),
            1: products.get('qty'),
            2: products.get('reward'),
            3: ",".join(products.get('tags')),
        }.get(col)

    def GetColLabelValue(self, col):
        return self.col_labels[col]

if __name__ == '__main__':
    app = wx.App(0)

    import json

    file = open('tasklist_data.json', 'r', encoding='utf-8')
    datas = json.load(file)
    datas = datas.get("payload").get("tasks")

    lf = ListFrame()
    lf.Show()
    lf.setData(datas)
    app.MainLoop()