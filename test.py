#coding:utf-8
#cppgohan @2012

import os
import urllib2
from urlparse import urlparse

import lxml.html
from element_parser import Parser



def test_temp_code():
    res = urllib2.urlopen('http://www.tianya.cn/publicforum/content/funinfo/1/3526037.shtml')
    res.read()
    f = open('page1.shtml', 'r')
    html = f.read()
    lxml_obj = lxml.html.fromstring(html.decode('gbk'))

    next_page = lxml_obj.cssselect('#pageDivTop > a')[-3]
    print next_page.text
    print next_page.attrib
    next_page.attrib.get('href', '')


def get_next_page_url(lxml_obj):
    next_page = lxml_obj.cssselect('#pageDivTop > a')[-3]
    if next_page.text.find(u'下一页') < 0:
        return None
    return next_page.get('href', None)



def parse_tianya_articles(pageone_url):
    count = 1
    referer_url = None
    while pageone_url:
        print "%02d start parse %s" % (count, pageone_url);
        opener = urllib2.build_opener()
        opener.addheaders = [( 'User-Agent' , 'Mozilla/5.0' )]
        try:
            req = urllib2.Request(pageone_url)
            if referer_url is not None:
                req.add_header('Referer', referer_url)
            #opener.addheaders.update
            res = opener.open(req)
            html = res.read().decode('gbk')
        except Exception as e:
            print 'error %s retry %s ' % (e, pageone_url)
            continue

        count += 1
        lxml_obj = lxml.html.fromstring(html);
        url = pageone_url
        referer_url = url
        pageone_url = get_next_page_url(lxml_obj);
        yield url,lxml_obj

def dump_elements_list(load_result, backup_file):
    string_list = map(lambda x:(x[0], lxml.html.tostring(x[1])), load_result);
    with open(backup_file, 'w') as f:
        import pickle
        pickle.dump(string_list, f)

def load_elements_list(dump_file):
    with open(dump_file, 'r') as f:
        import pickle
        string_list = pickle.load(f)
        return [(x[0], lxml.html.fromstring(x[1])) for x in string_list]

def load_tianya818_url(page_url = None):
    url = page_url or 'http://www.tianya.cn/publicforum/content/funinfo/1/3526037.shtml'
    res = [l for l in parse_tianya_articles(url)]
    return res

def get_posts(page_obj):
    authors = map(lambda x:x.getprevious(), page_obj.cssselect('span[value]'));
    posts = page_obj.cssselect('.post')
    return zip(authors, posts)

def parse_post(post):
    """ 解析一个回帖
        @post[0] 帖子对应的作者名称 HtmlElement.a
        @post[1] 帖子对应的内容 HtmlElement集合 class='post'

        @解析出结果
    """
    result = {}
    result['element'] = []
    result['author'] = post[0].text

    for elem in post[1].xpath('text()|img'):
        result['element'].append(Parser.parse_element(elem))

    return result

def filter_posts_author_only(posts, author):
    """ 只看楼主的post
    """
    return filter(lambda x: x[0]==author, posts)

def download_images_in_post(post, referer_url):
    """ 下载图片到本地
    """
    for elem in post['element']:
        if hasattr(elem, 'need_download') and elem.need_download:
            url = elem.get_download_url()
            url_obj = urlparse(url)
            file_uri = '/'.join(['download', url_obj.netloc, url_obj.path])
            print "start download image %s to %s" % (url, file_uri)

            # 创建文件夹
            file_dir = os.path.split(file_uri)[0]
            if not os.path.exists(file_dir):
                os.makedirs(file_dir)

            while True:
                try:
                    opener = urllib2.build_opener()
                    opener.addheaders = [( 'User-Agent' , 'Mozilla/5.0' )]
                    req = urllib2.Request(url)
                    if referer_url is not None:
                        req.add_header('Referer', referer_url)

                    # 下载图片
                    import shutil
                    res = opener.open(req)
                    with open(file_uri, 'wb') as fp:
                        shutil.copyfileobj(res, fp, 16*1024)

                    print "%s 下载成功" % file_uri
                    elem.set_image_file_uri(file_uri)
                    elem.need_download = False
                    break

                except Exception as e:
                    print 'error %s' % e
                    continue
    return


if __name__ == '__main__':
    res = load_elements_list('tianya818')

    # 读取所有的页到一个对象中, url,lxml_obj
    # res = load_tianya818_url()

    article = {}
    pages = []
    for page in res:
        pages.append((page[0], get_posts(page[1])))

    # 第一页:           pages[0][1]
    # 第一页第一条:     pages[0][1][0]
    # 第一页第一条作者: pages[0][1][0][0]
    article['author'] = pages[0][1][0][0].text
    article['post'] = pages[0][1][0][1]
    t = parse_post(pages[0][1][0])
    download_images_in_post(t, pages[0][0])



