import re
import yaml
import httpx
import traceback
from openai import AsyncOpenAI
from nonebot.log import logger
from nonebot.rule import startswith
from nonebot import on_message, on_regex
from nonebot.adapters.onebot.v11 import Bot, Event, unescape
from nonebot_plugin_hammer_core.util.message_factory import reply_text
from datetime import datetime
from dateutil.relativedelta import relativedelta

from .gptlogger import gptlogger
from .status import get_status

def get_last_month_date():
    today = datetime.today()
    last_month_date = today - relativedelta(months=1)
    return last_month_date

reg = r"^gpt(s|c|h|g)?[ \t]*(?:\r?\n([\s\S]*))?$"
gpt_catcher = on_regex(reg)

with open("./src/plugins/chatgpt/gpt.yaml", 'r', encoding='utf-8') as file:
    yaml_read = yaml.safe_load(file.read())

history = dict()

@gpt_catcher.handle()
async def _(bot: Bot, event: Event):

    raw_msg: str = unescape(event.raw_message)
    user_id: int = event.user_id
    group_id: int | None = event.dict().get('group_id', None)

    guid = ("g" + str(group_id)) if group_id is not None else ("u" + str(user_id))

    name_prefix = (f"(message from qq={user_id}): ") if group_id is not None else ""
    history_prefix = ""
    history_used = False

    history.setdefault(guid, '')

    reg_find_list: list[tuple | str] = re.findall(reg, raw_msg)
    if not reg_find_list or len(reg_find_list) == 0:
        await gpt_catcher.finish()
    first_find_data: tuple | str = reg_find_list[0]
    mode: str = first_find_data[0].strip()  # >= 2
    content: str = first_find_data[1].strip()  # >= 2

    gptlogger.info("get message\n" + event.get_log_string() + "\nmethod (s|c|h|nothing): " + mode)

    if mode == "h":
        await gpt_catcher.send("gpth: 显示帮助\ngpt<换行>内容: 不使用历史记录\ngpts<换行>内容: 使用历史记录\ngptc<换行>内容: 清空历史且不使用历史记录\ngptg: 显示本群用量")

    if mode == "g" and group_id is not None:
        res1 = get_status(datetime.today().strftime('%Y-%m'), str(group_id))
        res2 = get_status(get_last_month_date().strftime('%Y-%m'), str(group_id))
        await gpt_catcher.send(f"本月用量: {res1}\n上月用量: {res2}")

    if content == "":

        if mode == "c":
            history[guid] = ''
            await gpt_catcher.send("历史记录已清除")

        else:
            pass

        await gpt_catcher.finish()

    else:

        if mode == "c":
            history_used = False
            history[guid] = ''
            history_prefix = "(历史记录已清除)\n"

        elif mode == "s":
            history_used = True

        elif mode == "":
            history_used = False
            history_prefix = "(本次无历史)\n"

        else:
            await gpt_catcher.finish()


    client = AsyncOpenAI(
        api_key=yaml_read['api_key'],
        base_url=yaml_read['base_url'],
        timeout=httpx.Timeout(120.0)
    )
    
    try:
        if history_used:

            completion = await client.chat.completions.create(
                model=yaml_read['model_name'],
                messages=[
                    {"role": "system", "content": "" + ("You are now talking with many people." if group_id is not None else "")},
                    {"role": "user", "content": "history message (may be cut):\n\n" + history[guid] + "\n\ncurrent message:\n\n" + name_prefix + content}
                ],
            )

        else:

            completion = await client.chat.completions.create(
                model=yaml_read['model_name'],
                messages=[
                    {"role": "user", "content": content}
                ],
            )

    except Exception as e:
        gptlogger.error("send message to\n" + event.get_log_string() + "\n" + str(e) + "\n" + traceback.format_exc())
        await gpt_catcher.send(reply_text(f"网络不畅，请稍后重试。\n错误内容: {e}", event))
        await gpt_catcher.finish()

    result = completion.choices[0].message.content
    history[guid] += name_prefix + content + "\n\n\n" + result + "\n\n\n"
    history[guid] = history[guid][-2000:]

    gptlogger.info("send message to\n" + event.get_log_string() + "\n" + history_prefix + result)
    await gpt_catcher.send(reply_text(history_prefix + result, event))
    await gpt_catcher.finish()
