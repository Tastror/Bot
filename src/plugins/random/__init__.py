import re
import random
from nonebot.log import logger
from nonebot.rule import startswith
from nonebot import on_message, on_regex
from nonebot.adapters.onebot.v11 import Bot, Event, MessageEvent, unescape
from nonebot_plugin_hammer_core.util.message_factory import reply_text


random_reg = r"^(?:random|ran|随机数|随机)[:：，,\s]*(-?[\d]*)[:：，,\s]*(-?[\d]*)[\s]*$"
dies_reg = r"^[rR]?([\d]*)[dD]([\d]+)[\s]*$"

random_matcher = on_regex(random_reg)
dies_matcher = on_regex(dies_reg)


# 跑团专用
@dies_matcher.handle()
async def _(bot: Bot, event: MessageEvent):

    raw_msg: str = unescape(event.raw_message)
    user_id: int = event.user_id
    group_id: int | None = event.dict().get('group_id', None)

    content_list = list(re.findall(dies_reg, raw_msg))
    if len(content_list) == 0:
        await dies_matcher.finish()
        return
    content = list(content_list[0])
    # only two kinds:
    # ['', '12'] or ['2', '123']
    die_num = 1
    if content[0] != "":
        die_num = int(content[0])
    if die_num > 16:
        await dies_matcher.send(reply_text("骰子数量过多", event))
        await dies_matcher.finish()
        return
    if die_num <= 0:
        await dies_matcher.finish()
        return
    die_range = int(content[1])
    result = 0
    now_data = random.randint(1, die_range)
    reply = f"{now_data}"
    result += now_data
    for i in range(die_num - 1):
        now_data = random.randint(1, die_range)
        reply += f" + {now_data}"
        result += now_data
    if die_num >= 2:
        reply += f" = {result}"
    await dies_matcher.send(reply_text(reply, event))
    await dies_matcher.finish()


@random_matcher.handle()
async def _(bot: Bot, event: MessageEvent):

    raw_msg: str = unescape(event.raw_message)
    user_id: int = event.user_id
    group_id: int | None = event.dict().get('group_id', None)

    content_list = list(
        re.findall(random_reg, raw_msg)
    )
    if len(content_list) == 0:
        await random_matcher.finish()
        return
    content = list(content_list[0])

    if not content[0]:
        a, b = random.random() * 10, random.random() * 10
        if a != 0 and b != 0:
            await random_matcher.send(
                reply_text(
                    "{}{:.2f} {} {:.2f}i".format(
                        "" if (random.randint(0, 1) == 0) else "- ", a,
                        "+" if (random.randint(0, 1) == 0) else "-", b,
                    ),
                    event,
                )
            )
        elif a == 0 and b != 0:
            await random_matcher.send(
                reply_text(
                    "{}{:.2f}i".format("" if (random.randint(0, 1) == 0) else "- ", b),
                    event,
                )
            )
        elif a != 0 and b == 0:
            await random_matcher.send(
                reply_text(
                    "{}{:.2f}".format(
                        "" if (random.randint(0, 1) == 0) else "- ", a,
                    ),
                    event,
                )
            )
        else:
            await random_matcher.send(reply_text("0"), event)

    else:
        a = int(content[0])
        if not content[1]:
            if a >= 1:
                b = 1
            else:
                b = 0
        else:
            b = int(content[1])
        if a > b:
            a, b = b, a
        await random_matcher.send(reply_text(f"{random.randint(a, b)}", event))

    await random_matcher.finish()
