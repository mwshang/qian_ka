import wx
import time
import threading
from wx.grid import GridTableBase
from main.config import COLUMN_NAMES

try:
    from main.entry import app
except:
    app = wx.App(0)

# def _openView(View,*args):
#     view = View(*args)
#     view.openView()
#
# def OpenView(View,*args):
#
#     timer = threading.Timer(0.1, _openView, (View,*args))
#     timer.setDaemon(True)
#     timer.start()
#
#     time.sleep(5999)

class FrameBase(wx.Panel):
    session = {}
    def __init__(self,title,size,parent=None,style=None):
        super().__init__(parent=parent,  size=size,
                         style=wx.CENTER | wx.ALL | wx.EXPAND)

        self.Center()
        self.contentpanel = wx.Panel(parent=self)
        # icon = wx.Icon("../res/icon/task_item.jpg",wx.BITMAP_TYPE_JPEG)
        # self.SetIcon(icon)

        # 设定窗口大小，这里设置了相同的最大和最小值，也就是固定了窗口大小。
        # 因为上面的窗口风格了保留了wx.RESIZE_BORDER，所以这里用另外一个放来来保证大小不可调整
        # 这样做有一点不好，就是鼠标放在窗口边缘，会变成调整窗口大小的样子，但是拉不动窗口
        self.SetSizeHints(size, size)

        self.Bind(wx.EVT_CLOSE,self.onClose)

    def onClose(self,event):
        self.Destroy()
        # sys.exit()

class ListFrame(FrameBase):
    def __init__(self,parent=None):
        super().__init__("任务列表",(690,600),parent=parent)
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

class RuningTaskWindow(wx.Frame):

    def __init__(self,expire_at,owner=None, parent=None, id=-1):
        wx.Frame.__init__(self, parent, id, '正在进行时任务面板',
                          size=(500, 400))
        # 过期时间
        self.expire_at = expire_at
        self.owner = owner
        self.bgColor = "Green"

        self._initUI()

    def _initUI(self):
        self.panel = wx.Panel(self)
        self.button = wx.Button(self.panel,
                                label="点击设置任务已做完", pos=(0, 50))
        self.display = wx.TextCtrl(self.panel, -1, '', style=wx.TE_RIGHT)
        self.display.AppendText('9')

        self.Bind(wx.EVT_BUTTON, self.OnButtonClick,
                  self.button)  # 1 绑定按钮事件
        self.Bind(wx.EVT_WINDOW_DESTROY, self.onDestroyWindow)

        # 创建定时器
        self.timer = wx.Timer(self)  # 创建定时器
        self.Bind(wx.EVT_TIMER, self.OnTimer, self.timer)  # 绑定一个定时器事件
        self.timer.Start(1000)

    def setExpireAt(self,expire_at):
        self.expire_at = expire_at

    def handleWarning(self):
        self.bgColor = 'Green' if self.bgColor == 'Red' else 'Green' if self.bgColor == 'Red' else 'Red'
        self.panel.SetBackgroundColour(self.bgColor)
        self.panel.Refresh()

    def OnTimer(self, evt):  # 显示时间事件处理函数
        t = self.expire_at - time.time()
        self.display.SetLabelText(str(int(t)))
        if t < 100:
            self.handleWarning()

    def OnButtonClick(self, event):
        self.Close(True)

    def onDestroyWindow(self, event=None):
        if hasattr(self.owner,"setFinised"):
            self.owner.setFinised(True)

    def openView(self):
        self.Show()
        app.MainLoop()

    @staticmethod
    def create(expire_at,owner):
        frame = RuningTaskWindow(expire_at,owner)
        return frame

class Icon(wx.Frame):
    def __init__(self,parent,url):

        self.url = url
        arr = self.url.split(".")
        imgType = arr[len(arr)-1].lower()
        imgType = wx.BITMAP_TYPE_JPEG if imgType == "jpg" else wx.BITMAP_TYPE_PNG if imgType == 'png' else wx.BITMAP_TYPE_BMP
        image = wx.Image(self.url, wx.BITMAP_TYPE_JPEG)
        temp = image.ConvertToBitmap()
        size = temp.GetWidth(), temp.GetHeight()
        super().__init__( parent,size=wx.Size(60,60))

        self.bmp = wx.StaticBitmap(parent=self, bitmap=temp)

