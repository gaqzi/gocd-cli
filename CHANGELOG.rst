==========
Change Log
==========

`0.9.1`_ - 2015-11-06
=====================

**Changed**

* Expand user home path from the passwd db on POSIX systems.

  This fixes bug `#8`_

* Any output from the cli will go to STDOUT

.. _#8: https://github.com/gaqzi/gocd-cli/issues/8

`0.9.0`_ - 2015-10-26
=====================

**Added**

* encryption support for configuration values

  Keys ending in ``_encrypted`` will be decrypted using the encryption module
  ``encryption_module``. This was added as a requirement from a client where
  the password may not be stored in plain text, but it is fine to have it
  stored on the same computer. The default `Caesar`_ module is not
  recommended for production use.

  For a module with a better encryption see `gocd-cli.encryption.blowfish`_.

* settings decrypt/encrypt

  Decrypts/encrypts string or settings in the settings file.

  **Note** does not store changes in the settings file.

.. _Caesar: https://en.wikipedia.org/wiki/Caesar_cipher
.. _gocd-cli.encryption.blowfish: https://github.com/gaqzi/gocd-cli.encryption.blowfish

0.8.1 - 2015-09-16
==================

**Changed**

* Depend on gocd version 0.8.0 or newer.

`0.8.0`_ - 2015-09-16
=====================

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

.. _`0.9.1`: https://github.com/gaqzi/gocd-cli/compare/v0.9.0...v0.9.1
.. _`0.9.0`: https://github.com/gaqzi/gocd-cli/compare/v0.8.0...v0.9.0
.. _`0.8.0`: https://github.com/gaqzi/gocd-cli/compare/v0.7.1...v0.8.0
.. _`0.7.1`: https://github.com/gaqzi/gocd-cli/compare/v0.7.0.3...v0.7.1
.. _`0.7.0.3`: https://github.com/gaqzi/gocd-cli/releases/tag/v0.7.0.3
