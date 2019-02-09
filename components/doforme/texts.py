from common.texts import bot_name

texts = {
    'missing-title': lambda name: f"Please include a task title, {name}!",
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
                                                                                 f"{num_done} task" + (
        "s have" if num_done != 1 else " has") + " been completed" +
    (f" ({in_time}% in time)." if num_done > 0 else "."),
    'task-review-comparison': lambda num_created, num_done, in_time:
    f"Compared to the previous week this is " + ("an increase" if num_created >= 0 else "a decrease") +
    f" of created tasks by {abs(num_created)}, and " + ("an increase" if num_done >= 0 else "a decrease") +
    f" of completed tasks by {abs(num_done)}.",
    'task-review-user-stats': lambda user_name, num_done, on_time:
    f"{user_name}: {num_done} done, {('{:.2f}'.format(on_time))}% on time",
    'task-review-done-tasks': f"Tasks that have been completed:",
    'task-review-incomplete-tasks': f"Unfortunately the following tasks have not yet been completed :(",
    'task-review-motivation': f"All of you, keep up your great work!",
    'task-line-review': lambda title, user_name, owner_name: f"๏ {user_name} completed {title} from {owner_name}",
    'task-line-review-in-time': lambda in_time: f"in time!" if in_time else "a little late.",
    'task-line-review-incomplete': lambda title, user_name, owner_name, num_days: f"๏ {user_name} left {title} from {owner_name} open for already {num_days} day{'s' if num_days != 1 else ''}",
    'task-review-most-busy': lambda user_names, multiple:
    "The most busy bee" + ("s" if multiple else "") + " of this week " + ("are" if multiple else "is") +
    f" {user_names}!\nCongratulations!",
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
    'nothing': "Nothing.",
    'ranking': "User ranking",
    'add-to-group': "Please add the bot to a group to get started!",
}
