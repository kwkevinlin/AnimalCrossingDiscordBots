import aiohttp
import json
import logging
import os
import requests

from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
DISCORD_BOT_TOKEN = os.getenv("ACNH_BOT_TOKEN")
VILLAGER_DB_AUTOCOMPLETE_URL = "https://villagerdb.com/autocomplete"
VILLAGER_DB_ITEM_URL = "https://villagerdb.com/item"

bot = commands.Bot(command_prefix="!")

logging.basicConfig(
    level="INFO",
    format="[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s",
    datefmt="%H:%M:%S")
logger = logging.getLogger(__name__)


@bot.event
async def on_ready():
    logger.info("Started up %s", bot.user.name)
    logger.info("Bot running on servers: %s",
                ", ".join([guild.name for guild in bot.guilds]))


@bot.event
async def on_guild_join(guild):
    logger.info("Bot added to new server! Server name: %s", guild.name)


@bot.command(name="item", help="Responds with a link to the item in VillagerDB")
async def item_search(ctx, *item_name):
    if not item_name:
        await ctx.send(
            "Please specify an item name after the command, "
            "ex: `!item giant teddy bear`")
        return

    item_name = " ".join(item_name)

    async with aiohttp.ClientSession() as session:
        raw_response = await session.get(
            VILLAGER_DB_AUTOCOMPLETE_URL,
            params={"q": item_name})
        top_matches = await raw_response.json()

        if not top_matches:
            await ctx.send("No items found with that name")
            return

        if len(top_matches) > 1:
            similar_items = [x.lower() for x in top_matches[1:]]
            await ctx.send("Possible alternatives: {}".format(
                ", ".join(similar_items)))

        await ctx.send("{item_url}/{item_name}".format(
            item_url=VILLAGER_DB_ITEM_URL,
            item_name=top_matches[0].replace(" ", "-").lower()
        ))


bot.run(DISCORD_BOT_TOKEN)
