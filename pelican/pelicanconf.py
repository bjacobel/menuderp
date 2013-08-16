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

LOGO = u'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" version="1.1" x="0px" y="0px" width="80px" height="80px" viewBox="-6.05 -16.73 80 80" enable-background="new -6.05 -16.73 80 80" xml:space="preserve"><g><circle fill="#918A8A" cx="35.7" cy="17" r="26"/><g><g><polygon fill="#E67E22" points="29.5,5 41.4,28.8 53.3,5"/></g></g><g><g><polygon fill="#3498DB" points="29.6,5 17.8,28.8 41.5,28.8"/></g></g></g></svg>'

# Uncomment following line if you want document-relative URLs when developing
#RELATIVE_URLS = True
