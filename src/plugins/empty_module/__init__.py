import re
from nonebot.log import logger
from nonebot.rule import startswith
from nonebot import on_message, on_regex
from nonebot.adapters.onebot.v11 import Bot, Event, unescape

your_plugin_catcher = on_message(rule=startswith(("开头内容", "开头另一")))
reg = "^(?:开头内容)[:：，,\s]*([\S]*)[:：，,\s]*([\S]*)[\s]*$" # 例：两个参数，可无空格，不允许空行
reg = "^(?:开头内容)[:：，,\s]+([\S\s]+)$" # 例：一个参数，有空格，允许空行
# your_plugin_catcher = on_regex(reg)

@your_plugin_catcher.handle()
async def _(bot: Bot, event: Event):

    event_dict = event.dict()
    raw_msg = unescape(event_dict['raw_message'])
    # group_id = event_dict.get('group_id', None)
    # user_id = event.get_user_id()

    # raw_msg = unescape(str(event.get_message()))  # 和第一种一样，图片等会显示成 [CQ:xxx] 形式
    # raw_msg = unescape(event.get_plaintext())  # 去除所有 [CQ:xxx] 的形式

    content_list = re.findall(reg, raw_msg)[0]  # add [0] if multiple capture() in reg, otherwise do not!
    content = content_list[0].strip()

    # reply = f'哈哈这是{content}'
    # await your_plugin_catcher.send(reply)
    await your_plugin_catcher.finish()
