import asyncio
import socket
import threading
from collections.abc import Callable
from datetime import UTC, datetime, timedelta

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.date import BaseTrigger, DateTrigger
from loguru import logger
from pystonic.common import context


class BaseManager:
    def __init__(self):
        self.host = socket.gethostname()
        self.asyncio_scheduler = AsyncIOScheduler()
        self.backgroup_scheduler = BackgroundScheduler()
        self.shutdown_event = threading.Event()

    async def start(self):
        self.asyncio_scheduler.start()
        self.backgroup_scheduler.start()

    async def stop(self):
        self.shutdown_event.set()
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
        after_seconds: int = 0,
    ):
        logger.info("run background job: {}", func)
        self.backgroup_scheduler.add_job(
            func,
            trigger=DateTrigger(datetime.now(UTC) + timedelta(seconds=after_seconds)),
            args=args,
            kwargs=kwargs,
            id=id,
            name=name,
            max_instances=1,
        )

    def get_request_account(self):
        return context.account() or "guest"

    def add_async_job(
        self,
        trigger: BaseTrigger,
        func: Callable,
        args: tuple | None = None,
        kwargs: dict | None = None,
        id: str | None = None,
        name: str | None = None,
        max_instances: int = 1,
        coalesce=True,
    ):
        if max_instances <= 0:
            raise ValueError(
                f"max_instances must be a positive integer, got {max_instances}"
            )
        self.asyncio_scheduler.add_job(
            func,
            trigger=trigger,
            args=args,
            kwargs=kwargs,
            id=id,
            name=name,
            max_instances=max_instances,
            coalesce=coalesce,
        )
        logger.info("add sync job: {} with trigger: {}", func, trigger)
