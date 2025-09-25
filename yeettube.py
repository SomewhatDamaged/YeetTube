import logging
import os
import re
import sys
from typing import Tuple, Union

import discord
from redbot.core import Config, commands, data_manager
from yarl import URL

from .log_manager import add_logger, create_logging

# from .modals import *

log = create_logging("YeetTube")


class YeetTube(commands.Cog):
    """YeetTube creates a button in reply to Youtube links that have tracking BS. The
    button has no such dross.

    In server chat...
    Turn on: @<bot> enable yeettube
    Turn off: @<bot> disable yeettube"""

    url_regex = re.compile(
        r"https?:\/\/(?:www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,16}\b(?:[-a-zA-Z0-9()@:%_\+.,~#?&//=\[\]]*)",
        flags=re.IGNORECASE,
    )
    valid_keys = ["v", "t", "index", "list"]

    def __init__(self, bot: commands.Bot) -> None:
        """Initializes YeetTube."""
        self.bot_path = str(data_manager.cog_data_path(cog_instance=self))
        global log
        log.debug(f"{self.bot_path = }")
        log = add_logger(log, f"{self.bot_path}/YeetTube.log")
        if os.path.exists(self.bot_path + "/.istest"):
            log.setLevel(logging.DEBUG)
            log.debug("Logging: DEBUG")
        else:
            log.setLevel(logging.INFO)
            log.error("Logging: INFO")
        self.bot = bot
        self.config = Config.get_conf(self, identifier=0x98535937539)
        default_guild = {"mode": False}
        self.config.register_guild(**default_guild)

    @commands.Cog.listener()
    async def on_message(
        self,
        message: discord.Message,
    ) -> None:
        try:
            log.debug(f"{await self.config.guild(message.guild).mode() = }")
            if self.bot.user in message.mentions:
                log.debug(f"Might be config...\n{message.content = }")
                await self.do_config(message)
                return
            if not await self.config.guild(message.guild).mode():
                """Not enabled here!"""
                return
            if message.message_snapshots:
                log.debug("Is message reference")
                for forwarded_message in message.message_snapshots:
                    if forwarded_message.content:
                        message.content = forwarded_message.content
                        break
            log.debug(f"Might be url...\n{message.content = }")
            urls: list = self.url_regex.findall(message.content)
            if not urls:
                """Nothing to work on."""
                return
            log.debug(f"Urls found!\n{urls = }")
            buttons = []
            for url in urls:
                url: Union[URL, None] = URL(url)
                url, v = self.process_url(url)
                if url:
                    buttons.append(
                        discord.ui.Button(
                            label=v,
                            url=str(url),
                            style=discord.ButtonStyle.link,
                        ),
                    )
            if buttons:
                view = self.make_view(buttons)
                await message.reply(mention_author=False, silent=True, view=view)
        except Exception:
            exc_type, _, _ = sys.exc_info()
            log.exception(exc_type)

    def make_view(self, buttons: list[discord.ui.Button]) -> discord.ui.LayoutView:
        view = discord.ui.LayoutView()
        i = 1
        action_row = []
        for button in buttons:
            if i % 5 == 0:
                view.add_item(discord.ui.ActionRow(*action_row))
                action_row = []
            action_row.append(button)
            i += 1
        if action_row:
            view.add_item(discord.ui.ActionRow(*action_row))
        return view

    def process_url(self, url: URL) -> Tuple[Union[URL, None], Union[str, None]]:
        if not url.host.endswith("youtube.com") and not url.host.endswith("youtu.be"):
            return None, ""
        new_url = URL(url).with_query("")
        process = False
        v = "YeetTube"
        for key, value in url.query.items():
            log.debug(f"Key and value pairs in query:\n{key = }\n{value = }")
            if key not in self.valid_keys:
                process = True
                continue
            if key == "v":
                v = value
            new_url: URL = new_url.update_query(f"{key}={value}")
        if url.host.endswith("youtu.be"):
            v = url.path[1:]
        if "shorts" in url.path:
            v = url.path.rsplit("/", 1)[1]
        return new_url, v if process else None

    async def do_config(self, message: discord.Message) -> None:
        if "enable yeettube" in message.content.lower():
            if not await permission_check(message):
                return await message.reply(
                    "You do not have permission to do this (requires guild manager)."
                )
            if await self.config.guild(message.guild).mode():
                return await message.reply(
                    "YeetTube is already enabled on this server."
                )
            await self.config.guild(message.guild).mode.set(True)
            return await message.reply("YeetTube is now enabled on this server.")
        if "disable yeettube" in message.content.lower():
            if not await permission_check(message):
                return await message.reply(
                    "You do not have permission to do this (requires guild manager)."
                )
            if not await self.config.guild(message.guild).mode():
                return await message.reply(
                    "YeetTube is already disabled on this server."
                )
            await self.config.guild(message.guild).mode.set(False)
            return await message.reply("YeetTube is now disabled on this server.")


async def permission_check(message: discord.Message) -> bool:
    if message.channel.permissions_for(message.author).manage_guild:
        return True
    False
