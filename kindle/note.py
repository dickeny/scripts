#!/usr/bin/python
# -*- coding: UTF-8 -*-

from __future__ import print_function
import re, sys, os
from sys import argv
from BeautifulSoup import BeautifulSoup as BS
from BeautifulSoup import BeautifulStoneSoup as BSS
from urllib2 import urlopen
from collections import OrderedDict

def msg(*args, **kwargs):
    print(*args, end="", **kwargs)

def get_id(url):
    if 'http' not in url:
        return url
    m = re.search(r'http://www.douban.com/people/([^/]*)', url)
    if not m:
        msg('could not find uesrdouban_id in [%s]' % url)
    return m.groups()[0]

def get_info(douban_id):
    url = 'http://www.douban.com/people/'+douban_id
    html = urlopen(url).read().decode('UTF-8')
    soup = BS(html)
    try:
        name = soup.find("h1").text
        intro = soup.find(id='intro_display').renderContents().decode('UTF-8')
        return ( name, intro )
    except:
        return ("", "")

def get_note(url):
    try:
        html = urlopen(url, timeout=5).read().decode('UTF-8')
    except:
        msg('!')
        return ""
    soup = BS(html)
    div = soup.find(id='link-report')
    if not div: return ""
    for img in div.findAll("img"):
        url = img['src']
        filename = os.path.basename(url)
        data = urlopen(url, timeout=5).read()
        open(filename, "w").write(data)
        img['src'] = filename
        msg( '%' )
    return div.renderContents().decode('UTF-8')

def get_notelist(url):
    html = urlopen(url).read().decode('UTF-8')
    a = html.find('<div class="article">')
    b = html.find('<div class="aside">')
    content = html[a:b]
    m = re.findall(r'<a title=".*" href="(http://www.douban.com/note/[0-9]*/)">(.*)</a>', content)
    if not m:
        return []
    d = OrderedDict(m)
    return d.items()

def people(url):
    msg('getting ', url)
    douban_id = get_id(url)

    output = []
    name, info = get_info(douban_id)
    if not name:
        msg(' skip\n')
        return []
    output.append( u'#@chapter:' + name )
    output.append( u'豆瓣ID: @' + douban_id )
    output.append( info )
    output.append( '' )

    url = 'http://www.douban.com/people/'+douban_id+'/notes?start='
    n = 0
    notes = []
    while True:
        msg('*')
        urls = get_notelist(url + str(n))
        if not urls:
            break;
        notes.extend( urls )
        n += len(urls)
    notes.reverse()
    msg(' ', len(notes), 'notes ')
    if len(notes) == 0: return output

    for url, title in notes:
        msg('.')
        content = get_note(url)
        output.append( u'#@section:' + title )
        output.append( content )
        output.append( '' )
    txt = '\n'.join(output).encode('UTF-8')
    open('douban.'+douban_id+'.txt', 'w').write(txt)
    msg(' done\n')
    return output

def run_all(contacts):
    sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)
    output = ['']
    for douban_id in contacts:
        output.append( people(douban_id) )
    txt = '\n'.join(output).encode('UTF-8')
    open('douban.txt', 'w').write(txt)


contacts = [
'qinan', 'sukiss', 'aisk', 'luxiaobao', 'mysad', '50463565',
'munchhausens', '66213648', 'qrzf', '60259191', '73689183',
'lemonhall2012', 'tanxiaomai', '30056740', 
'zeajin', 'kyl',
'2070706', 'lottie9', 'loyuR', '50025437', '14597285', '38735934',
'61923250', '57474462', '14308156', 'yyy18n', '26767111', 'cloudtints',
'4541462', '41332745', '65758999', 'caochao', 'fishniao', 'Queenie.Emika',
'50937084', '51160223', '35153601', 'wenlizhou', '53454691', 'shaylazeng',
'yudafan', '3372020', 'renxiaowen', '67421184', 'tifaqu',
'tantan_', 'lionbb', '59098154', '53265493', 'stevenpapaya',
'hoterran', 'joanna_7', 'since918', 'EchoTu', 'mejet1', 'sumei', 
'z1984s', 'prepuce', 'liudandan', 'bonnae1982',
'lizn007', 'zishuzishu', 'poinousivy', 'hongqn', 'guyi',
'CMGS', 'whales', '2019156', 'Dbxiong', 'Jolie',
'daisychen1942', 'littlealice', 'wolfenstein', '1238695', 'jarod3',
'jasonlou', 'xiaoyaxiaoya', '38150995', 'aprilroro', 'wanying',
'alenwg_cn', '1939348', 'pluskid', 'ml2068', 'huangyongtao',
'smlzhang', '48045145', 'wildold', 'L42y', 'cindyvvv',
'DADANDAN', 'vvoody', 'keats1981', 'flyflyfish', '36796133',
'lisaisa', 'zyzyzhangyuan', 'farmostwood', 'margaretwcblue', 'xmz', 'xiajia'
]

if __name__ == '__main__':
    run_all(contacts)
    #run_all(['prepuce'])

