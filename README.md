DoForMe
=======

A Telegram bot for assigning tasks to other people based on [python-telegram-bot-base](https://github.com/jbinder/python-telegram-bot-base), see [README.md](docs/README.md).
It helps you keeping track of your own tasks as well as tasks that you assigned others.

Try it out on [Telegram](https://telegram.me/doformebot) (Warning: things might break, use at your own risk!).
Just add @DoForMeBot as contact, to a group, and follow the instructions.

Features
--------

* Create tasks including due date and assignee
* Mark tasks as complete
* Edit due date of tasks
* Daily reminder of your open tasks
* Weekly review
* Privacy
  * Task info is cleared as soon as it is not used anymore
  * Leaving the group causes destruction of own data associated with that group


Setup
-----

For setup, configuration, and usage instructions see [README.md](docs/README.md).


Usage
-----

### User

Each participating user needs to add the bot as contact. Furthermore the bot needs to be added to a group.
For members in this group it is possible to assign tasks to other members if they have been detected by the bot.
To get detected, all users need to write an informal message in the group after the bot has been added.

Users can assign (/do \<task title\>), list (/tasks), show stats (/stats), etc. in the private chat with the bot.
Open task reminders are also shown in the private chat.
The bot posts status updates and weekly review messages to the group.


### Admin

The admin id is a Telegram user id and allows the specified user to perform following commands:

* admin-stats: Shows basic stats of the data in the database.
* admin-announce \<text\>: Sends \<text\> to all users.
* admin-feedback-show: Lists unresolved (not done) feedback entries.
* admin-feedback-reply \<id\> \<text\>: Sends \<text\> to the user that issued feedback \<id\>.
* admin-feedback-close \<id\>: Marks feedback \<id\> as done.
