python-telegram-bot
===================

A seed for Python Telegram bots.


Components
----------

### user

Currently used to determine which users are members of chats where the bot has been added to.
This is done by observing added users and senders of messages.

### feedback

Allows users to provide feedback, and the admin to view, respond, and close feedback.

### announce

Allows the admin to send messages to all users.

### core

For now used to send welcome and help messages.


Install
-------

* Requires Python 3.6
* Install dependencies: pip install -r requirements.txt
* Register the bot with privacy status 'disabled'


Run
---

The bot can be run using as console (polling, recommended for local testing)
as well as web app (webhook, for deployment).

### Console

Run python main.py -t [your telegram token] -a [admin id]

### Web app

A Flask web app of the bot is available in app.py. It requires the following environment variables to be set:
* DFM_WEB_IP: the web server ip, e.g. 0.0.0.0
* DFM_WEB_PORT: the web server port, e.g. 8080
* DFM_WEB_DNS: the public domain name of the bot
* DFM_BOT_TOKEN: the Telegram bot token
* DFM_REQUEST_SECRET: a secret to slightly protect requests to the web app
* DFM_ADMIN_ID: the Telegram user id of the admin

### Database

To use a MySQL database instead the default SQLite (common/database.sqlite) database, set the following environment variables:
* DFM_DB_HOST
* DFM_DB_PORT
* DFM_DB_USERNAME
* DFM_DB_PASSWORD
* DFM_DB_DATABASE

Note: The character set of the database needs to be set to utf8mb4!


Usage
-----

The admin id is a Telegram user id and allows the specified user to perform following commands:

* admin-stats: Shows basic stats of the data in the database.
* admin-announce ([text]): Sends [text] to all users.
* admin-feedback-show: Lists unresolved (not done) feedback entries.
* admin-feedback-reply ([id] [text]): Sends [text] to the user that issued feedback [id].
* admin-feedback-close ([id]): Marks feedback [id] as done.


Development
-----------

Run the tests using:

    python -m unittest
