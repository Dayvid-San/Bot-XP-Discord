
import asyncio
import json
import logging
from pathlib import Path
import discord
from discord.ext import commands
from fastapi import FastAPI, Request, HTTPException
import uvicorn
import aiohttp

# --- Configuration ---
DISCORD_BOT_TOKEN = "YOUR_DISCORD_BOT_TOKEN"
CLICKUP_API_TOKEN = "YOUR_CLICKUP_API_TOKEN"
DISCORD_SERVER_ID = 123456789012345678 # Replace with your Discord Server ID
NOTIFICATION_CHANNEL_ID = 123456789012345678 # Replace with your notification channel ID

# --- XP and Role Mapping ---
XP_LEVELS = {
    "urgent": 100,
    "high": 70,
    "normal": 40,
    "low": 20,
    "none": 10
}

ROLE_LEVELS = {
    500: "Novice",
    1000: "Active Member",
    2000: "Elite"
}

# --- File Paths ---
USERS_MAP_FILE = Path("users_map.json")
DB_FILE = Path("db.json")

# --- Logging ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Data Manager ---
class DataManager:
    def __init__(self, file_path):
        self.file_path = file_path
        self.lock = asyncio.Lock()

    async def read_data(self):
        async with self.lock:
            if not self.file_path.exists():
                return {}
            with open(self.file_path, "r") as f:
                return json.load(f)

    async def write_data(self, data):
        async with self.lock:
            with open(self.file_path, "w") as f:
                json.dump(data, f, indent=4)

users_map_manager = DataManager(USERS_MAP_FILE)
db_manager = DataManager(DB_FILE)

# --- Discord Bot ---
intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)

# --- FastAPI App ---
app = FastAPI()

# --- ClickUp API ---
async def get_clickup_task(task_id: str):
    url = f"https://api.clickup.com/api/v2/task/{task_id}"
    headers = {
        "Authorization": CLICKUP_API_TOKEN
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            if response.status == 200:
                return await response.json()
            else:
                logger.error(f"Failed to get ClickUp task: {response.status} {await response.text()}")
                return None

# --- Webhook Endpoint ---
@app.post("/webhook/clickup")
async def clickup_webhook(request: Request):
    try:
        data = await request.json()
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON")

    if data.get("event") == "taskStatusUpdate" and data.get("history_items"):
        history_item = data["history_items"][0]
        if history_item.get("after", {}).get("status") in ["complete", "closed"]:
            task_id = data["task_id"]
            task_data = await get_clickup_task(task_id)

            if not task_data:
                return {"status": "failed", "reason": "Could not fetch task details"}

            priority = task_data.get("priority", {}).get("priority", "none")
            xp_to_award = XP_LEVELS.get(priority.lower(), 10)
            task_name = task_data.get("name")

            for assignee in task_data.get("assignees", []):
                assignee_email = assignee.get("email")
                if assignee_email:
                    users_map = await users_map_manager.read_data()
                    discord_user_id = users_map.get(assignee_email)

                    if discord_user_id:
                        await award_xp(int(discord_user_id), xp_to_award, task_name)
    return {"status": "success"}

async def award_xp(user_id: int, xp: int, task_name: str):
    db = await db_manager.read_data()
    user_data = db.get(str(user_id), {"xp": 0})
    user_data["xp"] += xp
    db[str(user_id)] = user_data
    await db_manager.write_data(db)

    guild = bot.get_guild(DISCORD_SERVER_ID)
    if guild:
        member = guild.get_member(user_id)
        if member:
            await check_and_assign_role(member, user_data["xp"])
            notification_channel = guild.get_channel(NOTIFICATION_CHANNEL_ID)
            if notification_channel:
                await notification_channel.send(f"✅ {member.mention} completed \"{task_name}\" and earned {xp} XP!")
        else:
            logger.warning(f"User with ID {user_id} not found in the server.")
    else:
        logger.warning(f"Discord server with ID {DISCORD_SERVER_ID} not found.")


async def check_and_assign_role(member: discord.Member, current_xp: int):
    for xp_threshold, role_name in sorted(ROLE_LEVELS.items(), key=lambda item: item[0], reverse=True):
        if current_xp >= xp_threshold:
            role = discord.utils.get(member.guild.roles, name=role_name)
            if role and role not in member.roles:
                await member.add_roles(role)
                logger.info(f"Assigned '{role_name}' role to {member.display_name}")
                # Remove lower level roles if you want
            break


@bot.event
async def on_ready():
    logger.info(f"{bot.user} has connected to Discord!")


@bot.command()
@commands.has_permissions(administrator=True)
async def sync_levels(ctx):
    """Manually recalculates and assigns roles based on current XP."""
    db = await db_manager.read_data()
    guild = bot.get_guild(DISCORD_SERVER_ID)
    if not guild:
        await ctx.send("Discord server not found.")
        return

    for user_id_str, data in db.items():
        user_id = int(user_id_str)
        member = guild.get_member(user_id)
        if member:
            await check_and_assign_role(member, data["xp"])
    await ctx.send("Levels and roles have been synced.")


async def run_bot():
    try:
        await bot.start(DISCORD_BOT_TOKEN)
    except KeyboardInterrupt:
        await bot.close()


async def run_server():
    config = uvicorn.Config(app, host="0.0.0.0", port=8000, log_level="info")
    server = uvicorn.Server(config)
    await server.serve()


async def main():
    await asyncio.gather(
        run_bot(),
        run_server(),
    )


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Shutting down.")

