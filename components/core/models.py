from datetime import datetime

from pony.orm import Required, Optional

from common.utils.db_tools import get_database, init_database

db = get_database()


class JobLog(db.Entity):
    job_id = Required(str)
    last_run = Optional(datetime)


init_database(db)
