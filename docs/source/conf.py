from datetime import datetime

# pylint: disable=W0622
_logo = 'https://raw.githubusercontent.com/ansibleguy/webui/latest/src/ansibleguy-webui/aw/static/img/logo.svg'

project = 'AnsibleGuy WebUI'
copyright = f'{datetime.now().year}, AnsibleGuy'
author = 'AnsibleGuy'
extensions = ['piccolo_theme']
templates_path = ['_templates']
exclude_patterns = []
html_theme = 'piccolo_theme'
html_static_path = ['_static']
html_logo = _logo
html_favicon = _logo
html_css_files = ['css/main.css']
master_doc = 'index'
display_version = True
sticky_navigation = True
source_suffix = {
    '.rst': 'restructuredtext',
    '.md': 'markdown',
}
html_theme_options = {
    'banner_text': '<a href="https://github.com/ansibleguy/webui">Repository on GitHub</a> | '
                   '<a href="https://github.com/ansibleguy/webui/issues/new/choose">Report errors</a>'
}
html_short_title = 'Ansible WebUI'
