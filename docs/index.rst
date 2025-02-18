.. AuthoritySpoke documentation master file, created by
   sphinx-quickstart on Mon Apr 29 10:48:21 2019.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

=========================================================
AuthoritySpoke: Legal Rules as Data
=========================================================


.. epigraph::
   "when I speak, we speak with authority."

   -- President Donald Trump (Executive Order signing ceremony, February 5, 2025)


Release v\. |release|.

`AuthoritySpoke <https://github.com/mscarey/AuthoritySpoke>`_ is the
first open source legal authority automation tool.

AuthoritySpoke is available as a Python
package `from the Python Package Index <https://pypi.org/project/AuthoritySpoke/>`_,
so you can install it from the command line with pip:

.. parsed-literal::
    $ pip install AuthoritySpoke

AuthoritySpoke runs on Python versions 3.8 and up.

To access these guides in an interactive Jupyter Notebook, you can download the
AuthoritySpoke git repository, or navigate to the "notebooks" folder
of the repository using `Binder <https://mybinder.org/v2/gh/mscarey/AuthoritySpoke/master>`_.

.. toctree::
    :maxdepth: 2
    :caption: User Guides

    guides/introduction.rst
    guides/template_strings.rst
    guides/load_yaml_holdings.rst
    guides/create_holding_data.rst
    guides/statute_rules.rst

.. toctree::
    :maxdepth: 2
    :caption: Examples

    examples/example_holdings.rst

.. toctree::
    :maxdepth: 1
    :caption: API Reference

    api_core
    api_io


.. toctree::
    :maxdepth: 2
    :caption: Development Updates

    history/releases

Indices and tables
------------------

* :ref:`genindex`
* :ref:`modindex`
