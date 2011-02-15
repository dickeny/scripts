#!/usr/bin/env python2
#-*- coding: UTF-8 -*-

import sys,os

readme="""
说明:
    将带有简单格式的TXT文件转换为带有目录、作者信息的mobi文件。
    然后就可以邮寄到free.kindle.com来下载啦

用法：
    %s  紫川.txt  罗浮.txt
"""

BASE_DIR = os.path.dirname( os.path.realpath( __file__ ) )

def convert(file):
    from jinja2 import Template
    import os
    import re
    from datetime import datetime
    import time
    print "Dealing: %s" % file
    fin = open(file)
    mobi_file = file.replace('.txt', '') +".mobi"

    meta = {'title': '', 'author': '',
            'template': 'templates/book.html',
            'template-ncx': 'templates/book.ncx',
            'template-opf': 'templates/book.opf',
            'isbn': int(time.mktime(datetime.now().timetuple())),
            'date': datetime.now().strftime("%Y-%m-%d"),
            'conver': [], 'chapters': []}
    state = 'paragraph'
    paras = []
    chapter = {'name':'_', 'sections': []}
    section = {'name':'_', 'paras':[]}

    for line in fin:
        line = line.decode('utf-8').replace('\r', '\n').strip()
        if len(line) < 2:
            continue

        # 参数值
        m = re.match(u'#([a-z]+):(.*)', line)
        if m is not None:
            tag, val = m.groups()
            meta[tag] = val
            continue

        # 段落内容
        m = re.match(u'##([a-z]+):(.*)', line)
        if m is not None:
            tag, val = m.groups()
            paras = []
            meta[tag] = paras
            continue

        # 多个段落内容（例如N个章节）
        m = re.match(u'#@([a-z]+):(.*)', line)
        if m is not None:
            tag, val = m.groups()
            paras = []
            if tag not in meta:
                meta[tag] = []
            meta[tag].append( (val, paras) )
            continue

        # 猜测章节序号
        m = re.match(u'.*第(.*)[卷章](.*) 第(.*)[章节](.*)', line)
        if m is not None:
            vals = m.groups()
            chapter_name = u'第%s卷%s' % (vals[0], vals[1])
            section_name = u'第%s章%s' % (vals[2], vals[3])
            if chapter_name != chapter['name']:
                #print chapter['name'].encode('utf-8'), len(chapter['sections'])
                chapter = {'name': chapter_name, 'sections': []}
                meta['chapters'].append(chapter)
            if section_name != section['name']:
                #print '\t', section['name'].encode('utf-8'), len(section['paras'])
                paras = []
                section = {'name': section_name, 'paras': paras}
                chapter['sections'].append(section)
            continue

        # 猜测章节序号
        m = re.match(u'.*第([^卷]*)章[ 　](.*)', line) # 等效与 #@section:
        if m is not None:
            tag = 'section'
            val = m.group()
            #print val
            paras = []
            if tag not in meta:
                meta[tag] = []
            meta[tag].append( (val, paras) )
            continue

        paras.append(line)

    fin.close()
    print "analyse done: %s. %d Chapters." % (file, len(meta['chapters']))

    if len(meta['chapters']) == 0 and len(meta['section']) > 0:
        print 'INFO: no chapters, using Article mode.'
        meta['template'] = 'templates/article.html'
        meta['template-ncx'] = 'templates/article.ncx'

    gen_files = {
            'template': 'book.html',
            'template-ncx': 'book.ncx',
            'template-opf': 'book.opf',
            }
    from jinja2 import Environment, PackageLoader
    for tag,gen_file in gen_files.items():
        print 'generating : %s by %s' % (gen_file, meta[tag])
        t = Template(open(BASE_DIR + "/" + meta[tag]).read().decode('utf-8'))
        open(gen_file, 'w').write(t.render(meta = meta).encode('utf-8'))

    import subprocess
    print 'Running "kindlegen" to build .mobi file:%s' % mobi_file
    subprocess.call(BASE_DIR + '/kindlegen -unicode %s -o "%s"' % ('book.opf', mobi_file), shell=True)

    if os.path.isfile(mobi_file) is False:
        print " !!!!!!!!!!!!!!!   %s failed  !!!!!!!!!!!!!!" % file
        return None
    else:
        fsize = os.path.getsize(mobi_file)
        print "\n>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"
        print ".mobi save as: %s(%.2fMB)" %  (mobi_file, fsize/1048576)
        print ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>\n"
        return mobi_file

if __name__ == '__main__':
    from sys import argv
    if len(argv) < 2:
        print readme % (argv[0])
    else:
        for file in argv[1:]:
            convert(file)

