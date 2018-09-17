DoForMe
=======

A Telegram bot to assign tasks to other people.
Just add it to a group and follow the instructions.

:construction: Under construction!


Requirements
------------

* Python 3.6
* Register the bot with privacy status 'disabled'


Usage
-----

Run python main.py -t [your telegram token] -a [admin id]

The admin id is a Telegram user id and allows the specified user to perform following commands:

* admin-stats: Shows basic stats of the data in the database.
* admin-announce ([text]): Sends [text] to all users.
* admin-feedback-show: Lists unresolved (not done) feedback entries.
* admin-feedback-reply ([id] [text]): Sends [text] to the user that issued feedback [id].
* admin-feedback-close ([id]): Marks feedback [id] as done.

Install
-------

pip install -r requirements.txt


Libraries
---------

* https://github.com/grcanosa/telegram-calendar-keyboard
