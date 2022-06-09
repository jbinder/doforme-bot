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

* Each participating user needs to add the bot as contact.
* The bot needs to be added to at least one group.
* Each participating user needs to post a message in those groups once the bot has been added. This will allow the bot to register the groups and its users.

For members in this group it than is possible to assign tasks to other members which have been registered by the bot as described above.

Users can assign (/do \<task title\>), list (/tasks), show stats (/stats), etc. in the private chat with the bot.
Open task reminders are also shown in the private chat.
The bot posts status updates and weekly review messages to the group.

#### Supergroups

Following [actions](https://t.me/tgbetachat/59941) automatically cause groups to be converted to supergroups.
If that happens, it is attempted to automatically migrate the data. Still, in some cases it might be necessary to remove and add the bot again to those groups, and also to follow the setup (member detection) procedure as described above.


### Admin

The admin id is a Telegram user id and allows the specified user to perform following commands:

* admin-stats: Shows basic stats of the data in the database.
* admin-announce \<text\>: Sends \<text\> to all users.
* admin-feedback-show: Lists unresolved (not done) feedback entries.
* admin-feedback-reply \<id\> \<text\>: Sends \<text\> to the user that issued feedback \<id\>.
* admin-feedback-close \<id\>: Marks feedback \<id\> as done.
