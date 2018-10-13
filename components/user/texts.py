texts = {
    'help': "Use\n"  # TODO: move to common
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
    'welcome-bot': "Hi all! Please say hi to me so I am able to let others assign task to you!"
                   "Also, please make sure to add me as contact to allow me to interact with you and vice versa.",
    'user-welcome': lambda chat_title, name: f"Welcome in the {chat_title}'s realm of productivity, {name}!",
    'user-goodbye': lambda name: f"Farewell, my dear little exhausted busy bee {name}!",
    'add-to-group': "Please add the bot to a group to get started!",
}
