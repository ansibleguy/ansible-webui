.. _usage_integrations:

.. include:: ../_include/head.rst

============
Integrations
============


ARA Records Ansible
*******************

ARA can be used to gather detailed statistics of Ansible executions.

To enable AW to send data to an ARA server - you need to:

* Install the :code:`ara` Python3 module on your controller system
* Configure the server at :code:`System - Config`

Quote: ara provides Ansible reporting by recording ansible and ansible-playbook commands regardless of how and where they run.

`Documentation <https://ara.readthedocs.io/>`_ | `Repository <https://github.com/ansible-community/ara>`_

----

Identity Providers using SAML SSO
*********************************

Easily integrate with SAML2 SSO identity providers like Okta, Azure AD and others.

For configuration - see: :ref:`Usage - Authentication <usage_auth>`
