import asyncio
import socket
from datetime import UTC, datetime, timedelta
from typing import Callable

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.schedulers.background import BackgroundScheduler
from loguru import logger


class BaseManager:
    def __init__(self):
        self.host = socket.gethostname()
        self.asyncio_scheduler = AsyncIOScheduler()
        self.backgroup_scheduler = BackgroundScheduler()

    async def start(self):
        self.asyncio_scheduler.start()
        self.backgroup_scheduler.start()

    async def stop(self):
        logger.info("shutdown scheduler")
        await asyncio.to_thread(self.asyncio_scheduler.pause)
        await asyncio.to_thread(self.backgroup_scheduler.pause)
        await asyncio.to_thread(self.asyncio_scheduler.shutdown)
        await asyncio.to_thread(self.backgroup_scheduler.shutdown)

    def run_background_job(
        self,
        func: Callable,
        args: tuple | None = None,
        kwargs: dict | None = None,
        id: str | None = None,
        name: str | None = None,
    ):
        logger.info("run background job: {}", func)
        self.backgroup_scheduler.add_job(
            func,
            args=args,
            kwargs=kwargs,
            id=id,
            name=name,
            next_run_time=datetime.now(UTC) + timedelta(seconds=1),
        )
