'''
Author       : Lancercmd
Date         : 2020-12-14 13:29:38
LastEditors  : Lancercmd
LastEditTime : 2021-07-19 07:52:15
Description  : None
GitHub       : https://github.com/Lancercmd
'''
from binascii import b2a_base64
from copy import deepcopy
from hashlib import sha1
from hmac import new
from random import randint
from sys import maxsize, version_info
from time import time
import re

from aiohttp import request
from loguru import logger
from nonebot import get_driver
from nonebot.adapters import Bot, Event
from nonebot.adapters.onebot.v11 import unescape, GroupMessageEvent, MessageEvent, PrivateMessageEvent
from nonebot_plugin_hammer_core.util.message_factory import reply_text
from nonebot.exception import ActionFailed
from nonebot.permission import Permission
from nonebot.plugin import on_command
from nonebot.typing import T_State

try:
    import ujson as json
except ImportError:
    import json

config = get_driver().config
this_plugin_name = "翻译"
slow_translate = on_command('自定义翻译', block=True)
fast_translate = on_command("翻译")


@slow_translate.permission_updater
async def _(bot: Bot, event: Event, state: T_State):
    message_type = event.message_type
    user_id = event.get_user_id()
    group_id = None
    if isinstance(event, GroupMessageEvent):
        group_id = event.group_id

    async def _onFocus(bot: Bot, event: Event):
        if isinstance(event, GroupMessageEvent):
            return event.message_type == message_type and event.get_user_id() == user_id and event.group_id == group_id
        elif isinstance(event, PrivateMessageEvent):
            return event.message_type == message_type and event.get_user_id() == user_id
    return Permission(_onFocus)


async def getReqSign(params: dict) -> str:
    common = {
        'Action': 'TextTranslate',
        'Region': f'{config.tencentcloud_common_region}',
        'Timestamp': int(time()),
        'Nonce': randint(1, maxsize),
        'SecretId': f'{config.tencentcloud_common_secretid}',
        'Version': '2018-03-21',
    }
    params.update(common)
    sign_str = 'POSTtmt.tencentcloudapi.com/?'
    sign_str += '&'.join('%s=%s' % (k, params[k]) for k in sorted(params))
    secret_key = config.tencentcloud_common_secretkey
    if version_info[0] > 2:
        sign_str = bytes(sign_str, 'utf-8')
        secret_key = bytes(secret_key, 'utf-8')
    hashed = new(secret_key, sign_str, sha1)
    signature = b2a_base64(hashed.digest())[:-1]
    if version_info[0] > 2:
        signature = signature.decode()
    return signature


@fast_translate.handle()
async def _(bot: Bot, event: Event, state: T_State):

    plain_text = event.get_plaintext().strip()
    user_id: int = event.user_id
    group_id: int | None = event.dict().get('group_id', None)

    res_list = re.findall(r'^(?:翻译)\s*(zh|en|ja|ko|fr|es|it|de|tr|ru|pt|vi|id|th|ms|ar|hi|)(\s*)([\s\S]*)', plain_text)[0]
    target_language: str = res_list[0]
    apart: str = res_list[1]
    source_text: str = res_list[2]

    if apart == '' and ('a' <= source_text[0] <= 'z'):
        source_text = target_language + source_text
        target_language = ''

    state['Source'] = 'auto'
    state['Target'] = target_language if target_language != '' else 'zh'
    if not source_text:
        await fast_translate.send(reply_text("请输入要翻译的内容", event))
    else:
        state['SourceText'] = source_text
        await go_trans(bot, event, state)


@slow_translate.handle()
async def _(bot: Bot, event: Event, state: T_State):

    if isinstance(event, MessageEvent):
        available = [
            'auto',
            'zh', 'zh-TW', 'en', 'ja', 'ko', 'fr',
            'es', 'it', 'de', 'tr', 'ru', 'pt',
            'vi', 'id', 'th', 'ms', 'ar', 'hi'
        ]
        state['available'] = ' | '.join(available)
        state['valid'] = deepcopy(available)
        if event.get_plaintext():
            for language in available:
                if event.get_plaintext().startswith(language):
                    state['Source'] = language
                    break
            if 'Source' in state:
                input = event.get_plaintext().split(' ', 2)
                available.remove('auto')
                available.remove('zh-TW')
                if state['Source'] == 'zh-TW':
                    available.remove('zh')
                if state['Source'] != 'en':
                    for i in ['ar', 'hi']:
                        available.remove(i)
                if not state['Source'] in ['zh', 'zh-TW', 'en']:
                    for i in ['vi', 'id', 'th', 'ms']:
                        available.remove(i)
                if state['Source'] in ['ja', 'ko', 'vi', 'id', 'th', 'ms', 'ar', 'hi']:
                    for i in ['fr', 'es', 'it', 'de', 'tr', 'ru', 'pt']:
                        available.remove(i)
                if not state['Source'] in ['zh', 'zh-TW', 'en', 'ja', 'ko']:
                    for i in ['ja', 'ko']:
                        available.remove(i)
                if state['Source'] in ['ar', 'hi']:
                    available.remove('zh')
                try:
                    available.remove(state['Source'])
                except ValueError:
                    pass
                if len(available) == 1:
                    state['Target'] = available[0]
                    if len(input) == 3:
                        state['SourceText'] = input[2]
                    else:
                        state['SourceText'] = input[1]
                elif len(input) == 3:
                    state['Target'] = input[1]
                    state['SourceText'] = input[2]
                elif len(input) == 2:
                    for language in available:
                        if input[0] in available:
                            state['Target'] = input[1]
                        else:
                            state['SourceText'] = input[1]
            else:
                # state['SourceText'] = event.get_plaintext()
                pass
        message = f'请选择输入语种，可选值如下~\n{state["available"]}'
        if 'header' in state:
            message = ''.join([state['header'], f'{message}'])
        state['prompt'] = message
        if 'Source' not in state:
            await slow_translate.send(reply_text(message, event))
    else:
        logger.warning('Not supported: translator')
        return

