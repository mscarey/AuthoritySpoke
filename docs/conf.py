# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# http://www.sphinx-doc.org/en/master/config

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import sys
import pathlib
import sphinx_rtd_theme

sys.path.insert(0, os.path.abspath(".."))

# -- Project information -----------------------------------------------------

project = "AuthoritySpoke"
copyright = "2019-2020, Matt Carey"
author = "Matt Carey"

# The full version, including alpha/beta/rc tags
release = "0.7.0"


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.inheritance_diagram",
    "sphinx.ext.intersphinx",
    "sphinx_autodoc_typehints",
    "sphinx.ext.graphviz",
    "sphinx_rtd_theme",
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# The master toctree document.
master_doc = "index"

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "sphinx_rtd_theme"

html_theme_options = {
    "logo": "spoke.jpg",
    "github_user": "mscarey",
    "github_repo": "AuthoritySpoke",
}

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "anchorpoint": ("https://anchorpoint.readthedocs.io/en/latest/", None),
    "legislice": ("https://legislice.readthedocs.io/en/latest/", None),
    "nettlesome": ("https://nettlesome.readthedocs.io/en/latest/", None),
    "pint": ("https://pint.readthedocs.io/en/stable/", None),
}

autodoc_member_order = "bysource"

if "READTHEDOCS" in os.environ:
    src_folder = pathlib.Path(__file__).resolve().parent.parent / "authorityspoke"
    sys.path.append(str(src_folder))

    print("Detected running on ReadTheDocs")
    print(f"Added {src_folder} to sys.path")
