Cell Types
==========

Python
------

Write and execute Python code in cells like traditional notebooks. Almost all packages available 
in the Python ecosystem are usable within Zero-True notebooks.

SQL
---

Our SQL cells are powered by `duckdb <https://duckdb.org/docs/>`_. You can query csv, parquet, jsons, and other
files as well as dataframes at blazingly fast speed. You can also reference Python variables in 
your SQL queries by using the following syntax:
    
.. code-block:: python

    SELECT * FROM {python_variable_name}

Markdown 
--------

Like many other code notebooks, Zero-True allows you to interweave both Python and markdown so that 
you can easily document your findings and create a narrative using your analysis so that you can 
really tell the data story! 

Text
----

Zero-True also features a rich text editor so that users that are more comfortable writing text 
this way can contribute to notebooks. 