@slow_translate.got('Source')
async def _(bot: Bot, event: Event, state: T_State):
    if isinstance(event, MessageEvent):
        available = deepcopy(state['valid'])
        state['Source'] = unescape(event.raw_message)
        if state['Source'].lower() == 'jp':
            state['Source'] = 'ja'
        elif not state['Source'] in state['valid']:
            message = f'不支持的输入语种 {state["Source"]}'
            if 'header' in state:
                message = ''.join([state['header'], f'{message}'])
            try:
                await slow_translate.send(reply_text(message, event))
                await slow_translate.finish()
            except ActionFailed as e:
                logger.error(
                    f'ActionFailed | {e.info["msg"].lower()} | retcode = {e.info["retcode"]} | {e.info["wording"]}'
                )
                return
        available.remove('zh-TW')
        if state['Source'] == 'zh-TW':
            available.remove('zh')
        if state['Source'] != 'en':
            for i in ['ar', 'hi']:
                available.remove(i)
        if not state['Source'] in ['zh', 'zh-TW', 'en']:
            for i in ['vi', 'id', 'th', 'ms']:
                available.remove(i)
        if state['Source'] in ['ja', 'ko', 'vi', 'id', 'th', 'ms', 'ar', 'hi']:
            for i in ['fr', 'es', 'it', 'de', 'tr', 'ru', 'pt']:
                available.remove(i)
        if not state['Source'] in ['zh', 'zh-TW', 'en', 'ja', 'ko']:
            for i in ['ja', 'ko']:
                available.remove(i)
        if state['Source'] in ['ar', 'hi']:
            available.remove('zh')
        try:
            available.remove(state['Source'])
        except ValueError:
            pass
        if len(available) == 1:
            state['Target'] = available[0]
        else:
            state['available'] = ' | '.join(available)
            state['valid'] = deepcopy(available)
        message = f'请选择目标语种，可选值如下~\n{state["available"]}'
        if 'header' in state:
            message = ''.join([state['header'], f'{message}'])
        state['prompt'] = message
        await slow_translate.send(reply_text(message, event))
    else:
        logger.warning('Not supported: translator')
        return


@slow_translate.got('Target')
async def _(bot: Bot, event: Event, state: T_State):
    if isinstance(event, MessageEvent):
        state['Target'] = unescape(event.raw_message)
        if state['Target'].lower() == 'jp':
            state['Target'] = 'ja'
        elif not state['Target'] in state['valid']:
            message = f'不支持的目标语种 {state["Target"]}'
            if 'header' in state:
                message = ''.join([state['header'], f'{message}'])
            try:
                await slow_translate.send(reply_text(message, event))
                await slow_translate.finish()
            except ActionFailed as e:
                logger.error(
                    f'ActionFailed | {e.info["msg"].lower()} | retcode = {e.info["retcode"]} | {e.info["wording"]}'
                )
                return
        message = '请输入要翻译的内容~'
        if 'header' in state:
            message = ''.join([state['header'], f'{message}'])
        state['prompt'] = message
        await slow_translate.send(reply_text(message, event))
    else:
        logger.warning('Not supported: translator')
        return


@slow_translate.got('SourceText')
@fast_translate.got('SourceText')
async def go_trans(bot: Bot, event: Event, state: T_State):
    if isinstance(event, MessageEvent):
        # state['SourceText'] = unescape(event.raw_message)
        endpoint = 'https://tmt.tencentcloudapi.com'
        params = {
            'Source': state['Source'],
            'SourceText': state['SourceText'],
            'Target': state['Target'],
            'ProjectId': 0,
        }
        params['Signature'] = await getReqSign(params)
        async with request(
            'POST',
            endpoint,
            data=params
        ) as resp:
            code = resp.status
            if code != 200:
                message = '网络异常，请稍后再试~'
                if 'header' in state:
                    message = ''.join([state['header'], f'{message}'])
                try:
                    await slow_translate.send(reply_text(message, event))
                    await slow_translate.finish()
                except ActionFailed as e:
                    logger.error(
                        f'ActionFailed | {e.info["msg"].lower()} | retcode = {e.info["retcode"]} | {e.info["wording"]}'
                    )
                    return
            data = json.loads(await resp.read())['Response']
        if 'Error' in data:
            message = '\n'.join([
                f'<{data["Error"]["Code"]}> {data["Error"]["Message"]}',
                f'RequestId: {data["RequestId"]}'
            ])
            if 'header' in state:
                message = ''.join([state['header'], f'{message}'])
            try:
                await slow_translate.send(reply_text(message, event))
                await slow_translate.finish()
            except ActionFailed as e:
                logger.error(
                    f'ActionFailed | {e.info["msg"].lower()} | retcode = {e.info["retcode"]} | {e.info["wording"]}'
                )
                return
        message = data['TargetText']
        if 'header' in state:
            message = ''.join([state['header'], f'{message}'])
        try:
            await slow_translate.send(reply_text(message, event))
            await slow_translate.finish()
        except ActionFailed as e:
            logger.error(
                f'ActionFailed | {e.info["msg"].lower()} | retcode = {e.info["retcode"]} | {e.info["wording"]}'
            )
            return
    else:
        logger.warning('Not supported: translator')
        return
