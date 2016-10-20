# -*- coding: utf-8 -*-

import sys
import os

# Where pushjet is, so autodoc can find it.
sys.path.insert(0, os.path.abspath('..'))

# Update when the nested classes update is released.
#needs_sphinx = '1.0'
extensions = ['sphinx.ext.autodoc']
source_suffix = '.rst'
master_doc = 'index'

project = u'pushjet (Python API)'
copyright = u'2016, Samuel (@obskyr)'
author = u'Samuel (@obskyr)'
version = '1.0'
release = '1.0.0'

language = 'en'
pygments_style = 'sphinx'
todo_include_todos = False

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']
html_show_sourcelink = True
html_logo = 'pushjet.png'
htmlhelp_basename = 'pushjetdoc'
