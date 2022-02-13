import os
os.environ['KIVY_IMAGE'] = 'pil,sdl2'
import json
import threading
import socket

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.gridlayout import GridLayout
from kivy.properties import ObjectProperty
from kivy.properties import StringProperty
from kivy.app import Builder

Builder.load_file(filename = 'E:\pythonobj\scroll\my.kv')





#  定义一个 task 类
class task:
    def __init__(self, path, m3u8s: list, mp4s: list):
        self.__mp4s = mp4s
        self.__m3u8s = m3u8s
        self.__path = path

    def get_path(self):
        return self.__path

    def get_m3u8(self):
        return self.__path + self.__m3u8s[0]

    def get_mp4(self):
        return self.__path + self.__mp4s[0]

    def __del__(self):
        print('一个任务已经被销毁')


# 任务列表
dl = [
    # task(path = '/root/',m3u8s = ['神魔恋1.m3u8'],mp4s = ['神魔恋1.mp4']),
    # task(path = '/root/',m3u8s = ['神魔恋2.m3u8'],mp4s = ['神魔恋2.mp4']),
    # task(path = '/root/',m3u8s = ['神魔恋3.m3u8'],mp4s = ['神魔恋3.mp4']),
]


# 行
class Row(GridLayout):
    panel: Widget = ObjectProperty(None)  # 面板
    widget_id: str = StringProperty('')  # 行 组件id （包含此行在映射下载信息列表中的索引）
    txt: str = StringProperty('')  # 行文本

    def __init__(self, widget_id: str, panel: Widget, txt: str, **kwargs):
        super(Row, self).__init__(**kwargs)
        self.txt = txt
        self.panel = panel
        self.widget_id = widget_id

    def selector(self):
        # 需要获取他的父级容器
        print(self.panel.ids)
        print(self.widget_id)
        # print(self.widget_id)


class Panel(GridLayout):
    panel_list: Widget = ObjectProperty(None)

    def __init__(self, download_list: list, **kwargs):
        super(Panel, self).__init__(**kwargs)

        # 将列表信息添加入相应组件中
        self.download_list = download_list
        for i in range(len(self.download_list)):
            self.render_(index = i)

    def join_(self, item: bytes, render: bool = False):
        # 处理字节序列
        data = json.loads(item.decode('utf-8'))

        # join to download_list
        self.download_list.append(task(path = data['path'], m3u8s = [data['m3u8']], mp4s = [data['mp4']]))

        if render:
            self.render_(index = len(self.download_list) - 1)

    def render_(self, index: int):
        """

        @param index: 下载列表索引
        """

        # 构建 ids 中 的索引 id
        id = self._id(index)

        # 将创建的raw 对象存入ids中
        self.ids[id] = Row(widget_id = id, panel = self, txt = self.download_list[index].get_m3u8())

        # 将存入 ids 字典中的对象渲染进 panel
        self.panel_list.add_widget(self.ids[id])

    def unrender_(self, widget: Widget):
        self.panel_list.remove_widget(widget = widget)

    def download_(self, widget_id: str):
        # 获取 task
        task_item = self.download_list[self._index(widget_id)]
        # task_item = task()

        args_ = (task_item.get_m3u8(), task_item.get_mp4())

        print('path: ', os.path.exists(task_item.get_path()))
        print('m3u8: ', os.path.exists(task_item.get_m3u8()))
        print('mp4: ', os.path.exists(task_item.get_mp4()))

        if not os.path.exists(task_item.get_mp4()):
            # 线程因为 ffmpeg 执行而堵塞
            os.system('ffmpeg -protocol_whitelist concat,file,http,https,tcp,tls,crypto -i %s -c copy %s' % args_)
        else:
            print('文件已经存在，无需再下载')

    def _id(self, index: int) -> str:
        return str('l__%s' % index)

    def _index(self, id: str) -> int:
        return int(id.split('__')[-1])

    def confirm(self):
        print('confirm')
        print(self.ids)
        print(self.download_list)


class MyApp(App):
    panel: Panel = None

    def build(self):
        self.panel = Panel(download_list = dl)
        return self.panel


def socket_single(**kwargs):
    # panel = Panel(download_list=[])

    # 创建 socket 对象
    with socket.socket(family = socket.AF_INET, type = socket.SOCK_STREAM) as s:
        # 绑定端口号和允许连接的网络地址
        s.bind(('0.0.0.0', 1234))

        s.listen()

        print('socket listening ...')

        while True:  # 开始循环获取客户端连接请求， （有序请求，服务端单线程队列处理连接和请求）
            # 线程等待客户端连接
            c, addr = s.accept()

            try:
                with c:
                    print('connected ', addr)  # 客户端连接成功

                    panel_ = kwargs['app'].panel

                    data = c.recv(1024)
                    if not data:
                        break
                    # tod
                    # o

                    # 先添加 panel download_list 中
                    panel_.join_(item = data, render = True)

                    # c.sendall(data)

            except ConnectionError as ce:  # 连接断开
                print(ce)

            print('资源面板处理了一个 socket 连接')
    print('会话已完毕')


def main():
    # 创建面板对象
    app = MyApp()

    # 在另一个线程中创建 socket
    args_ = {
        'app': app,
        'additional': '个人问候'
    }
    threading.Thread(name = 'socket_single_thread', target = socket_single, kwargs = args_, daemon = True).start()

    # 打开面板
    app.run()


'''
1.打开面板api 并创建一个 socket 对象
2.接受数据并处理



整体思路，打开一个资源面板进程，面板进程可以接收socket 传递进来的信息打印并返回同样的信息给客户端

ffpemg 命令代码
#     os.system(
#         'ffmpeg -protocol_whitelist concat,file,http,https,tcp,tls,crypto -i %s -c copy %s' % (
#             locales['local_m3u8'], locales['local_mp4']))

'''

if __name__ == '__main__':
    main()
