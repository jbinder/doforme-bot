from datetime import time

from telegram.ext import Dispatcher, CallbackQueryHandler
from telegram.ext.jobqueue import Days

from common.component_base import ComponentBase
from common.event_type import EventType
from components.doforme.doforme_command_handler import DoForMeCommandHandler


class DoForMeComponent(ComponentBase):

    command_handler: DoForMeCommandHandler

    def __init__(self, command_handler: DoForMeCommandHandler):
        super().__init__()
        self.command_handler = command_handler

    def init(self, dp: Dispatcher):
        cmd_handlers = [
            ('do', self.command_handler.do_select_chat, True),
            ('tasks', self.command_handler.tasks_show, False),
            ('stats', self.command_handler.stats_show, False),
            ('admin-stats', self.command_handler.admin_stats, False),
        ]
        super()._register_command_handlers(dp, cmd_handlers)

        dp.add_handler(CallbackQueryHandler(self.command_handler.inline_handler, pass_user_data=True))

        jobs = [
            (self.command_handler.job_daily_tasks_show_all, time(hour=5, minute=0)),
            (self.command_handler.job_daily_tasks_show_daily, time(hour=11, minute=0)),
            (self.command_handler.job_daily_tasks_show_daily, time(hour=17, minute=0)),
        ]
        [dp.job_queue.run_daily(callback, time=run_at) for (callback, run_at) in jobs]

        dp.job_queue.run_daily(self.command_handler.job_weekly_review, time(hour=18, minute=0), days=(Days.SUN,))

    def register_observer(self, event_type: EventType, observer: callable):
        raise NotImplementedError()
