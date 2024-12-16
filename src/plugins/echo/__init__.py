import re
from nonebot import on_message
from nonebot.rule import startswith
from nonebot.adapters.onebot.v11 import Bot, MessageEvent, Message, MessageSegment

echo_matcher = on_message(rule=startswith("echo"))

@echo_matcher.handle()
async def _(bot: Bot, event: MessageEvent):

    esc_raw_msg: str = event.raw_message
    user_id: int = event.user_id
    group_id: int | None = event.dict().get('group_id', None)

    content = re.findall(r'^echo[:：，,\s]*([\S\s]*)', esc_raw_msg)
    if content:
        await echo_matcher.send(
            MessageSegment.at(user_id) +
            Message(f"{content[0]}")
        )
    await echo_matcher.finish()
