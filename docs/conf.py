# pylint: skip-file
# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import sys

sys.path.insert(0, os.path.abspath("."))
sys.path.insert(0, os.path.abspath("../"))
sys.path.insert(1, os.path.dirname(os.path.abspath("../")) + os.sep + "starknet")
sys.path.append(os.path.abspath("./_ext"))

# -- Project information -----------------------------------------------------

project = "Starknet.py"
copyright = "2023, Software Mansion"
author = "Software Mansion"


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
needs_extensions = {"enum_tools.autoenum": "0.9.0"}

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosectionlabel",
    "sphinx_rtd_theme",
    "enum_tools.autoenum",
    "codesnippet",
    "autoclass_with_examples",
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# Add note about documentation from development branch
if os.environ.get("READTHEDOCS_VERSION") == "development":
    rst_prolog = """.. attention::

        This page was created from `development <https://github.com/software-mansion/starknet.py>`_ branch.
    """


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "furo"

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]

html_css_files = ["custom.css"]

autodoc_class_signature = "separated"
autodoc_default_options = {"exclude-members": "__new__"}

pygments_dark_style = "dracula"

html_favicon = "_static/favicon.png"
html_title = "StarkNet.py Documentation"
html_short_title = "StarkNet.py"
html_permalinks_icon = "#"

html_theme_options = {
    "light_logo": "logo.png",
    "dark_logo": "logo-contour-white.png",
}
