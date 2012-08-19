#coding:utf-8
#cppgohan @2012
import lxml.html
from image import TianyaImage
from text import TianyaText

class Parser(object):
    """
        用于解析对应帖子内容的类, 返回可能的Text对象和Image对象
    """
    @staticmethod
    def parse_element(element):
        if type(element) is lxml.etree._ElementUnicodeResult:
            return Parser._make_text(element)
        elif type(element) is lxml.html.HtmlElement and element.tag == 'img':
            return Parser._make_image(element)

    @staticmethod
    def _make_text(element):
        text_element = TianyaText()
        text_element.text_content = element.encode('utf-8')
        return text_element

    @staticmethod
    def _make_image(element):
        image_element = TianyaImage()
        image_element.image_url = element.attrib['original']
        return image_element
