#!/usr/bin/python
#-*- coding: UTF-8 -*-

import sys, os, re, time, pkgutil
from jinja2 import Template
from datetime import datetime

readme="""
说明:
    将带有简单格式的TXT文件转换为带有目录、作者信息的mobi文件。
    然后就可以邮寄到free.kindle.com来下载啦

用法：
    %s [--debug] 紫川.txt  罗浮.txt
"""

DEBUG=False

def get_tpl(filename):
    return Template(pkgutil.get_data('__main__', filename).decode('utf-8'))

def convert(file):
    print "Dealing: %s" % file
    fin = open(file)
    mobi_file = file.replace('.txt', '') +".mobi"

    meta = {'title': '', 'author': '',
            'template': 'templates/book.html',
            'template-ncx': 'templates/book.ncx',
            'template-opf': 'templates/book.opf',
            'isbn': int(time.mktime(datetime.now().timetuple())),
            'date': datetime.now().strftime("%Y-%m-%d"),
            'cover': None, 'chapters': [], 'sections': []}
    state = 'paragraph'
    paras = ['']
    section = {'name':'_', 'paras': paras}
    chapter = {'name':'_', 'sections': [], 'default': section}
    line_style = 0

    for raw in fin:
        try:
            raw = raw.decode('utf-8')
        except:
            raw = raw.decode('gbk')
        line = raw.replace('\r', '\n').replace('\t', ' ').strip()

        if len(line) < 2:
            continue

        if line.startswith(u'《'):
            line = line.replace(u'》', '').replace(u'《', '#title:')
        if line.startswith(u'简介') or line.startswith(u'内容简介'):
            line = '##brief:' + line
        if line.startswith(u'封面：'):
            line = line.replace(u'封面：', '#cover:')
        if line.startswith(u'作者：'):
            line = line.replace(u'作者：', '#author:')

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

        chapter_name=None
        section_name=None
        # 多个段落内容（例如N个章节）
        m = re.match(u'#@([a-z]+):(.*)', line)
        if m is not None:
            tag, val = m.groups()
            if tag == 'chapter': chapter_name = val
            if tag == 'section': section_name = val

        while True:

            # 猜测章节序号
            m = re.match(u'.*(第.*[卷章部分][ 　].*)[ 　](第.*[章节][ 　]*.*)$', line)
            if m is None:
                m = re.match(u'.*(第.*[卷章部分][ 　].*)[ 　](序[ 　]*幕.*)$', line)
            if m is not None:
                vals = m.groups()
                chapter_name = vals[0]
                section_name = vals[1]
                break;

            # 猜测章节序号
            m = re.match(u'.*(第.*[卷部分][ 　].*)$', line)
            if m is not None:
                vals = m.groups()
                chapter_name = vals[0]
                break;

            # 等效与 #@section:
            m = re.match(u'.*(第.*[章节][ 　].*)$', line)
            if m is None:
                m = re.match(u'.*(第.*[章节])$', line)
            if m is None:
                m = re.match(u'(尾[ 　]*声.*)$', line)
            if m is None:
                m = re.match(u'(序[ 　]*[章幕].*)$', line)
            if m is not None:
                section_name = m.groups()[0]
                break;
            break;
        if chapter_name:
            chapter_name = chapter_name.strip().replace("  ", " ").replace("  ", " ")
            if chapter_name != chapter['name']:
                if DEBUG: print 'chapter:', chapter_name #chapter['name'].encode('utf-8'), len(chapter['sections']), 'sections'
                paras = ['']
                section = {'name': u'_', 'paras': paras}
                chapter = {'name': chapter_name, 'sections': [], 'default': section}
                meta['chapters'].append(chapter)
                line_style = 0  #reset line style
        if section_name:
            section_name = section_name.strip().replace("  ", " ").replace("  ", " ")
            if section_name != section['name']:
                if DEBUG: print '\t', len(chapter['sections']), section_name
                #if DEBUG: print '\t', section['name'].encode('utf-8'), len(section['paras']), 'lines'
                paras = ['']
                section = {'name': section_name, 'paras': paras}
                chapter['sections'].append(section)
        if chapter_name or section_name:
            continue

        # 处理正文（增加换行检测）
        has_space = raw.startswith(u"    ") or raw.startswith(u"　　")
        has_special = line.startswith("--") or line.startswith("==")
        if line_style == 0:
            if has_space: line_style = 2
            else: line_style = 1
        elif line_style == 1:
            paras.append(line)
        elif line_style == 2:
            if has_space or has_special: paras.append(line)
            else: paras[-1] += line

    fin.close()
    print "analyse done: %s. %d Chapters, %d sections" % (file, len(meta['chapters']), len(chapter['sections']) )

    if chapter['name'] == '_' and chapter['sections']:  #no chapter
        print 'using ARTICLE mode'
        for section in chapter['sections']:
            meta['sections'].append( (section['name'], section['paras']) )

    if len(meta['chapters']) == 0 and len(meta['sections']) > 0:
        print 'INFO: no chapters, using Article mode. (%d sections)' % len(meta['sections'])
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
        t = get_tpl(meta[tag])
        open(gen_file, 'w').write(t.render(meta = meta).encode('utf-8'))

    if DEBUG: return
    import subprocess
    print 'Running "ebook-convert" to build .mobi file:%s' % mobi_file
    cmd = u'ebook-convert %s "%s" ' % ('book.opf', mobi_file.decode("UTF-8"))
    if meta['cover']: cmd += u' --cover "%s"' % meta['cover']
    subprocess.call(cmd, shell=True)

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
            if file == '--debug': DEBUG=True
        for file in argv[1:]:
            if file in ['--debug', '--build']: continue
            convert(file)

