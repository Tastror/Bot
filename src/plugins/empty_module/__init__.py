import re
from nonebot.log import logger
from nonebot.rule import startswith
from nonebot import on_message, on_regex
from nonebot.adapters.onebot.v11 import Bot, Event, MessageEvent, unescape
from nonebot_plugin_hammer_core.util.message_factory import reply_text


reg = r"^(?:开头内容)[:：，,\s]*([\S]*)[:：，,\s]*([\S]*)"
reg = r"^(?:开头内容)[:：，,\s]+([\S\s]+)$"
reg = r"^(?:开头内容)[:：，,\s]+([\S]+)[:：，,\s]+([\S\s]+)$"
your_plugin_catcher = on_regex(reg)

@your_plugin_catcher.handle()
async def _(bot: Bot, event: Event):

    raw_msg: str = unescape(event.raw_message)
    user_id: int = event.user_id
    group_id: int | None = event.dict().get('group_id', None)

    reg_find_list: list[tuple | str] = re.findall(reg, raw_msg)
    if not reg_find_list or len(reg_find_list) == 0:
        await your_plugin_catcher.finish()
    first_find_data: tuple | str = reg_find_list[0]
    content_0: str = first_find_data[0].strip()  # >= 2
    content_1: str = first_find_data[1].strip()  # >= 2
    # content_0: str = first_find_data.strip()  # == 1 or no

    res = f'哈哈，{content_0}, {content_1}'

    # await your_plugin_catcher.send(res)
    # await your_plugin_catcher.send(reply_text(res, event))

    await your_plugin_catcher.finish()
