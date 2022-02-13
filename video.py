import os
import time

from selenium import webdriver

'''
打开 Google 浏览器
使用 mitmproxy 代理
'''

if __name__ == '__main__':
    url = 'https://www.iqiyi.com/v_i2fj3m7m3o.html' # 设置网址
    # url = 'https://dagabinhluan.com/blog/page/2/' # 设置网址
    # url = 'https://www.baidu.com' # 设置网址
    # url = input('请在此输入爱奇艺、优酷、腾讯视频播放页面网址\n')

    # 简单检测一下端口
    cmd = os.popen('netstat -ano|findstr 8080')
    if cmd.read() is '':
        print('请检测 mitmproxy 服务器是否处于打开状态,请在打开 mitmproxy 服务器之后再重试。')
    else:
        # 使用代理 google 驱动 从而模拟浏览器发起请求
        chromeOptions = webdriver.ChromeOptions()

        # 设置代理
        chromeOptions.add_argument("--proxy-server=http://127.0.0.1:8080")


        # 一定要注意，=两边不能有空格，不能是这样--proxy-server = http://202.20.16.82:10152
        browser = webdriver.Chrome(chrome_options = chromeOptions, executable_path = "E:/chromedriver/chromedriver.exe")



        # browser.get(url)

