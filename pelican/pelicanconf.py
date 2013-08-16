#!/usr/bin/env python
# -*- coding: utf-8 -*- #
from __future__ import unicode_literals

AUTHOR = u'Menuwatch'
SITENAME = u'News | Menuwatch'
SITEURL = 'http://news.menuwat.ch'

THEME = u'themes/pelican-svbtle/'

TIMEZONE = 'America/New_York'

DEFAULT_LANG = u'en'

# Feed generation is usually not desired when developing
FEED_ALL_ATOM = None
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None

# Blogroll
LINKS =  (
    ('Twitter >', 'http://twitter.com/menuwatch'),
    ('GitHub >', 'http://github.com/bjacobel/menuwatch'),
)

# Social widget
#SOCIAL = (('You can add links in your config file', '#'),
#          ('Another social link', '#'),)

DEFAULT_PAGINATION = False

GOOGLE_ANALYTICS = u'UA-38327978-2'

AUTHOR_BIO = 'A website designed around the Bowdoin dining experience. <a href="http://www.menuwat.ch">menuwat.ch</a>'

# Uncomment following line if you want document-relative URLs when developing
#RELATIVE_URLS = True
