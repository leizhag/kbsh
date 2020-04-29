Kbsh - Work Effectively with Multiple Kubernetes Clusters
=========================================================

|PyPI version| |PyPI pyversions| |License|

Features
-------------------

No Need to Type ``kubectl`` Every Time
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Kbsh accepts the same commands as Kubectl, except you don't
need to provide the ``kubectl`` prefix.

.. image :: https://github.com/leizhag/kbsh/raw/master/docs/images/feat-prefix-free.png

If you want to run a shell command rather than a Kubectl
command, you can add the ``!`` prefix to your command.

.. image :: https://github.com/leizhag/kbsh/raw/master/docs/images/feat-non-kube-cmd.png

Switch Contexts/Namespaces on the Fly
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

You can provide ``--context`` (or ``-c``) option to switch the context,
and ``--namespace`` (or ``-n``) option to switch the namespace, before executing
the command.

.. image :: https://github.com/leizhag/kbsh/raw/master/docs/images/feat-switch.png

Show Contexts and Namespaces at Toolbar
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

One man names a resource, many have to remember it. It may help to display all contexts
and namespaces at the bottom of the shell so that no need to use ``config get-contexts`` and
``get ns``.

.. image :: https://github.com/leizhag/kbsh/raw/master/docs/images/feat-all-ctx.png

Aliases and Short Options
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Built-in aliases:

- ``g`` -> ``get``
- ``d`` -> ``describe``
- ``e`` -> ``exec -i -t``
- ``l `` -> ``logs``
- ``lt`` -> ``logs --tail``
- ``ld`` -> ``logs deploy/``

Built-in short options:

- ``-t`` -> ``--tail``
- ``-c`` -> ``--context``

Although, do not support configuration yet.

.. image :: https://github.com/leizhag/kbsh/raw/master/docs/images/feat-alias.png

Highlight Output
^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. image :: https://github.com/leizhag/kbsh/raw/master/docs/images/feat-highlight.png

Upstream Features
^^^^^^^^^^^^^^^^^^^

Kbsh is forked from ``kube-shell``, and keeps all `its features <https://github.com/cloudnativelabs/kube-shell#kube-shell-features>`_.

Installation
------------

::

    pip install kbsh

Status
------

Kbsh has been working great for my personal use case. But given that its aim is to increase
productivity and easy of use, it can be improved in a number of ways. If
you have suggestions for improvements or new features, or run into a bug
please open an issue
`here <https://github.com/leizhag/kbsh/issues>`__.

Acknowledgement
---------------

Kbsh is forked from `kube-shell <https://github.com/cloudnativelabs/kube-shell>`_.

Kube-shell is inspired by `AWS
Shell <https://github.com/awslabs/aws-shell>`__,
`SAWS <https://github.com/donnemartin/saws>`__ and uses awesome Python
`prompt
toolkit <https://github.com/jonathanslenders/python-prompt-toolkit>`__

.. |PyPI version| image:: https://badge.fury.io/py/kbsh.svg
   :target: https://badge.fury.io/py/kbsh
.. |PyPI pyversions| image:: https://img.shields.io/pypi/pyversions/ansicolortags.svg
   :target: https://pypi.python.org/pypi/kbsh/
.. |License| image:: http://img.shields.io/:license-apache-blue.svg
   :target: http://www.apache.org/licenses/LICENSE-2.0.html
