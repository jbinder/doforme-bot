bot_name = "DoForMeBot"

texts_informal = {
    'help': "Use\n"
            f"/do [your task title] - to start distributing tasks to your helpful peers "
            f"(private chat with the bot only)\n"
            f"/do [title] @[username] in [count] [days|weeks|...] - to start distributing tasks to your helpful peers "
            f"(in groups only)\n"
            f"/tasks - to list your duties\n"
            f"/stats - to list some numbers about your work\n"
            f"/feedback [your message] - to report issues or get in contact with the doforme-team\n"
            f"/help - to show this info\n\n"
            f"Note: All tasks from groups that you leave will be deleted!\n\n"
            f"WARNING: This bot is not fully grown up, it might forget data, be asleep, confuse data, etc.\n"
            f"Use at your own risk, there is no liability whatsoever."
            f"Please use the feedback command or find the doforme-bot on GitHub "
            f"to report any issues, thanks a lot!",
    'announcement-prefix': "Hi, there is an announcement from the doforme-team:",
    'feedback-thanks': "Thanks for your feedback, the doforme-team will have a look and might get back to you.",
    'feedback-reply-prefix': "Hi, there is a reply from the doforme-team to your feedback:",
    'user-welcome': lambda chat_title, name: f"Welcome in the {chat_title}'s realm of productivity, {name}!",
    'user-goodbye': lambda name: f"Farewell, my dear little exhausted busy bee {name}!",
}

texts_formal = {
    'help': "Use\n"
            f"/do [your task title] - to create a task in the private chat with the bot\n"
            f"/do [title] @[username] in [count] [days|weeks|...] - to create in groups\n"
            f"/tasks - to list tasks\n"
            f"/stats - to show some numbers about your work\n"
            f"/feedback [your message] - to report issues or get in contact with the doforme-team\n"
            f"/help - to show this info\n\n"
            f"Note: All tasks from groups that you leave will be deleted!\n\n"
            f"WARNING: This bot is not completely stable as of now.\n"
            f"Use it at your own risk, there is no liability whatsoever."
            f"Please use the feedback command or find the doforme-bot on GitHub "
            f"to report any issues, thanks a lot!",
    'user-welcome': lambda chat_title, name: f"Welcome in the {chat_title} team, {name}!",
    'user-goodbye': lambda name: f"Farewell {name}, thanks for your contributions!",
}

texts = {**texts_informal, **texts_formal}
