#!/usr/bin/env python
import tornado.ioloop
import tornado.web
import tornado.autoreload
from tornado.escape import json_encode

import safeurl
import types
import sys
import datetime
import calendar
import time
import re
import mimetypes
import re
import glob
import jsbeautifier
import time
import urllib.parse
import datetime
import requests

from netaddr import *
from collections import defaultdict
from bs4 import BeautifulSoup
from html import escape

#------------------------------------------------------------
# Base / Status Code Handlers
#------------------------------------------------------------


class BaseHandler(tornado.web.RequestHandler):

    def get_current_user(self):
        return []

    def write_error(self, status_code, **kwargs):
        if status_code in [403, 404, 500, 503]:
            self.render(
                'templates/error.html',
                status_code=status_code
            )


class ErrorHandler(tornado.web.ErrorHandler, BaseHandler):
    # override to prevent errors

    def get_current_user(self):
        return
    pass

#------------------------------------------------------------
# /
#------------------------------------------------------------


class MainHandler(BaseHandler):

    def initialize(self):
        return

    def get(self):
        self.render(
            'templates/index.html',
        )

#------------------------------------------------------------
# /about
#------------------------------------------------------------


class ViewAboutHandler(BaseHandler):

    def initialize(self):
        return

    def get(self):
        self.render(
            'templates/about.html',
        )

#------------------------------------------------------------
# /readme
#------------------------------------------------------------

class ViewReadmeHandler(BaseHandler):

    def initialize(self):
        return

    def get(self):
        self.render(
            'templates/readme.html',
        )

#------------------------------------------------------------
# /parse/ajax
#------------------------------------------------------------

class ViewParseAjaxHandler(BaseHandler):

    def initialize(self):
        return

    def find_str(self, s, char):
        index = 0
        if char in s:
            c = char[0]
            for ch in s:
                if ch == c:
                    if s[index:index+len(char)] == char:
                        return index
                index += 1
        return -1

    def findEntireLine(self, contents, str):
        lineNum = 0
        for item in contents.split("\n"):
            if str in item:
                linkPos = self.find_str(item, str)
                return item, lineNum, linkPos
            lineNum = lineNum+1

    def parseForLinks(self, contents):
        discoveredLinks = []
        outputLinks = []
        # Borrowed from https://github.com/GerbenJavado/LinkFinder/
        addition = ("","")
        regex = re.compile(r"""
		  (%s(?:"|')
		  (?:
		    ((?:[a-zA-Z]{1,10}://|//)
		    [^"'/]{1,}\.
		    [a-zA-Z]{2,}[^"']{0,})
		    |
		    ((?:/|\.\./|\./)
		    [^"'><,;| *()(%%$^/\\\[\]]
		    [^"'><,;|()]{1,})
		    |
		    ([a-zA-Z0-9_\-/]{1,}/
		    [a-zA-Z0-9_\-/]{1,}\.[a-z]{1,4}
		    (?:[\?|/][^"|']{0,}|))
		    |
		    ([a-zA-Z0-9_\-]{1,}
		    \.(?:php|asp|aspx|jsp)
		    (?:\?[^"|']{0,}|))
		  )
		  (?:"|')%s)
		""" % addition, re.VERBOSE)        
        links = re.finditer(regex, contents)
        for link in links:
            linkStr = link.group(0)
            # discoveredLinks list to avoid dupes and complex dupe checks
            if linkStr not in discoveredLinks:
                # get the entire line, line number, and link position
                entireLine, lineNum, linkPos = self.findEntireLine(
                    contents, linkStr)
                discoveredLinks.append(linkStr)
                outputLinks.append({
                    "line": entireLine,
                    "link": linkStr,
                    "lineNum": lineNum,
                    "linkPos": linkPos
                })
        return outputLinks

    def getFormattedTimestamp(self):
        d = datetime.datetime.now()
        formatted = "{}_{}_{}_{}-{}".format(d.month,
                                            d.day, d.year, d.hour, d.minute)
        return formatted

    def formatHTMLOutput(self, html):
        output = output + html
        return output

    def beautifyJS(self, content):
        return jsbeautifier.beautify(content)

    def isLongLine(self, line):
        if len(line) > 1000:
            return True
        return False

    def fileRoutine(self, url, content):
        html = ""

        # beautify the JS for cleaner parsing
        # note: this can be slow against large JS files and can lead to failure
        prettyContent = self.beautifyJS(content)

        # parse all the links out
        parsedLinks = self.parseForLinks(prettyContent)

        # if we have results, start building HTML
        if parsedLinks:
            print("Discovered {} links in {}".format(len(parsedLinks), url))
            # generate HTML output
            # html = html+'<h1>{}</h1><div class="file">'.format(url)
            html = html+'<div class="file">'
            for link in parsedLinks:
                html = html+"<h2>{}</h2>".format(link["link"][1:-1])
                # Get positions for highlighting
                startPos = link["linkPos"]
                endPos = link["linkPos"]+len(link["link"])
                # highlight the link
                if self.isLongLine(link["line"]):
                    highlightedLine = '...{}<span class="highlight"\
                    >{}</span>{}...'.format(escape(
                        link["line"][startPos-100:startPos]),
                        link["link"],
                        escape(link["line"][endPos:100])
                    )
                else:
                    highlightedLine = '{}<span class="highlight"\
                    >{}</span>{}'.format(
                        escape(link["line"][:startPos]),
                        link["link"],
                        escape(link["line"][endPos:])
                    )
                # generate the link HTML
                html = html + \
                    '<div class="link">{}: {}</div>'.format(
                        link["lineNum"], highlightedLine)
            html = html+'</div>'
        return html

    def fetchURL(self, url):
        sc = safeurl.SafeURL()
        res = sc.execute(url)
        return res

    def parseLinks(self, url):
        html = ""
        file = self.fetchURL(url)
        html = html + self.fileRoutine(url, file)
        return html

    def get(self):

        error = False
        errorMsg = ""

        url = self.get_argument("url")

        if error == False:

            data = self.parseLinks(url)

            # set content-type
            self.set_header('Content-Type', 'application/json')

            # output
            self.write(json_encode({
                "url": url,
                "output": data,
            }))

        else:

            self.write("error")


#------------------------------------------------------------
# Main
#------------------------------------------------------------


portNum = 8008
print("Running on http://localhost:8008")

# Application Settings
settings = {
    'default_handler_class': ErrorHandler,
    'default_handler_args': dict(status_code=404),
}

# Endpoints
urls = [

    (r"/", MainHandler),

    (r"/images/(.*)", tornado.web.StaticFileHandler, {"path": "images/"}),
    (r"/js/(.*)", tornado.web.StaticFileHandler, {"path": "js/"}),
    (r"/css/(.*)", tornado.web.StaticFileHandler, {"path": "css/"}),
    (r"/fonts/(.*)", tornado.web.StaticFileHandler, {"path": "fonts/"}),

    (r"/parse/ajax", ViewParseAjaxHandler),
    (r"/about", ViewAboutHandler),
    (r"/readme", ViewReadmeHandler)

]

application = tornado.web.Application(
    urls,
    debug=True,
    **settings
)

if __name__ == "__main__":
    application.listen(portNum)
    tornado.ioloop.IOLoop.current().start()
