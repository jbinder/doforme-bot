import unittest
from telegram.ext import Updater
import ptbtest


class PtbTestCase(unittest.TestCase):

    def setUp(self):
        self.bot = ptbtest.Mockbot()
        self.ug = ptbtest.UserGenerator()
        self.cg = ptbtest.ChatGenerator()
        self.mg = ptbtest.MessageGenerator(self.bot)
        self.updater = Updater(bot=self.bot)
