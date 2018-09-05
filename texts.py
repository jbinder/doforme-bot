bot_name = "DoForMeBot"
texts = {'help': "Use\n"
                 f"/do [your task title] - to start distributing tasks to your helpful peers\n"
                 f"/tasks - to list your duties\n"
                 f"/help - to show this info\n"
                 f"Note: talk to the bot in the private chat with the bot, not in groups!\n"
                 f"WARNING: This bot is not fully grown up, it might forget data, be asleep, confuse data, etc.\n"
                 f"Please find the doforme-bot on GitHub to report any issues, thanks a lot!",
         'add-to-group': "Please add the bot to a group to get started!",
         'welcome-bot': "Hi all! Please say hi to me so I am able to let others assign task to you!"
                        "Also, please make sure to add me to allow me to interact with you and vice versa.",
         'missing-title': lambda name: f"Please include a task title, {name}!",
         'select-chat': f"Which is the place of power?\nSelect below!",
         'select-user': lambda title, name: f"Whom do you want to enslave doing {title} for you, {name}?\n"
                                            f"Select below!",
         'select-date': "Select a due date!",
         'added-task': lambda name, title: f"I burdened {name} with your request to {title}.",
         'added-task-to-group':
             lambda owner_name, user_name, title: f"{owner_name} loaded {title} on {user_name}'s back.",
         'btn-complete': lambda title: f"Complete {title}",
         'summary-overdue': "Overdue!!!!",
         'summary-due-today': "Due today",
         'summary-due-this-week': "This week",
         'summary-due-later': "Later",
         'summary-due-undefined': "Undefined",
         'task-line-summary': lambda task, chat_name, owner_name: (f"{task.due.date()} - " if task.due else "") +
                                                                  f"{chat_name} - {task.title} ({owner_name})",
         'task-line': lambda chat_title, title, owner_name: f"๏ {chat_title}: {title} from {owner_name}",
         'private-chat-required': f"Please switch to the private chat with @{bot_name} and write your commands there!",
         'user-welcome': lambda chat_title, name: f"Welcome in the {chat_title}'s realm of productivity, {name}!",
         'user-goodbye': lambda name: f"Farewell, my dear little exhausted busy bee {name}!",
         'task-done': lambda title: f"I released you from the task {title}.",
         'task-done-to-group': lambda owner_name, user_name, title: f"{owner_name}: {user_name} completed {title}!"
         }
