#coding:utf-8
#cppgohan @2012
"""
爬虫使用的图像接口封装, 渲染时候可以自己输出对应的HTML
"""

class TianyaImage(object):
    def __init__(self):
        self.image_url = None
        self.image_file_uri = None
        self.need_download = True
    def render():
        pass

    def get_download_url(self):
        return self.image_url

    def set_image_file_uri(self, uri):
        self.image_file_uri = uri

    def get_image_file_uri(self):
        return self.image_file_uri

