import abc


class MigrationHandlerBase(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def migrate_to_supergroup(self, chat_id: int, new_chat_id: int):
        """ Updates the database entries from group_id to supergroup_id. """
