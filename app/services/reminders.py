from collections import defaultdict

from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import ReminderLog, ReminderStatus, User
from app.integrations.discord import send_discord_message
from app.services.action_items import (
    get_all_overdue_action_items,
    get_overdue_action_items,
)


async def process_overdue_reminders(
    db: AsyncSession,
    current_user: User,
):
    overdue_items = await get_overdue_action_items(
        db=db,
        current_user=current_user,
    )

    await _send_reminders(
        db=db,
        overdue_items=overdue_items,
        trace_id="manual-reminder-job",
    )


async def process_all_overdue_reminders(
    db: AsyncSession,
):
    overdue_items = await get_all_overdue_action_items(
        db=db,
    )

    await _send_reminders(
        db=db,
        overdue_items=overdue_items,
        trace_id="scheduler",
    )


async def _send_reminders(
    db: AsyncSession,
    overdue_items,
    trace_id: str,
):
    grouped = defaultdict(list)

    for item in overdue_items:
        if item.assignee_email:
            grouped[item.assignee_email].append(item)

    for assignee_email, items in grouped.items():
        try:
            lines = [
                "Overdue Action Items:",
                "",
                f"Assignee: {assignee_email}",
                "",
                "Tasks:",
            ]

            for item in items:
                lines.append(f"• {item.task}")

            message = "\n".join(lines)

            await send_discord_message(message)

            for item in items:
                db.add(
                    ReminderLog(
                        action_item_id=item.id,
                        status=ReminderStatus.SUCCESS.value,
                        trace_id=trace_id,
                    )
                )

        except Exception as e:
            for item in items:
                db.add(
                    ReminderLog(
                        action_item_id=item.id,
                        status=ReminderStatus.FAILED.value,
                        trace_id=trace_id,
                        error_message=str(e),
                    )
                )

    await db.commit()