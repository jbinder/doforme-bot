bot_name = "DoForMeBot"
texts = {'help': "Use\n"
                 f"/do [your task title] - to start distributing tasks to your helpful peers "
                 f"(private chat with the bot only)\n"
                 f"/tasks - to list your duties\n"
                 f"/stats - to list some numbers about your work\n"
                 f"/feedback [your message] - to report issues or get in contact with the doforme-team\n"
                 f"/help - to show this info\n\n"
                 f"Note: All tasks from groups that you leave will be deleted!\n\n"
                 f"WARNING: This bot is not fully grown up, it might forget data, be asleep, confuse data, etc.\n"
                 f"Please use the feedback command or find the doforme-bot on GitHub "
                 f"to report any issues, thanks a lot!",
         'add-to-group': "Please add the bot to a group to get started!",
         'welcome-bot': "Hi all! Please say hi to me so I am able to let others assign task to you!"
                        "Also, please make sure to add me as contact to allow me to interact with you and vice versa.",
         'missing-title': lambda name: f"Please include a task title, {name}!",
         'missing-text': lambda name: f"Please include a text, {name}!",
         'select-chat': f"Which is the place of power?\nSelect below!",
         'select-user': lambda title, name: f"Whom do you want to enslave doing {title} for you, {name}?\n"
                                            f"Select below!",
         'select-date': "Select a due date!",
         'added-task': lambda name, title: f"I burdened {name} with your request to {title}.",
         'added-task-to-group':
             lambda owner_name, user_name, title, due: f"{owner_name} loaded {title} on {user_name}'s back" + (
                 "" if not due else f", due {due.date()}") + ".",
         'update-task-due-request':
             lambda user_name, title, prev_due, due: f"{user_name} requested the change the due date of {title} "
                                                     f"from {prev_due.date()} to {due.date()}.",
         'update-task-due-accepted':
             lambda requestee_name, requestor_name, title, prev_due, due:
             f"{requestee_name} accepted {requestor_name}'s request to change the due date of {title} "
             f"from {prev_due.date()} to {due.date()}.",
         'update-task-due-denied':
             lambda requestee_name, requestor_name, title, prev_due, due:
             f"{requestee_name} denied {requestor_name} to update the due date of {title} "
             f"from {prev_due.date()} to {due.date()}",
         'update-denied': "You denied the request.",
         'update-granted': "You kindly accepted the request.",
         'updated-task-requested': lambda user_name: f"I requested {user_name} to updated your task.",
         'btn-complete': "Complete",
         'btn-edit-date': "Edit date",
         'btn-accept': "Accept",
         'btn-deny': "Deny",
         'summary-headline': "Your open tasks",
         'summary-overdue': "Overdue!!!!",
         'summary-due-today': "Due today",
         'summary-due-this-week': "This week",
         'summary-due-later': "Later",
         'summary-due-undefined': "Undefined",
         'task-line-summary': lambda task, chat_name, owner_name:
         (f"{task.due.date()} - " if task.due else "") + f"{chat_name} - {task.title} ({owner_name})",
         'task-line': lambda chat_title, title, owner_name: f"๏ {chat_title}: {title} from {owner_name}",
         'task-line-group': lambda task, user_name, owner_name: f"๏ " + (f"{task.due.date()} - " if task.due else "") +
                                                                f"{task.title} from {owner_name} for {user_name}",
         'task-overview-group': lambda chat_title: f"Here are {chat_title}'s open tasks",
         'task-overview-private-chat': f"Switch to the private chat with @{bot_name} "
                                       f"to view all of your assigned tasks!",
         'task-headline-assigned': "Tasks you have been assigned",
         'task-headline-owning': "Your tasks for others",
         'task-review': lambda chat_title: f"The following happened this week here at {chat_title}",
         'task-review-summary': lambda num_created, num_done, in_time:
         f"Overall {num_created} task" + ("s have" if num_created != 1 else " has") + " been created and "
         f"{num_done} task" + ("s have" if num_done != 1 else " has") + " been completed" +
         (f" ({in_time}% in time)." if num_done > 0 else "."),
         'task-review-comparison': lambda num_created, num_done, in_time:
         f"Compared to the previous week this is " + ("an increase" if num_created >= 0 else "a decrease") +
         f" of created tasks by {abs(num_created)}, and " + ("an increase" if num_done >= 0 else "a decrease") +
         f" of completed tasks by {abs(num_done)}.",
         'task-review-done-tasks': f"Tasks that have been completed:",
         'task-review-motivation': f"All of you, keep up your great work!",
         'task-line-review': lambda title, user_name, owner_name: f"๏ {user_name} completed {title} from {owner_name}",
         'task-line-review-in-time': lambda in_time: f"in time!" if in_time else "a little late.",
         'task-review-most-busy': lambda user_names, multiple:
         "The most busy bee" + ("s" if multiple else "") + " of this week " + ("are" if multiple else "is") +
         f" {user_names}!\nCongratulations!",
         'private-chat-required': f"Please switch to the private chat with @{bot_name} and write your commands there!",
         'user-welcome': lambda chat_title, name: f"Welcome in the {chat_title}'s realm of productivity, {name}!",
         'user-goodbye': lambda name: f"Farewell, my dear little exhausted busy bee {name}!",
         'task-done': lambda title: f"I released you from the task {title}.",
         'task-done-to-group': lambda owner_name, user_name, title: f"{owner_name}: {user_name} completed {title}!",
         'no-tasks': "Nothing to do right now, enjoy!",
         'tasks-stats-done': lambda count, on_time, late:
         f"{count} task" + ("s" if count != 1 else "") + f" have been completed, {on_time} on time, {late} late.",
         'tasks-stats-open': lambda count, on_time, late:
         f"{count} task" + ("s are" if count != 1 else " is") + f" left open, {on_time} still in time, {late} overdue.",
         'task-stats': lambda owning_count, owning, assigned_count, assigned:
         f"You have been assigned to {assigned_count} tasks:\n{assigned}\n\n"
         f"You assigned others to {owning_count} tasks:\n{owning}",
         'tasks': "Tasks",
         'users': "Users",
         'feedback': "Feedback",
         'feedback-thanks': "Thanks for your feedback, the doforme-team will have a look and might get back to you.",
         'feedback-include-id': "Include the id of the feedback in the form: id [message]",
         'feedback-not-found': "Feedback not found!",
         'feedback-closed': "I closed the feedback!",
         'feedback-none': "Currently there is no open feedback, enjoy!",
         'feedback-new': "There is new feedback!",
         'feedback-reply-prefix': "Hi, there is a reply from the doforme-team to your feedback:",
         'feedback-reply-postfix': "If you want to reply to this message, please use the /feedback command!",
         'feedback-reply-sent': "I sent your reply to the user!",
         'announcement-prefix': "Hi, there is an announcement from the doforme-team:",
         'announcement-sent': lambda num_users: f"Your announcement has been sent to {num_users} users!",
         'admin': "Admin",
         'nothing': "Nothing.",
         }
