#!/usr/bin/env python2
#-*- coding: UTF-8 -*-

readme="""
说明:
    将带有简单格式的TXT文件转换为带有目录、作者信息的mobi文件。
    然后就可以邮寄到free.kindle.com来下载啦

用法：
    %s  紫川.txt  罗浮.txt
"""

def convert(file):
    from jinja2 import Template
    import os
    import re
    print "%s => %s.html" % (file, file)
    fin = open(file)
    html_file = file+".html"

    meta = {'title': '', 'author': '',
            'template': 'templates/book.html',
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

        paras.append(line)

    fin.close()
    print "analyse done: %s. %d Chapters." % (file, len(meta['chapters']))

    print 'generating  HTML: %s' % html_file
    t = Template(open(meta['template']).read().decode('utf-8'))
    open(html_file, 'w').write(t.render(meta = meta).encode('utf-8'))

    import subprocess
    mobi_file = file + '.mobi'
    print 'Running "kindlegen" to build .mobi file:%s' % mobi_file
    subprocess.call('kindlegen -unicode %s -o "%s"' % (html_file, mobi_file), shell=True)

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

