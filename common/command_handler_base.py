import abc


class CommandHandlerBase(metaclass=abc.ABCMeta):

    admin_id: int
    texts: dict

    def __init__(self, admin_id, texts):
        self.admin_id = admin_id
        self.texts = texts

    def _is_admin(self, user_id):
        return self.admin_id and self.admin_id == user_id
