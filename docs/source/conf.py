# Configuration file for the Sphinx documentation builder.
#
# For a full list of options see:
# http://www.sphinx-doc.org/en/master/config

# -- Path setup ---------------------------------------------------------
#
# nota2md is installed editable by the builds that render these docs
# (website.yml, test.yml) rather than reached via sys.path manipulation
# here, so conf.py only needs to import the already-installed package to read
# its __version__.

import nota2md

# -- Project information -------------------------------------------------

project = "nota2md"
copyright = "2026, legistlan"
author = "legistlan"

# The repository is the package, so there is a single version here -- kept as
# the same |nota2md_version| substitution the page used while it was one page
# of the site of the monorepo this package was extracted from.
rst_epilog = f"""
.. |nota2md_version| replace:: {nota2md.__version__}
"""

# -- General configuration ------------------------------------------------

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinx.ext.intersphinx",
    "sphinx.ext.doctest",
]

# The page cross-references the names nota2md re-exports or calls into
# (`dofjson.api.get_nota`, `scjn.release.download_scjn_leyes_corpus`, ...)
# where each is defined: the developer reference of each sibling package,
# published under /dev/ of its own GitHub Pages site.
intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "requests": ("https://requests.readthedocs.io/en/latest/", None),
    "dofjson": ("https://legistlan.github.io/dofjson/dev/", None),
    "scjn": ("https://legistlan.github.io/scjn/dev/", None),
    "document2md": ("https://legistlan.github.io/document2md/dev/", None),
}

source_suffix = ".rst"
master_doc = "index"
language = "en"
exclude_patterns = []

pygments_style = "sphinx"
highlight_language = "python"
# Docstrings quote JSON shapes, DOF HTML and console sessions in plain literal
# blocks, which are not Python: Pygments falls back to plain text, and the
# strict build (`-n -W`) must not fail on that fallback.
suppress_warnings = ["misc.highlighting_failure"]
# BeautifulSoup publishes no Sphinx inventory, so the `bs4.element.Tag` in
# nota2md.html_converter's signatures has nothing to resolve against.
nitpick_ignore = [("py:class", "bs4.element.Tag")]
autodoc_member_order = "bysource"
autodoc_class_signature = "separated"
add_function_parentheses = False
add_module_names = False

# -- Options for HTML output ----------------------------------------------

html_theme = "furo"
htmlhelp_basename = "nota2mddoc"
