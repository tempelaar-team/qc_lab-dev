from datetime import datetime
# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'QC Lab'
year = datetime.now().year
copyright = f'2024-{year}, Tempelaar Group'
author = 'Tempelaar Group'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.duration',
    'sphinx.ext.doctest',
    'sphinx.ext.autodoc',
   'sphinx.ext.autosummary',
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']



# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output
#import sphinx_rtd_theme
#html_theme = 'sphinx_rtd_theme'
#html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]
html_theme = 'pydata_sphinx_theme' #'bizstyle'#
html_static_path = ['_static']
html_theme_options = {
    'body_max_width': '100%',  # Remove maximum width constraint
    "github_url": "https://github.com/tempelaar-team/qclab",
    "collapse_navigation": True,
    "show_nav_level":2,
    "secondary_sidebar_items": ["page-toc", "sourcelink"],
}
html_css_files=['custom.css']

#html_sidebars = {
#    "**": ["sidebar-nav-bs", "sidebar-ethical-ads"],
#}
html_sidebars = {
    "**": ["sidebar-nav-bs.html", "sidebar-ethical-ads.html"],
    "quickstart": [],
    "model_class": [],
    "ingredients": [],
}
