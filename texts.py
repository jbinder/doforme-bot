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
         'missing-text': lambda name: f"Please include a text, {name}!",
         'admin': "Admin",
         'feedback-reply-postfix': "If you want to reply to this message, please use the /feedback command!",
         'announcement-prefix': "Hi, there is an announcement from the doforme-team:",
         'announcement-sent': lambda num_users: f"Your announcement has been sent to {num_users} users!",
         }
