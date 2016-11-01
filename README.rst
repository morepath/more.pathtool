more.pathtool: info about paths in Morepath apps
================================================

``more.pathtool`` lets you create a tool that generates information
about paths in a Morepath application. This way you can see exactly
what paths a Morepath application supports, including views and mounted
applications. It does this by reading the configuration information of
a Morepath application.

To create such a tool you do the following, for instance in the
``main.py`` of your project::

  from more.pathtool import path_tool
  from .someplace import SomeApp

  def my_path_tool():
      SomeApp.commit()
      path_tool(SomeApp)

where ``SomeApp`` is the application you want to query, typically the
root application of your project.

Now you need to hook it up in ``setup.py`` to you can have the tool
available::

    entry_points={
        'console_scripts': [
            'morepathtool = myproject.main:path_tool',
        ]
    },

After you install your project, you should now have a ``morepathtool``
tool available that lets you query your project for path information.

By default the path tool generates a CSV file with information in it
about paths in your application::

  $ morepathtool paths.csv

You can open it in a spreadsheet application such as Excel or
OpenOffice Calc.

Columns
-------

The columns in the CSV file are as follows:

path
  The URL path. If this is a named view, the view name is appended
  with a ``+``. If this is an absorb path, the ``/...`` is appended.
  If this is an internal view, the path will be ``internal``.

directive
  The directive used.

filename
  The filename in which this configuration was made.

lineno
  The line number of the configuration.

model
  A dotted name to the model class exposed.

permission
  A dotted name to the permission used for the path. Or ``public`` if no
  permission declared, or ``internal`` if this is an internal view. ``path``
  and ``mount`` directives have no permission.

view_name
  The view name predicate, if any. By default this is empty. ``path``
  and ``mount`` directives have no view name.

request_method
  The request method predicate. By default this is ``GET` ``path`` and
  ``mount`` directives have no request method predicates.

extra_predicates
  Whether there are additional predicates in use. Go to the actual code
  to see them.
