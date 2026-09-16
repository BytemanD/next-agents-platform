import socket
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.schedulers.background import BackgroundScheduler


class BaseManager:
    def __init__(self):
        self.host = socket.gethostname()
        self.asyncio_scheduler = AsyncIOScheduler()
        self.backgroup_scheduler = BackgroundScheduler()

    def start(self):
        self.asyncio_scheduler.start()
        self.backgroup_scheduler.start()

    def stop(self):
        self.asyncio_scheduler.pause()
        self.backgroup_scheduler.pause()
        self.asyncio_scheduler.shutdown()
        self.backgroup_scheduler.shutdown()
