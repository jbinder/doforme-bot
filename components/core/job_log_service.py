from datetime import datetime, timedelta

from pony.orm import commit, db_session, select

from components.core.models import JobLog, db
from common.decorators.db_use_utf8mb import db_use_utf8mb


class JobLogService:
    @db_session
    @db_use_utf8mb(db)
    def update_job_log(self, job_id):
        """ Updates the last run datetime of a specific job """
        job_log = JobLog.get(job_id=job_id)
        if not job_log:
            job_log = JobLog(job_id=job_id)
        job_log.last_run = datetime.utcnow()
        commit()

    @db_session
    @db_use_utf8mb(db)
    def has_run_recently(self, job_id, recent_minutes=5):
        """ :returns True if specified job has been run in the last recent_minutes minutes, False if not """
        job_log = JobLog.get(job_id=job_id)
        if not job_log:
            return False
        return job_log.last_run > (datetime.utcnow() - timedelta(minutes=recent_minutes))
