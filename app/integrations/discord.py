import httpx

from app.core.config import get_settings

settings = get_settings()


async def send_discord_message(message: str) -> None:
    async with httpx.AsyncClient() as client:
        response = await client.post(
            settings.discord_webhook_url,
            json={
                "content": message,
            },
        )

        response.raise_for_status()