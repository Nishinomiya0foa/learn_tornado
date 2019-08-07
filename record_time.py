import tornado.ioloop
import tornado.web
import tornado.websocket
from tornado import gen
from tornado.options import define,options,parse_command_line
import asyncio

clients=dict()#客户端Session字典

class IndexHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    @gen.coroutine
    def get(self):
        print("123")
        self.render("index.html")

class MyWebSocketHandler(tornado.websocket.WebSocketHandler):
    def open(self, *args, **kwargs): #有新链接时被调用
        self.id=self.get_argument("Id")
        self.stream.set_nodelay(True)
        clients[self.id]={"id":self.id,"object":self}#保存Session到clients字典中

    def on_message(self, message):#收到消息时被调用
        print("Client %s received a message:%s"%(self.id,message))

    def on_close(self): #关闭链接时被调用
        if self.id in clients:
            del clients[self.id]
            print("Client %s is closed"%(self.id))

    def check_origin(self, origin):
        return True
app=tornado.web.Application([
    (r'/',IndexHandler),
    (r'/websocket',MyWebSocketHandler),
])


import threading
import time
class SendThread(threading.Thread):
    # 启动单独的线程运行此函数，每隔1秒向所有的客户端推送当前时间
    def run(self):
        # tornado 5 中引入asyncio.set_event_loop,不然会报错
        asyncio.set_event_loop(asyncio.new_event_loop())
        import datetime
        while True:
            for key in clients.keys():
                msg = str(datetime.datetime.now())
                clients[key]["object"].write_message(msg)
                print("write to client %s:%s" % (key, msg))
            time.sleep(1)


if __name__ == '__main__':
    #启动推送时间线程
    SendThread().start()
    parse_command_line()
    app.listen(8888)
    #挂起运行
    tornado.ioloop.IOLoop.instance().start()