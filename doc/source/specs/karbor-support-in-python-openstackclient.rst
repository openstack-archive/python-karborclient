..
 This work is licensed under a Creative Commons Attribution 3.0 Unported
 License.

 http://creativecommons.org/licenses/by/3.0/legalcode

========================================
Karbor support in python-openstackclient
========================================

Implement a new set of karbor commands as python-openstackclient plugins.

Launchpad Blueprint:
https://blueprints.launchpad.net/python-karborclient/+spec/karbor-support-python-openstackclient


Problem Description
===================

python-openstackclient is becoming the default command line client for many
OpenStack projects. Karbor would benefit from implementing all of its client
commands as a single python-openstackclient plugin implemented in the
python-karborclient repository.

Proposed Change
===============

The intent of this spec is to identify the commands to be implemented and
establish conventions for command and argument names. This spec is not
intended to be a full and correct specification of command and argument names.
The details can be left to the code reviews for the commands themselves.

The following conventions will be adopted for command names:

* As the ``OpenStackClient`` convention, the command name shall always take
  the following form:

.. code-block:: bash

    openstack [<global-options>] <object-1> <action> [<object-2>] \
              [command-arguments]


As a example:
The following ``karbor`` commands about plan will be implemented for ``openstack``
initially suggesting these command names:

.. code-block:: bash

    karbor plan-create <name> <provider_id> <resources>
    openstack data protection plan create <name> <provider_id> <resources>

    karbor plan-delete <plan>
    openstack data protection plan delete <plan>

    karbor plan-list
    openstack data protection plan list

    karbor plan-show <plan>
    openstack data protection plan show <plan>

    karbor plan-update <name> <resources> <status>
    openstack data protection plan update <name> <resources> <status>


Configuration
-------------

None

Database
--------

None

Public API
----------

None

Public API Security
-------------------

None

Python API
----------

None

CLI (python-karborclient)
-------------------------

A new directory named osc will be created under /karborclient/osc
for the ``OpenStackClient`` plugin and the commands mentioned above.

Internal API
------------

None

Guest Agent
-----------

None

Alternatives
------------

None

Dashboard Impact (UX)
=====================

None

Implementation
==============

Assignee(s)
-----------

Primary assignee:
  chenying


Milestones
----------


Work Items
----------

CLI commands as stated above.
Unit tests

Upgrade Implications
====================

None

Dependencies
============

python-openstackclient
osc-lib

Testing
=======

Unit tests will be located in: /karborclient/tests/unit/osc/

Documentation Impact
====================

OpenStack Client adoption list will be updated to include python-karborclient.

References
==========

https://docs.openstack.org/python-openstackclient/latest/

Appendix
========

None
