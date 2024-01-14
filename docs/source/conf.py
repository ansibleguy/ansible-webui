from datetime import datetime

# pylint: disable=W0622

project = 'Ansible WebUI'
copyright = f'{datetime.now().year}, AnsibleGuy'
author = 'AnsibleGuy'
extensions = ['sphinx_rtd_theme', 'myst_parser']
templates_path = ['_templates']
exclude_patterns = []
html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']
html_logo = 'https://raw.githubusercontent.com/ansible/logos/main/vscode-ansible-logo/vscode-ansible.svg'
html_favicon = 'https://raw.githubusercontent.com/ansible/logos/main/vscode-ansible-logo/vscode-ansible.svg'
html_css_files = ['css/main.css']
master_doc = 'index'
display_version = True
sticky_navigation = True
source_suffix = {
    '.rst': 'restructuredtext',
    '.md': 'markdown',
}
html_theme_options = {}