class TaskItem(wx.Frame):
    def __init__(self,parent):
        super().__init__(parent)
        self._initUI()

    def _initUI(self):
        # icon = Icon(self,"https://upload.qkcdn.com/a3de8df92bd1572c20ad68fd2bcf232b.jpg")
        icon = Icon(self, "f:\pic1.jpg")


class TaskListView(wx.Panel):
    def __init__(self,parent):
        wx.Panel.__init__(self, parent)
        # wx.StaticText(self,label='Absolute Positioning1')
        # pass
        item = TaskItem(self)


class QianKaTaskListView(TaskListView):
    def __init__(self,parent):
        super().__init__(parent)
        self._initUI()

    def _initUI(self):
        pass

class cjview(wx.Panel):
    def __init__(self,parent):
        wx.Panel.__init__(self, parent)
        wx.StaticText(self,label='Page Two2')
        pass

class cjsave(wx.Panel):
    def __init__(self,parent):
        wx.Panel.__init__(self, parent)
        wx.StaticText(self,label='Page Three3')
        pass


class TryPlayScene(wx.Frame):
    def __init__(self):
        super().__init__(None,title="试玩")

        self._initUI()

    def _initUI(self):
        self.nb = wx.Notebook(self)

        tabDatas = self.getSndTabDatas()
        for v in tabDatas:
            self.nb.AddPage(v['Cls'](self.nb), v["name"])

    def getSndTabDatas(self):
        return [
            {"Cls":TaskListView,"name":"试玩赚钱"},
            {"Cls": cjview, "name" : "试玩赚钱1"},
            {"Cls": cjsave, "name" : "试玩赚钱2"}
        ]

class TryPlayApp(wx.App):
    def OnInit(self):
        b = super().OnInit()
        self._initUI()
        return b

    def _initUI(self):
        # self.scene = TryPlayScene()
        # self.scene.Show()

        MainFrame(None).Show()


class MainFrame(wx.Frame):

    def __init__(self, parent):
        wx.Frame.__init__(self, parent, id=wx.ID_ANY, title=u"试玩", pos=wx.DefaultPosition, size=wx.Size(697, 457),
                          style=wx.DEFAULT_FRAME_STYLE | wx.TAB_TRAVERSAL)

        self.SetSizeHintsSz(wx.DefaultSize, wx.DefaultSize)
        self.SetBackgroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_CAPTIONTEXT))

        bSizer1 = wx.BoxSizer(wx.VERTICAL)

        bSizer1.SetMinSize(wx.Size(697, 495))
        self.m_notebook = wx.Notebook(self, wx.ID_ANY, wx.DefaultPosition, wx.Size(697, 600), 0)
        self.m_qianka = wx.Panel(self.m_notebook, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL)
        self.m_notebook.AddPage(self.m_qianka, u"钱咖", True)
        self.m_xiaoyu = wx.Panel(self.m_notebook, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL)
        self.m_notebook.AddPage(self.m_xiaoyu, u"小鱼", False)
        bSizer1.Add(self.m_notebook, 1, wx.EXPAND | wx.ALL, 5)

        self.SetSizer(bSizer1)
        self.Layout()
        self.Centre(wx.BOTH)

        # lf = ListFrame(parent=self.m_qianka)
        self._initQianKa()

    def _initQianKa(self,m_qianka):
        wx.StaticText(self.m_qianka, label="test")

    def onTabChanged(self,evt):
        print("dd")
        if self.m_notebook.GetCurrentPage() == self.m_qianka:
            print("qiank")
        else:
            print("xiaoyu")

    def __del__(self):
        pass

if __name__ == '__main__':
    app = TryPlayApp(False)
    # frame = wx.Frame(None, title="Demo with Notebook")
    # nb = wx.Notebook(frame)
    # nb.AddPage(cjlists(nb), "试玩赚钱")
    # nb.AddPage(cjview(nb), "Page Two")
    # nb.AddPage(cjsave(nb), "Page Three")
    # frame.Show()
    app.MainLoop()

    # RuningTaskWindow.create(time.time() + 101, {"d": 1}).openView()


