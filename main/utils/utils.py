
'''
    absClassPath: e.g. 'main.taskList.TaskList'
'''
def createInstanceByAbsClass(absClassPath, *args, **kwargs):
    arr = absClassPath.split(".")
    sarr = arr[0:len(arr) - 1]
    module_name = ".".join(sarr)
    class_name = arr[len(arr) - 1]
    return createInstance(module_name,class_name,*args,**kwargs)

def createInstance(module_name, class_name, *args, **kwargs):
    module_meta = __import__(module_name, globals(), locals(), [class_name])
    class_meta = getattr(module_meta, class_name)
    obj = class_meta(*args, **kwargs)
    return obj