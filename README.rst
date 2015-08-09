A command line interface for common `Go Continuous Delivery`_ tasks
===================================================================

.. image:: https://coveralls.io/repos/gaqzi/py-gocd-cli/badge.svg?branch=master&service=github
   :target: https://coveralls.io/github/gaqzi/py-gocd-cli?branch=master
   :alt: Coverage Status

.. image:: https://snap-ci.com/gaqzi/py-gocd-cli/branch/master/build_image
   :target: https://snap-ci.com/gaqzi/py-gocd-cli/branch/master
   :alt: Build Status

.. image:: https://readthedocs.org/projects/py-gocd-cli/badge/?version=latest
   :target: https://readthedocs.org/projects/py-gocd-cli/?badge=latest
   :alt: Documentation Status

.. image:: https://img.shields.io/pypi/v/gocd-cli.svg
   :target: https://pypi.python.org/pypi/gocd-cli/
   :alt: Latest Version

.. image:: https://img.shields.io/pypi/dm/gocd-cli.svg
   :target: https://pypi.python.org/pypi/gocd-cli/
   :alt: Downloads
   
.. image:: https://img.shields.io/pypi/pyversions/gocd-cli.svg
   :target: https://pypi.python.org/pypi/gocd-cli/
   :alt: Python versions


For work I and colleagues have for the last nine months been writing a lot of
different small shell scripts with curl that interacts with the Go api.
 
Most of them are quick works but they aren't very robust, and we keep repeating
the same work and discovery every time we need to do it.

The goal of this project is to make these and similar tasks super simple to do
and repeatable without having to write a so-so reliable bash script.

Usage
-----

This is something I'm writing down before even starting to code, so until this
line is gone this is just an idea of how I imagine a good interaction would be
like.

.. code-block:: shell

    $ gocd pipeline unlock <name>
    $ gocd pipeline pause <name>
    $ gocd pipeline unpause <name>
    $ gocd pipeline trigger <name> [--unlock]
    $ gocd pipeline retrigger-failed <name> [--counter default last] 
                    [--stage only retrigger if this stage failed] 
                    [--retrigger stage|pipeline, default pipeline] 
                    
Help
----

The commands should be mostly self-documenting in how they are defined,
which is made available through the `help` command.

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
    

Writing your own commands
-------------------------

The way the cli searches for commands is quite straightforward:

* The first argument is the package the command belongs to
* The second argument is the class to call
* Any unnamed parameters are passed in the same order as on the cli
* Any --parameters gets the dashes stripped and sent as keyword arguments

To make it work this way there's a pattern to keep to. For each package the
`__init__.py` file will have to provide all the subcommands in the `__all__`
variable. Each command is a class and it's the name of those classes that are in
the `__all__` variable.

The subcommands will on the command line be divided by dashes, meaning that
`RetriggerFailed` will become `retrigger-failed` on the command line.

.. code-block:: shell

    $ gocd <command> <subcommand> posarg1 --kwarg1
    # or how it's referred to in code
    $ gocd <package> <command class> posarg1 --kwarg1
    # or when used
    $ gocd pipeline retrigger-failed Simple-with-lock --stage=firstStage --retrigger=stage

Calling help for a command or subcommand will list all available commands, for
more information about each command ask for help on each in turn.

.. _`Go Continuous Delivery`: http://go.cd/
