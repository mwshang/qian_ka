from main.gui.gui import RuningTaskWindow
from main.gui.tasklistui import TileListWindow

_runningWindow = None
_tileListWindow = None

def getRunningWindow():
    global _runningWindow
    if _runningWindow == None:
        _runningWindow = None
