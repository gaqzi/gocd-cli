==========
Change Log
==========

WIP - Some point
================

Added
-----

* pipeline check command

  Will check a pipeline to see whether it's currently stalled or failed.

  Created with the intention to be run through Nagios

* pipeline check-all command

  Will iterate over all pipelines and warn/critical if any is stalled/failed
  that is not paused.

* pipeline list

  Will list all pipelines and their current status.
  Created to be able to list all pipelines currently paused or locked.

`0.7.1`_ - 2015-08-23
=====================

Changed
-------

* Changed to depend on version >= 0.7.1 of gocd because of bug fixes.
  For more info see the `release notes`_ for py-gocd.

.. _`release notes`: https://github.com/gaqzi/py-gocd/releases/tag/v.0.7.1

`0.7.0.3`_ - 2015-08-11
=======================

Nothing much to say here, initial public release. :)

.. _`0.7.1`: https://github.com/gaqzi/gocd-cli/compare/v0.7.0.3...v0.7.1
.. _`0.7.0.3`: https://github.com/gaqzi/gocd-cli/releases/tag/v0.7.0.3
