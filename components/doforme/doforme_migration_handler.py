from pony.orm import select, commit, db_session

from common.decorators.db_use_utf8mb import db_use_utf8mb
from common.migration_handler_base import MigrationHandlerBase
from components.doforme.models import Task, db


class DoForMeMigrationHandler(MigrationHandlerBase):

    @db_session
    @db_use_utf8mb(db)
    def migrate_to_supergroup(self, chat_id: int, new_chat_id: int):
        # noinspection PyTypeChecker
        tasks = select(task for task in Task if task.chat_id == chat_id)[:]
        for task in tasks:
            task.chat_id = new_chat_id
        commit()

