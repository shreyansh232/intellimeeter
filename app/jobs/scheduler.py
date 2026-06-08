from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.database.db import AsyncSessionLocal
from app.services.reminders import process_all_overdue_reminders

scheduler = AsyncIOScheduler()


async def reminder_job():
    async with AsyncSessionLocal() as db:
        await process_all_overdue_reminders(
            db=db,
        )


scheduler.add_job(
    reminder_job,
    trigger="interval",
    minutes=60,
)