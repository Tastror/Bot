import re
from nonebot import on_message
from nonebot.rule import startswith
from nonebot.adapters.onebot.v11 import Bot, MessageEvent, Message, MessageSegment

echo_matcher = on_message(rule=startswith("echo"))

@echo_matcher.handle()
async def _(bot: Bot, event: MessageEvent):

    esc_raw_msg: str = event.get_raw_message()
    user_id: int = event.get_user_id()
    group_id: int | None = event.dict().get('group_id', None)

    content = re.findall(r'^echo[:：，,\s]*([\S\s]*)', esc_raw_msg)
    if content:
        await echo_matcher.send(
            MessageSegment.at(event.dict()['user_id']) +
            Message(f"{content[0]}")
        )
    await echo_matcher.finish()

"""
how to send messages?

1. nonebot.adapters.bot.send(event, message, **kwargs)
    await bot.send(
        message=A,
        # specify the group_id or user_id
        event=event_dict   or   group_id=group   or   user_id=qq
    )

2. nonebot.matcher.send(cls, message, **kwargs)
    await matcher.send(
        A   or   message=A
    )

A: Message
    "some messages"   or
    Message(a) + MessageSegment.xxx(b) + MessageSegment(a)   or
    [Message(a), MessageSegment.xxx(b), MessageSegment(a)]
    
    where a:
        "some messages"    or
        ("text", {"text": "some messages"})   (not recommand)   or
        ("at", {"qq": qq})   (not recommand)   or
        ...   or
        # from nonebot_plugin_hammer_core.util.message_factory import reply_text
        reply_text("some messages", event)
        

    where xxx, b:
        text, "some messages"   (recommand)   or
        at, qq   (recommand)   or
        image, "/image/path"   (recommand)   or
        ...

"""
