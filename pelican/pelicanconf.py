#!/usr/bin/env python
# -*- coding: utf-8 -*- #
from __future__ import unicode_literals

AUTHOR = u'Menuwatch'
SITENAME = u'News | Menuwatch'
SITEURL = ''

THEME = u'themes/pelican-svbtle/'

TIMEZONE = 'America/New_York'

DEFAULT_LANG = u'en'

# Feed generation is usually not desired when developing
FEED_ALL_ATOM = None
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None

# Blogroll
LINKS =  (
    ('Twitter', 'http://twitter.com/menuwatch'),
    ('<img src="https://github.global.ssl.fastly.net/images/modules/logos_page/GitHub-Logo.png"></img>', 'http://github.com/bjacobel/menuwatch'),
)

# Social widget
#SOCIAL = (('You can add links in your config file', '#'),
#          ('Another social link', '#'),)

DEFAULT_PAGINATION = False

GOOGLE_ANALYTICS = u'UA-38327978-2'

# Uncomment following line if you want document-relative URLs when developing
#RELATIVE_URLS = True
