import os
import socket
from logging import Logger

from utils.app_lock import AppLock


class SocketAppLock(AppLock):
    """Creates a lock file during the execution of a process."""

    lock_name: str
    logger: Logger

    def __init__(self, lock_name, logger):
        self.logger = logger
        self.lock_name = lock_name
        self.lock_socket = None

    def lock(self):
        """ Binds a socket.

        :returns True if binding was successful, False if not.
        """
        return self._set_locked()

    def unlock(self):
        """ Removes the lock file if exists. """
        self._set_unlocked()

    def _set_locked(self):
        try:
            self.lock_socket = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
            self.lock_socket.bind(os.path.join(os.getcwd(), self.lock_name))
            return True
        except socket.error:
            return False

    def _set_unlocked(self):
        raise NotImplementedError
