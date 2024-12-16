import re
from nonebot.log import logger
from nonebot.rule import startswith
from nonebot import on_message, on_regex
from nonebot.adapters.onebot.v11 import Bot, Event, MessageEvent, unescape
from nonebot_plugin_hammer_core.util.message_factory import reply_text

# (1) onebot.v11 adapter for nonebot 官方页面
#     https://onebot.adapters.nonebot.dev/docs/api/v11/event/
# (2) onebot.v11 message API
#     https://github.com/botuniverse/onebot-11/blob/master/event/message.md
# (3) onebot.v11 adapter for nonebot source code
#     https://github.com/nonebot/adapter-onebot/blob/master/nonebot/adapters/onebot/v11/event.py
# (4) 注意，任何 adapters 的 Event 都继承自 BaseEvent，代码如下
#     https://github.com/nonebot/nonebot2/blob/master/nonebot/internal/adapter/event.py
#     由于 BaseEvent 使用了 pydantic 的 BaseModel，所以诸如 .dict(), .json(), class-field 直接转化为 object-field 等操作都是可行的

# your_plugin_catcher = on_message(rule=startswith(("开头内容", "开头另一")))

reg = r"^(?:开头内容)[:：，,\s]*([\S]*)[:：，,\s]*([\S]*)"  # 例：0/1/2个参数, 可无分割符, 不允许空行
reg = r"^(?:开头内容)[:：，,\s]+([\S\s]+)$"  # 例：1个参数, 有分割符, 参数允许空行
reg = r"^(?:开头内容)[:：，,\s]+([\S]+)[:：，,\s]+([\S\s]+)$"  # 例：2个参数, 有分割符, 第二个参数允许空行
your_plugin_catcher = on_regex(reg)

@your_plugin_catcher.handle()
async def _(bot: Bot, event: Event):

    raw_msg: str = unescape(event.raw_message)
    user_id: int = event.get_user_id()
    group_id: int | None = event.dict().get('group_id', None)  # may not have get_group_id() attribute, so use this

    # raw_msg = unescape(str(event.get_message()))  # 和第一种一样, 图片等会显示成 [CQ:xxx] 形式
    # raw_msg = unescape(event.get_plaintext())  # 去除所有 [CQ:xxx] 的形式

    reg_find_list: list[tuple | str] = re.findall(reg, raw_msg)
    if not reg_find_list or len(reg_find_list) == 0:
        await your_plugin_catcher.finish()
    first_find_data: tuple | str = reg_find_list[0]
    content_0: str = first_find_data[0].strip()  # >= 2
    content_1: str = first_find_data[1].strip()  # >= 2
    # content_0: str = first_find_data.strip()  # == 1 or no

    # 如果 reg 中捕获数大于等于 2, reg_find_list 会形如 [(res1, res2, ...), (res1, res2, ...), ...]
    # 如果 reg 中捕获数为 1, reg_find_list 会形如 [res1, res1, ...]
    # 如果 reg 中没有捕获, reg_find_list 会形如 [res_all, res_all, ...]

    res = f'哈哈，{content_0}, {content_1}'

    # await your_plugin_catcher.send(res)  # 普通消息
    # await your_plugin_catcher.send(reply_text(res, event))  # 回复性消息

    await your_plugin_catcher.finish()
