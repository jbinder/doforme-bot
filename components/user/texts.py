texts = {
    'help': "Use\n"
            f"/feedback [your message] - to report issues or get in contact with the team\n"
            f"/help - to show this info\n\n"
            f"Please use the feedback command or find the bot on GitHub "
            f"to report any issues, thanks a lot!",
    'welcome-bot': "Hi all! Please say hi to me so I am able to let others assign task to you!"
                   "Also, please make sure to add me as contact to allow me to interact with you and vice versa.",
    'user-welcome': lambda chat_title, name: f"Welcome to {chat_title}, {name}!",
    'user-goodbye': lambda name: f"Farewell, {name}!",
    'add-to-group': "Please add the bot to a group to get started!",
}
