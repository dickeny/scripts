#!/usr/bin/python
#-*- coding: UTF-8 -*-

#    This file originally written by Nirmal Patel (http://nirmalpatel.com/).
#    Some modified to support web pages in chinese by Shen Miren (http://banjuan.net/).


import urllib, re, os, urlparse, logging
import HTMLParser
from BeautifulSoup import BeautifulSoup

NEGATIVE    = re.compile("comment|meta|footer|footnote|foot")
POSITIVE    = re.compile("post|hentry|entry|content|text|body|article|story")
PUNCTUATION = re.compile("""[!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~]""")


def grabTitle(html):
    try:
        soup = BeautifulSoup(html)
        return soup.title
    except HTMLParser.HTMLParseError:
        return u""

def grabContent(link, html):

    replaceBrs = re.compile("<br */? *>[ \r\n]*<br */? *>")
    html = re.sub(replaceBrs, "</p><p>", html)

    try:
        soup = BeautifulSoup(html)
    except HTMLParser.HTMLParseError:
        return u""

    # REMOVE SCRIPTS
    for s in soup.findAll("script"):
        s.extract()

    allParagraphs = soup.findAll("p")
    topParent     = None

    parents = []
    for paragraph in allParagraphs:

        parent = paragraph.parent
        if parent is None:
            continue

        if (parent not in parents):
            parents.append(parent)
            parent.score = 0

            if (parent.has_key("class")):
                if (NEGATIVE.match(parent["class"])):
                    parent.score -= 50
                if (POSITIVE.match(parent["class"])):
                    parent.score += 25

            if (parent.has_key("id")):
                if (NEGATIVE.match(parent["id"])):
                    parent.score -= 50
                if (POSITIVE.match(parent["id"])):
                    parent.score += 25

        if (parent.score == None):
            parent.score = 0

        innerText = paragraph.renderContents() #"".join(paragraph.findAll(text=True))
        if (len(innerText) > 10):
            parent.score += 1

        parent.score += innerText.count(",")
        parent.score += innerText.count("，")

    for parent in parents:
        if ((not topParent) or (parent.score > topParent.score)):
            topParent = parent

    if (not topParent):
        return u""

    # REMOVE LINK'D STYLES
    styleLinks = soup.findAll("link", attrs={"type" : "text/css"})
    for s in styleLinks:
        s.extract()

    # REMOVE ON PAGE STYLES
    for s in soup.findAll("style"):
        s.extract()

    # CLEAN STYLES FROM ELEMENTS IN TOP PARENT
    for ele in topParent.findAll(True):
        del(ele['style'])
        del(ele['class'])

    killDivs(topParent)
    clean(topParent, "form")
    clean(topParent, "object")
    clean(topParent, "iframe")

    fixLinks(topParent, link)

    title = soup.title.text

    return title, topParent.renderContents().decode('utf-8')


def fixLinks(parent, link):
    tags = parent.findAll(True)

    for t in tags:
        if (t.has_key("href")):
            t["href"] = urlparse.urljoin(link, t["href"])
        if (t.has_key("src")):
            t["src"] = urlparse.urljoin(link, t["src"])


def clean(top, tag, minWords=10000):
    tags = top.findAll(tag)

    for t in tags:
        if (t.renderContents().count(" ") < minWords):
            t.extract()


def killDivs(parent):

    divs = parent.findAll("div")
    for d in divs:
        p     = len(d.findAll("p"))
        img   = len(d.findAll("img"))
        li    = len(d.findAll("li"))
        a     = len(d.findAll("a"))
        embed = len(d.findAll("embed"))
        pre   = len(d.findAll("pre"))
        code  = len(d.findAll("code"))
        span  = len(d.findAll("span"))

        if p == 0 and pre == 0 and code == 0 and span > p:
            d.extract()

        contents = d.renderContents()
        chinese = contents.count("，") + contents.count("。")
        if (chinese > 6):
            continue
        if (contents.count(",") < 10):
            if ((pre == 0) and (code == 0)):
                if ((img > p ) or (li > p) or (span > p) or (a > p) or (p == 0) or (embed > 0)):
                #if ((img > p ) or (a > p) or (p == 0) or (embed > 0)):
                    d.extract()


if __name__ == "__main__":
    import urllib2
    link = 'http://banjuan.net/'
    html = urllib2.urlopen(link).read()
    title, page = grabContent(link, html)
    out  = u'<html><head><title>%s</title></head><body>%s</body></html>' % (title, page)
    print out.encode("UTF-8")



