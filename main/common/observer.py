'''
 消息观察者
'''
class Observer(object):
    def __init__(self):
        self._defalut = "default"
        self.dicType = {}

    def _notify(self, tb, data=None):

        for i in range(len(tb) - 1, -1, -1):
            v = tb[i]
            owner = v.get("owner")
            callback = v.get("callback")
            fixedParam = v.get("fixedParam")

            if v.get("destroyed") != True:

                if owner:
                    if fixedParam:
                        callback(owner, fixedParam, data)
                    else:
                        callback(v.owner, data)

                else:
                    if fixedParam:
                        callback(fixedParam, data)
                    else:
                        callback(data)

            count = v.get("count")
            if count != None:
                count = count - 1
                if count <= 0:
                    del tb[i]
                    v["destroyed"] = True
                else:
                    v['count'] = count

    '''
        添加观察者
        @param {owner,callback=(data) ,
                type="数据类型"
                }
    '''
    def addObserver(self, param):
        _type = param.get('type')

        if _type == None:
            _type = self._defalut
        if self.dicType.get(_type) == None:
            self.dicType[_type] = []

        tb = self.dicType.get(_type)
        flag = True

        for v in tb:
            if v.get("callback") == param.get("callback") and v.get("type") == _type:
                flag = False
                break

        if flag:
            tb.append(param)

    def _remove(self, tb, param):
        if tb == None or param == None:
            return
        for i in range(len(tb) - 1,-1,-1):
            v = tb[i]
            if v.get("callback") == param.get("callback"):
                del tb[i]
                break


    '''
        删除观察者
        @param {callback=def(data) ,
                type="数据类型"
                }
    '''
    def removeObserver(self, param):
        _type = param.get("type")

        if _type == None:
            _type = self._defalut

        if self.dicType[_type]:
            self._remove(self.dicType[_type], param)


    def removeObserverWithType(self, _type):
        self.dicType[_type] = None


    def hasObserver(self, param):
        _type = param.get("type")

        if _type == None:
            _type = self._defalut

        tb = self.dicType[_type]

        if not tb:
            return False

        for v in tb:
            if v.get("callback") == param.get("callback") and v.get("type") == _type:
                return True

        return False


    def hasObserverByType(self, type):
        _type = type

        if _type == None:
            return False

        tb = self.dicType[_type]

        if tb:
            return len(tb) > 0

        return False


    def send(self, _type, data=None):
        if _type == None:
            _type = self._defalut

        if self.dicType.get(_type) != None:
            self._notify(self.dicType[_type], data)


    def clear(self, excepts):
        if excepts:
            dic = {}
            for k, v in excepts:
                dic[v] = self.dicType[v]

            self.dicType = dic
        else:
            self.dicType = {}




if __name__ == '__main__':
    def cb(msg):
        print("cb...." + msg)


    def cb1(msg):
        print("cb1...." + msg)
    observer = Observer()
    observer.addObserver({'type': "fuck", 'callback': cb, 'owner': None})
    observer.addObserver({'type': "fuck", 'callback': cb1, 'owner': None})

    observer.send("fuck","")
    observer.removeObserver({'type': "fuck", 'callback': cb, 'owner': None})
    observer.send("fuck", "")

    if observer.hasObserver({'type':'fuck', 'callback': cb1}):
        print("has...")

    if observer.hasObserverByType("fuck"):
        print("ddd")
