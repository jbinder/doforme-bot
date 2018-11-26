class DfmMockbot:
    def getChat(self, chat_id, timeout=None, **kwargs):
        data = {'chat_id': chat_id, 'title': f"title {chat_id}"}
        return type('', (object,), data)()

    def getChatMember(self, chat_id, user_id, timeout=None, **kwargs):
        data = {'chat_id': chat_id, 'user_id': user_id, 'user': type('', (object,), {'name': f"user {user_id}"})()}
        return type('', (object,), data)()
