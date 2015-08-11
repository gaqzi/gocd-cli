A command line interface for common `Go Continuous Delivery`_ tasks
===================================================================

.. image:: http://codecov.io/github/gaqzi/py-gocd-cli/coverage.svg?branch=master 
   :target: http://codecov.io/github/gaqzi/py-gocd-cli?branch=master
   :alt: Coverage Status

.. image:: https://snap-ci.com/gaqzi/gocd-cli/branch/master/build_image
   :target: https://snap-ci.com/gaqzi/gocd-cli/branch/master
   :alt: Build Status

.. image:: https://img.shields.io/pypi/v/gocd-cli.svg
   :target: https://pypi.python.org/pypi/gocd-cli/
   :alt: Latest Version

.. image:: https://img.shields.io/pypi/dm/gocd-cli.svg
   :target: https://pypi.python.org/pypi/gocd-cli/
   :alt: Downloads
   
.. image:: https://img.shields.io/pypi/pyversions/gocd-cli.svg
   :target: https://pypi.python.org/pypi/gocd-cli/
   :alt: Python versions   

.. image:: https://img.shields.io/pypi/status/gocd-cli.svg
   :target: https://pypi.python.org/pypi/gocd-cli/
   :alt: Package status

For work I and colleagues have for the last nine months been writing a lot of
different small shell scripts with curl that interacts with the Go API.
 
Most of them are quick n' dirty scripts that aren't very robust, and because
they're written in the mindset of the now we just end up copy+pasting it
everywhere. As well as figuring out what API endpoints are available, how they
work and so on.

The goal of this project is to make these and similar tasks super simple,
without having to write a so-so reliable bash script. And for the most common
things just one invocation.

Note
----

This is still early in the development and a bit rough around the edges.
Any bug reports, feature suggestions, etc are greatly appreciated. :)

I'm planning to add support for all the API endpoints that make sense from a CLI
perspective. And also to handle some of the scenarios where we ended up writing
shell scripts.

Installation and usage
----------------------

**Installation**

Since this is a Python package available on PyPi you can install it like 
any other Python package.

.. code-block:: shell

    # on modern systems with Python you can install with pip
    $ pip install gocd-cli
    # on older systems you can install using easy_install
    $ easy_install gocd-cli


**Usage**
The commands should be mostly self-documenting in how they are defined,
which is made available through the ``help`` command.

.. code-block:: shell

    $ gocd
    usage: gocd <command> <subcommand> [<posarg1>, ...] [--kwarg1=value, ...]
    Commands:
       pipeline
          pause: Pauses the named pipeline
          retrigger-failed: Retrigger a pipeline/stage that has failed
          trigger: Triggers the named pipeline
          unlock: Unlocks the named pipeline if it's currently locked
          unpause: Unpauses the named pipeline
          
    $ gocd help pipeline retrigger-failed
    retrigger-failed <name> [--counter] [--stage] [--retrigger]

    Retrigger a pipeline/stage that has failed

    Flags:
       counter: the pipeline counter to check. Default: latest
       stage: if given the pipeline will only be retriggered if
         this stage failed
       retrigger: possible values (pipeline, stage) default pipeline.
         When pipeline and there's a failed stage retriggers the pipeline.
         When stage and there's a failure retriggers only that stage.
    $ gocd pipeline retrigger-failed Integration --stage external-points --retrigger stage

Configuration
-------------

This script has been prepared to be run two situations:

1. From your local machine
2. From inside of Go

Because of this the configuration is handled by a config file and
it can be overridden by environment variables.

The current options are:

:server: The server to connect to, example: http://go.example.com:8153/
:user: The user to login as
:password: The corresponding password

The configuration file is stored in ``~/.gocd/gocd-cli.cfg`` and is an ini file.
Example:

.. code-block:: ini

  [gocd]
  server = http://localhost:8153/
  user = admin
  password = badger

The environment variables are prefixed with ``GOCD_`` and always ALL CAPS.
Example:

.. code-block:: shell

  GOCD_SERVER=http://loaclhost:8153/
  GOCD_USER=admin
  GOCD_PASSWORD=badger


Writing your own commands
-------------------------

This project uses `namespaced packages`_ which means that you as a 
plugin/command author will extend the official namespace with your 
commands. 

There are several advantages to this:

* The CLI can dynamically be updated with new commands, just 
  install a Python package to get it integrated
* Internal/private commands can easily be used side-by-side with public
  commands, no need to maintain a fork for your personal commands
* Low entry to making your own commands

The way the cli searches for commands is quite straightforward:

* The first argument is the package the command belongs to
* The second argument is the class to call
* Any unnamed parameters are passed in the same order as on the cli
* Any ``--parameters`` gets the dashes stripped and sent as keyword arguments

To make it work this way there's a pattern to keep to. For each package the
``__init__.py`` file will have to provide all the subcommands in the ``__all__``
variable. Each command is a class and it's the name of those classes that are in
the ``__all__`` variable. There is an example `gocd-cli.commands.echo`_ 
which only does the bare minimum to show how all this works.

The subcommands will on the command line be divided by dashes, meaning that
``RetriggerFailed`` will become ``retrigger-failed`` on the command line.

.. code-block:: shell

    $ gocd <command> <subcommand> posarg1 --kwarg1
    # or how it's referred to in code
    $ gocd <package> <command class> posarg1 --kwarg1
    # or when used
    $ gocd pipeline retrigger-failed Simple-with-lock --stage=firstStage \
        --retrigger=stage

Calling help for a command or subcommand will list all available commands, for
more information about each command ask for help on each in turn.

.. _`Go Continuous Delivery`: http://go.cd/
.. _namespaced packages: http://pythonhosted.org/setuptools/setuptools.html#namespace-packages
.. _gocd-cli.commands.echo: https://github.com/gaqzi/gocd-cli.commands.echo
