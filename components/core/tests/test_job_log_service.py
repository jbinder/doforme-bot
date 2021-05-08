import os
import unittest
from datetime import datetime, timedelta
from unittest import mock

from pony.orm import Database, commit, db_session

from components.core.models import JobLog


class TestJobLogService(unittest.TestCase):

    job1_id: str
    db: Database

    @mock.patch.dict(os.environ, {'DFM_ENV': 'Test'})
    def setUp(self):
        from components.core.models import db
        from components.core.job_log_service import JobLogService
        self.service = JobLogService()
        self.job1_id = "job1"
        db.drop_all_tables(with_all_data=True)
        db.create_tables()
        self.db = db

    def tearDown(self):
        pass

    @db_session
    def test_update_job_log_if_not_exists(self):
        job_log = JobLog.get(job_id=self.job1_id)
        self.assertIsNone(job_log)
        self.service.update_job_log(self.job1_id)
        job_log = JobLog.get(job_id=self.job1_id)
        self.assertIsNotNone(job_log)
        self.assertIsNotNone(job_log.last_run)
        self.assertTrue(job_log.last_run > (datetime.utcnow() - timedelta(minutes=1)))

    @db_session
    def test_update_job_log_if_exists(self):
        job_log = JobLog(job_id=self.job1_id, last_run=datetime.utcnow() - timedelta(minutes=10))
        commit()
        self.service.update_job_log(self.job1_id)
        job_log = JobLog.get(job_id=self.job1_id)
        self.assertTrue(job_log.last_run > (datetime.utcnow() - timedelta(minutes=1)))

    def test_has_run_recently_not_yet_run(self):
        self.assertFalse(self.service.has_run_recently(self.job1_id))

    def test_has_run_recently_recently_run(self):
        self.service.update_job_log(self.job1_id)
        self.assertTrue(self.service.has_run_recently(self.job1_id))

    @db_session
    def test_has_run_recently_not_recent_run(self):
        job_log = JobLog(job_id=self.job1_id, last_run=datetime.utcnow() - timedelta(minutes=10))
        commit()
        self.assertFalse(self.service.has_run_recently(self.job1_id))


if __name__ == '__main__':
    unittest.main()
