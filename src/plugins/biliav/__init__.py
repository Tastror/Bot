import re
import asyncio

from nonebot.log import logger
from nonebot.adapters.onebot.v11 import Bot, Event
from nonebot import get_driver, on_regex
from nonebot.typing import T_State
from nonebot.params import T_State

from .bililogger import bililogger
from .data_source import get_abv_data

biliav = on_regex("[Aa][Vv]\d{1,12}|[Bb][Vv]1[A-Za-z0-9]{2}4.1.7[A-Za-z0-9]{2}|[Bb]23\.[Tt][Vv]/[A-Za-z0-9]{7}")

@biliav.handle()
async def handle(bot: Bot, event: Event, state: T_State):

    # event_dict = event.dict()
    # group_id = event_dict.get('group_id', None)
    # user_id = event.get_user_id()
    # raw_msg = event_dict['raw_message']

    raw_msg = str(event.get_message())

    abvcode_list: list[str] = re.compile(
        "[Aa][Vv]\d{1,12}|[Bb][Vv]1[A-Za-z0-9]{2}4.1.7[A-Za-z0-9]{2}|[Bb]23\.[Tt][Vv]/[A-Za-z0-9]{7}").findall(raw_msg)
    if not abvcode_list:
        return
    bililogger.debug(event.get_log_string())
    logger.debug("start matching biliav")
    rj_list: list[str] = await get_abv_data(abvcode_list)
    for rj in rj_list:
        await biliav.send(rj)
    if len(rj_list) == 0:
        logger.debug("no data in biliav")
    logger.debug("stop sending biliav")
    await biliav.finish()
