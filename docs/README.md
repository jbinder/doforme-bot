python-telegram-bot-base
========================

[![Build Status](https://travis-ci.org/jbinder/python-telegram-bot-base.svg?branch=master)](https://travis-ci.org/jbinder/python-telegram-bot-base) [![Codacy Badge](https://api.codacy.com/project/badge/Grade/b18c8596c5684727af0c402dd1628760)](https://www.codacy.com/app/jbinder/python-telegram-bot-base?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=jbinder/python-telegram-bot-base&amp;utm_campaign=Badge_Grade)

A seed for Python Telegram bots.


Components
----------

Components typically consist of:
* Models: The Pony entities to persist data in a database
* Texts: Constants and simple lambdas which are used to build responses.
* CommandHandler: The component that handles the interaction with Telegram.
* Service: Service(s), e.g. for handling data persistence.
* Component: This is where the Telegram handlers are registered (mandatory).
* EventType: Contains all the events if the component provides such.

The following components are available:

### user

Currently used to determine which users are members of chats where the bot has been added to.
This is done by observing added users and senders of messages.
It provides the following events:
* USER_LEFT_CHAT: Called when a user left a chat with the argument {'user_id': [user_id], 'chat_id': [chat_id]}.

### feedback

Allows users to provide feedback, and the admin to view, respond, and close feedback.
It provides the following commands:
* feedback [text]: Provide feedback.
* admin-feedback-show: Lists unresolved (not done) feedback entries.
* admin-feedback-reply ([id] [text]): Sends [text] to the user that issued feedback [id].
* admin-feedback-close ([id]): Marks feedback [id] as done.

### announce

Allows the admin to send messages to all users. It provides the following commands:
* admin-announce ([text]): Sends [text] to all users.

### core

For now used to send welcome and help messages. It provides the following commands:
* start: Shows the help message.
* help: Shows the help message.


Setup
-----

* Requires Python 3.6
* Install dependencies: pip install -r requirements.txt
* Register the bot with privacy status 'disabled'


Usage
-----

* Copy [init.example.py](../init.example.py) to [init.py](../init.py), [texts.example.py](../texts.example.py) to [texts.py](../texts.py), and [requirements.example.txt](../requirements.example.txt) to [requirements.txt](../requirements.txt).
* Set the bot name in [texts.py](../texts.py).
* Customize texts of existing components by copying the entries to the [texts.py](../texts.py) file.
* Develop your component(s).
* Register the components that your bot should use in [init.py](../init.py).

### Events

CommandHandlers allow observers to register for event notifications:

    register_observer(event_type: EventType, observer: Callable)


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

To use a MySQL database instead the default SQLite (common/utils/database.sqlite) database, set the following environment variables:
* DFM_DB_HOST
* DFM_DB_PORT
* DFM_DB_USERNAME
* DFM_DB_PASSWORD
* DFM_DB_DATABASE

Note: The character set of the database needs to be set to utf8mb4!

The admin id is the Telegram user id of the user that is allowed to execute admin commands (admin-...).


Development
-----------

Tests can be run using [nose](https://nose.readthedocs.io):

    nosetests 

or using

    scripts/test.sh
