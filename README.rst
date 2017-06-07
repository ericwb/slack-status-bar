Slack Status Bar
================

Overview
--------

The native Slack application has the capability to manually adjust a user's
status, but does nothing automatically. The manual nature of switching your
status based on where or what you're doing is tedious. This app attempts
to ease that pain point by automatically adjusting status based on factors
it can discern.

This status bar automatically (or manually) updates a user's Slack status
based on information from the user's calendars and Wireless SSID in use. It
only works on Mac OSX and is only effective for user's that use Mac's default
calendar application and wireless for networking.

Currently the app can detect 4 types of statuses

- Vacationing - scans the vacation calendar for events for the current time
- In a Meeting -  scans the work calendar for events for the current time
- Working Remotely - compares the SSID currently in use with the given work SSID
- Away - detects the lock state of the screen and sets away if locked

Installation
------------

.. code-block:: bash

    pip install -r requirements.txt

Run the following command to build the application into alias mode.

.. code-block:: bash

    python setup.py py2app -A

Configure settings
------------------

- Edit /Users/<username>/Library/Application Support/Slack Status/config.yaml
- Enter the token for your Slack user
- Enter your work wireless SSID
- Enter names for your work and vacation calendars
- Optionally you may want to edit some of the other settings

To run in application mode
--------------------------

Run the following to start the application

.. code-block:: bash

    open dist/status.app

To run in developer mode
------------------------

Running from the command line

.. code-block:: bash

    python status.py
