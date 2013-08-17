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

LOGO = u'<svg version="1.1" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" x="0px" y="0px" width="100%" height="100%" viewBox="9.7 -8.98 52 52" enable-background="new 9.7 -8.98 52 52" xml:space="preserve"><g><circle fill="#918A8A" cx="35.7" cy="17.02" r="26"/><g><g><polygon fill="#E67E22" points="29.521,5.039 41.399,28.797 53.277,5.039"/></g></g><g><g><polygon fill="#3498DB" points="29.641,5.042 17.763,28.801 41.519,28.801"/></g></g></g></svg>'

# Uncomment following line if you want document-relative URLs when developing
#RELATIVE_URLS = True
