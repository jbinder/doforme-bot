from components.core.job_log_service import JobLogService


class MockJobLogService(JobLogService):
    def update_job_log(self, job_id):
        pass

    def has_run_recently(self, job_id, recent_minutes=5):
        return False
