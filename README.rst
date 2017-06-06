Slack Status Bar
================


Install the dependencies
------------------------

.. code-block:: bash

    pip install -r requirements.txt


Configure settings
------------------

- Edit /Users/<username>/Library/Application Support/Slack Status/config.yaml
- Enter the token for your Slack user
- Enter your work wireless SSID
- Enter names for your work and vacation calendars

To run in application mode
--------------------------

Run the following command to build the application into alias mode.

.. code-block:: bash

    python setup.py py2app -A

Then run the following to start the application

    open dist/status.app
    
To run in developer mode
------------------------

Running from the command line

.. code-block:: bash

    python status.py
