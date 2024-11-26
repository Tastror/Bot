import re
from nonebot.log import logger
from nonebot.rule import startswith
from nonebot import on_message, on_regex
from nonebot.adapters.onebot.v11 import Bot, Event, unescape
from nonebot_plugin_hammer_core.util.message_factory import reply_text

from .codelogger import codelogger

regex_str = r"^(rs|rust|sh|bash|py|python|c|cc|cpp|c\+\+)[ \t]*\r?\n([\s\S]*)$";
code_catcher = on_regex(regex_str)


@code_catcher.handle()
async def _(bot: Bot, event: Event):

    event_dict = event.dict()
    raw_msg = unescape(event_dict['raw_message'])
    group_id = event_dict.get('group_id', None)
    user_id = event.get_user_id()

    codelogger.info("get message\n" + event.get_log_string())

    reg_find_list: list[tuple | str] = re.findall(regex_str, raw_msg)
    if not reg_find_list or len(reg_find_list) == 0:
        await code_catcher.finish()
    first_find_data: tuple | str = reg_find_list[0]
    language: str = first_find_data[0].strip()
    content: str = first_find_data[1].strip()

    if language in ["python", "py"]:
        from .pyrun import run_content_in_docker
    elif language in ["c++", "cpp", "cc", "c"]:
        from .cpprun import run_content_in_docker
    elif language in ["bash", "sh"]:
        from .shrun import run_content_in_docker
    elif language in ["rust", "rs"]:
        from .rustrun import run_content_in_docker

    res = run_content_in_docker(content)

    if res is not None and res != '':
        if len(res) + len(content) < 4500: # 4558:
            codelogger.info("send message\n" + res)
            await code_catcher.send(reply_text(res, event))
        else:
            codelogger.info("send message\n" + 'TooMuch')
            await code_catcher.send(reply_text("输出太多了！", event))
    else:
        codelogger.info("send message\n" + 'None')
        await code_catcher.send(reply_text("没有输出哦", event))

    await code_catcher.finish()
