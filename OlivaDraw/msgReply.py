# -*- encoding=utf8 -*-

import random
import os
import pathlib
import zipfile
import uuid

from PIL import Image
import requests

from OlivaDraw.config import *

command_dict = {}


def add_command(command):
    """ 命令的装饰器 """
    def add_func(func):
        command_dict[command] = func
    return add_func


def log(Proc, message, level=2):
    Proc.log(
        log_level=2,
        log_message=message,
        log_segment=[
            ('OlivaDraw', 'default'),
            ('Init', 'default')
        ]
    )


def request_get(url, type='content'):
    """使用get请求访问指定url"""
    headers = {
        "User-Agent": USER_AGENT,
    }
    try:
        response = requests.get(url, headers=headers, timeout=8)
        if response.status_code == 200 or response.status_code == 304:
            # response.encoding = 'utf-8'
            if type == 'text':
                return response.text
            elif type == 'json':
                return response.json()
            elif type == 'content':
                # 获取二进制数据
                return response.content
        else:
            return "request failed"
    except requests.RequestException:
        return "time out"
    except ValueError:
        return 'jsonify failed'


def download_card(Proc, type=1):
    card_path = 'cards' + str(type) + '.zip'
    card_save_path = SAVE_BASE_PATH + card_path
    card_extract_path = SAVE_BASE_PATH + 'card/cards' + str(type)

    # 创建多级目录
    if not pathlib.Path(card_extract_path).exists():
        pathlib.Path(card_extract_path).mkdir(parents=True)
    if not pathlib.Path(SAVE_BASE_PATH + 'tmp').exists():
        pathlib.Path(SAVE_BASE_PATH + 'tmp').mkdir(parents=True)
    if pathlib.Path(card_save_path).exists():
        return

    url = REQUEST_BASE_URL + card_path
    log(Proc, '正在下载抽卡资源包...')
    # 下载抽卡资源包并保存到本地
    res = request_get(url)
    if isinstance(res, str):
        log(Proc, '从 ' + url + ' 下载卡包失败，请手动下载解压放到以下目录 ' + card_extract_path)
    with open(card_save_path, 'wb') as f:
        f.write(res)

    # 解压到指定文件夹
    with zipfile.ZipFile(card_save_path) as zf:
        zf.extractall(card_extract_path)

    log(Proc, '下载抽卡资源包完成')


def concat_images(image_names, path, save_path, type):
    """ 拼接抽卡结果图片 """
    COL = [1, 5, 10, 3][type]
    ROW = [1, 2, 10, 3][type]
    UNIT_HEIGHT_SIZE = 900
    UNIT_WIDTH_SIZE = 600

    image_files = []
    for index in range(COL * ROW):
        image_files.append(Image.open(path + image_names[index]))
    target = Image.new('RGB', (UNIT_WIDTH_SIZE * COL, UNIT_HEIGHT_SIZE * ROW))
    for row in range(ROW):
        for col in range(COL):
            target.paste(image_files[COL * row + col], (UNIT_WIDTH_SIZE * col, UNIT_HEIGHT_SIZE * row))
    if COL == 10:
        # 修改图片尺寸
        target = target.resize((int(target.size[0] * 0.5), int(target.size[1] * 0.5)), Image.ANTIALIAS)
    target.save(save_path)


def get_image_names(path, type):
    """ 抽取指定数目的卡牌 """
    COL = [1, 5, 10][type]
    ROW = [1, 2, 10][type]
    image_names = os.listdir(path)
    selected_images = random.choices(image_names, k=COL*ROW)
    return selected_images


def generate_image(plugin_event, Proc, type):
    message = plugin_event.data.message
    try:
        # 获取抽卡类型
        card_type = int(message[2])
    except BaseException:
        return
    card_path = SAVE_BASE_PATH + 'card/cards' + str(card_type) + '/'
    if card_type > 0 and card_type < 8:
        # 获取图片保存绝对路径
        path = os.path.abspath(SAVE_BASE_PATH)
        pic_save_path = path + '/tmp/' + uuid.uuid4().hex + '.jpg'
        concat_images(get_image_names(card_path, type), card_path, pic_save_path, type)
        log(Proc, '图片生成成功')
        return SEND_PATH.format(pic_path=pic_save_path)


@add_command('单抽')
def single_draw(plugin_event, Proc):
    return generate_image(plugin_event, Proc, type=0)


@add_command('抽卡')
def single_draw(plugin_event, Proc):
    return generate_image(plugin_event, Proc, type=0)


@add_command('十连')
def dozen_draw(plugin_event, Proc):
    return generate_image(plugin_event, Proc, type=1)


@add_command('百连')
def dozen_draw(plugin_event, Proc):
    return generate_image(plugin_event, Proc, type=2)


def unity_init(plugin_event, Proc):
    if not os.path.exists(SAVE_BASE_PATH):
        os.mkdir(SAVE_BASE_PATH)
        log(Proc, '正在创建插件根目录')

    if not pathlib.Path(SAVE_BASE_PATH + 'card/'):
        pathlib.Path(SAVE_BASE_PATH + 'card/').mkdir()
        log(Proc, '正在创建插件卡牌目录')

    if not pathlib.Path(SAVE_BASE_PATH + 'tmp/'):
        pathlib.Path(SAVE_BASE_PATH + 'tmp/').mkdir(parents=True)
        log(Proc, '正在创建插件临时保存目录')

    download_card(Proc)


def unity_reply(plugin_event, Proc):
    message = plugin_event.data.message
    if len(message) < 3: return
    if message[:2] in ['单抽', '十连', '百连', '抽卡']:
        reply_msg = command_dict.get(message[:2])(plugin_event, Proc)
        plugin_event.reply(reply_msg)