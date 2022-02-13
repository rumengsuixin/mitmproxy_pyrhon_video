import json
import queue
import socket
import time
import os
import re
import threading

import mitmproxy.http
from mitmproxy import ctx


pthread_dynamic_id = 1  # 线程动态id



class V:
    def __init__(self):
        """

        """
        self.describe = None
        print('V 对象初始化')

    def update(self, flow: mitmproxy.http.HTTPFlow) -> None:
        """
        切换包
        @param flow: 包对象
        """
        self.flow = flow

    def parse_describe_html(self, flow: mitmproxy.http.HTTPFlow): pass
    def parse_describe_json(self, flow: mitmproxy.http.HTTPFlow): pass

    def handle(self): pass

# iqiyi
class Iqiyi(V):
    def parse_describe_html(self, flow: mitmproxy.http.HTTPFlow):
        """
        爱奇艺 iqiyi 视频 playvideoinfo 接口数据解解析
        """
        html = flow.response.content.decode('utf-8')

        title = re.compile('<title>(.+)</title>')
        irTitle = re.compile('<meta  name="irTitle" content="(.+)" />')
        irAlbumName = re.compile('<meta  name="irAlbumName" content="(.+)" />')

        irTitles = irTitle.findall(html)
        irAlbumNames = irAlbumName.findall(html)
        titles = title.findall(html)


        if len(irAlbumNames) == 0:
            irAlbumNames = titles

        if len(irTitles) and len(irAlbumNames):
            self.describe = {
                'drama': irAlbumNames[0],  # 剧名
                'drama_series': irTitles[0]  # 剧集
            }
    def parse_describe_json(self, flow: mitmproxy.http.HTTPFlow):
        """
        爱奇艺 iqiyi 视频 playvideoinfo 接口数据解解析
        """
        html = flow.response.content.decode('utf-8')
        irTitle = re.compile('"an": "(.*?)"')
        irAlbumName = re.compile('"vn": "(.*?)"')
        irTitles = irTitle.findall(html)
        irAlbumNames = irAlbumName.findall(html)
        if len(irTitles) and len(irAlbumNames):
            self.describe = {
                'drama': irAlbumNames[0],  # 剧名
                'drama_series': irTitles[0]  # 剧集
            }
    def get_task_info(self, counter) -> dict:
        """
        iqiyi 处理函数
        @type counter: Counter
        @param counter: counter 对象
        @return dict or None
        """
        json_data = json.loads(self.flow.response.content.decode('utf-8'))

        list_data = json_data['data']['program']['video']

        for data in list_data:
            for key, _ in data.items():
                # 因为有些包没有m3u8, 迭代寻找m3u8的键值,
                if key == 'm3u8':
                    if data['scrsz'] != '':  # 解析到一个视频
                        # 构建任务对象参数
                        path = 'E:\\video\\iqiyi\\%s\\%s\\' % (
                            self.describe['drama'], self.describe['drama_series'])
                        m3u8 = '%s.m3u8' % data['scrsz']
                        mp4 = '%s.mp4' % data['scrsz']

                        # 验证目录是否存在
                        if not os.path.exists(path):
                            os.makedirs(path)  # 创建路径目录

                        # 保存或更新 m3u8 文件
                        with open(path+m3u8, 'wb') as f:
                            f.write(bytes(data['m3u8'], 'utf-8'))

                        return {
                            'path': path,
                            'm3u8': m3u8,
                            'mp4': mp4
                        }
    def request(self, flow: mitmproxy.http.HTTPFlow):
        return flow

    def response(self, flow: mitmproxy.http.HTTPFlow):
        # 事实上 可能先要区分视频所属不同公司的工作空间 （后续改进）

        # 解析 iqiyi 视频路径信息
        iqiyi_re_compile = re.compile('http[s]?://www\.iqiyi\.com/.+\.html.*')
        if not iqiyi_re_compile.search(flow.request.url) is None and flow.response.status_code == 200:
            # 解析视频描述信息
            self.parse_describe_html(flow = flow) # 此方法会处理当前流， 并将修改 describe 成员

        # 解析 iqiyi 视频路径信息
        iqiyi_re_compile = re.compile('http[s]?://pcw-api\.iqiyi\.com/video/video/playervideoinfo?.*')
        if not iqiyi_re_compile.search(flow.request.url) is None and flow.response.status_code == 200:
            # 解析视频描述信息
            self.parse_describe_json(flow = flow) # 此方法会处理当前流， 并将修改 describe 成员


        # aqiyi
        if 'cache.video.iqiyi.com' in flow.request.url:
            # 此处开始分析包含视频文件的信息， 但是由于接口顺序关系， 只替换流， 不进行处理
            self.update(flow = flow)  # 切换流
            task_info = self.get_task_info(self)

            if not task_info is None:
                # 此处创建一个socket 对象并尝试连接至 socket_server 发送信息
                with socket.socket(family = socket.AF_INET, type = socket.SOCK_STREAM) as s:
                    # 连接面板的 socket 对象
                    s.connect(('127.0.0.1', 1234))

                    # 连接成功后发送任务信息
                    s.sendall(json.dumps(task_info).encode('utf-8'))
                    # 发送无需获取返回值， 单工通信即可， 此处只负责发送

        return flow

class YouKu(V):
    pass

# 建立一个 socket 对象1
addons = [
    Iqiyi(),
    YouKu()
]

'''
 
command

mitmdump -s start_up_by_mitmproxy.py --allow-hosts 'cache\.video\.iqiyi\.com'

mitmdump -s start_up_by_mitmproxy.py --ignore-hosts "^(?![0-9\.]+)(?!cache\.video\.iqiyi\.com)(?!www\.iqiyi\.com)(?!pcw-api\.iqiyi\.com)"


'''
