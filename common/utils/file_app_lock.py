import os
import signal
from logging import Logger
from pathlib import Path

from common.utils.app_lock import AppLock


class FileAppLock(AppLock):
    """Creates a lock file during the execution of a process."""

    lock_name: str
    logger: Logger

    def __init__(self, lock_name, logger):
        self.logger = logger
        self.lock_name = lock_name

    def lock(self):
        """ Creates a lock file if not exists.

        The lock file is removed when the process is stopped or unlock is called.

        :returns True if the lockfile did not exist, False if the lockfile already existed.
        """
        if self._is_locked():
            return False
        self._set_locked()
        return True

    def unlock(self):
        """ Removes the lock file if exists. """
        self._set_unlocked()

    def _is_locked(self):
        return Path(self.lock_name).is_file()

    def _set_locked(self):
        open(self.lock_name, 'a').close()
        signal.signal(signal.SIGTERM, self._on_stop)
        signal.signal(signal.SIGINT, self._on_stop)

    # noinspection PyUnusedLocal
    def _on_stop(self, signum, frame):
        self._set_unlocked()

    def _set_unlocked(self):
        if self._is_locked():
            self.logger.info("Removing the lock file...")
            os.remove(self.lock_name)
        else:
            self.logger.info("The lock file already has been removed.")
