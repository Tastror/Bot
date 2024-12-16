# Readme for Plugins

## Message Event (onebot-v11)

```python
# class MessageEvent(Event)
# https://github.com/nonebot/adapter-onebot/blob/master/nonebot/adapters/onebot/v11/event.py


# it used pydantic's BaseModel in BaseModel in BaseEvent, so you can use
event.dict()
event.user_id
event.raw_message
...

event.dict() == {

    # MessageEvent
    'time': 1600000000,
    'self_id': 123456789,
    'post_type': 'message',
    'sub_type': 'normal',
    'user_id': 1234567,
    'message_type': 'group',
    'message_id': -1479544568,  # can be negative or positive
    'message': [MessageSegment(type='text', data={'text': '你好'})],
    'original_message': [MessageSegment(type='text', data={'text': '你好'})],
    'raw_message': '你好',
    'font': 0,
    'sender': {'user_id': 1234567, 'nickname': 'QAQ', 'sex': 'unknown', 'age': 0, 'card': '', 'area': '', 'level': '', 'role': 'owner', 'title': ''},
    'to_me': False,  # always true if message_type == "private"; if reply (not @) the bot then true otherwise false if message_type == "group"
    'reply': None,  # if has reply, raw_message will look like "[CQ:reply,id=123123123][CQ:at,qq=1234567] 消息内容"
                    # no @ here, if has a real @ with no space after it, it will become "[CQ:reply,...][CQ:at,...] [CQ:at,...]消息内容"

    # PrivateMessageEvent
    'target_id': 7654321,  # receiver's qq

    # GroupMessageEvent
    'group_id': 12345678, 
    'anonymous': None,
    'message_seq': 7442
}
```

note that nonebot offers you another API

```python
event.get_plaintext()
```

for the text only

## Send Message (onebot-v11)

how to send messages?

```plaintext
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
```
