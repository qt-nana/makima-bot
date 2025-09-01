import os
import json
import time
import aiohttp
import random
import asyncio
import logging
import requests
import threading

from http.server import (
    HTTPServer,
    BaseHTTPRequestHandler
)

from dotenv import (
    load_dotenv
)

from aiogram import (
    F,
    Bot,
    Dispatcher
)
from aiogram.enums import (
    ParseMode,
    ChatAction
)
from aiogram.filters import (
    Command
)
from aiogram.types import (
    Message,
    BotCommand,
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InputMediaPhoto,
    InputMediaVideo,
    InputMediaAnimation
)
from aiogram.client.default import (
    DefaultBotProperties
)
import aiogram.types as types

import xml.etree.ElementTree as ET

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
TELEGRAM_API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

R34_API_KEY = os.getenv("R34_API_KEY")
R34_USER_ID = int(os.getenv("R34_USER_ID", "0"))

OWNER_ID = 5290407067
help_page_states = {}

RULE34_API_BASE = "https://api.rule34.xxx/index.php"

sent_content_ids = set()
user_offsets = {}
MAX_CONTENT_CACHE = 10000
api_request_times = []
MAX_REQUESTS_PER_MINUTE = 60

privacy_mode = "normal"

logger = logging.getLogger("makimabot")
logger.setLevel(logging.INFO)

for handler in logger.handlers[:]:
    logger.removeHandler(handler)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(logging.Formatter("%(asctime)s | %(levelname)s | %(message)s"))

logger.addHandler(console_handler)

logger.propagate = False


if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN environment variable is required")

if not R34_API_KEY:
    raise ValueError("R34_API_KEY environment variable is required")

if not R34_USER_ID:
    raise ValueError("R34_USER_ID environment variable is required")

bot = Bot(token=str(BOT_TOKEN), default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

class DummyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is alive!")

    def do_HEAD(self):
        self.send_response(200)
        self.end_headers()

def check_membership(user_id):
    """Check if user is a member of required channel and group"""
    try:
        channel_url = f"{TELEGRAM_API_URL}/getChatMember"
        channel_data = {"chat_id": "@WorkGlows", "user_id": user_id}
        channel_response = requests.post(channel_url, json=channel_data, timeout=10)

        group_url = f"{TELEGRAM_API_URL}/getChatMember"
        group_data = {"chat_id": "-1002186262653", "user_id": user_id}
        group_response = requests.post(group_url, json=group_data, timeout=10)

        if channel_response.status_code == 200 and group_response.status_code == 200:
            channel_member = channel_response.json().get("result", {})
            group_member = group_response.json().get("result", {})

            valid_statuses = ["member", "administrator", "creator"]

            channel_joined = channel_member.get("status") in valid_statuses
            group_joined = group_member.get("status") in valid_statuses

            logger.debug(f"💖 Membership check for {user_id}: Channel={channel_joined}, Group={group_joined}")
            return channel_joined and group_joined
        else:
            logger.warning(f"⚠️ Failed to check membership for user {user_id}")
            return False

    except Exception as e:
        logger.error(f"❌ Error checking membership: {e}")
        return False

def should_check_membership(user_id):
    """Check if membership verification is required based on privacy mode"""
    global privacy_mode

    if user_id == OWNER_ID:
        return False

    if privacy_mode == "public":
        return False

    return True

async def send_membership_reminder(chat_id, user_id, user_name):
    """Send cute reminder about joining required channel and group"""

    user_mention = f'<a href="tg://user?id={user_id}"><b>{user_name}</b></a>'

    reminder_message = f"""
🌺 <b>Hey {user_mention}, Glad to see you!</b>

I'm <b>Makima</b>, but I only play with those who join our <b>lovely family!</b> 💖

<blockquote><i>✨ Join our <b>special places</b>. Tap below and come find me! 💕</i></blockquote>
"""

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="💟 Our Channel", url="https://t.me/WorkGlows"),
            InlineKeyboardButton(text="Our Group 💞", url="https://t.me/SoulMeetsHQ")
        ],
        [
            InlineKeyboardButton(text="💗️ Joined Both 💗", callback_data="check_membership")
        ]
    ])

    image_urls = [
    "https://ik.imagekit.io/asadofc/Images1.png",
    "https://ik.imagekit.io/asadofc/Images2.png",
    "https://ik.imagekit.io/asadofc/Images3.png",
    "https://ik.imagekit.io/asadofc/Images4.png",
    "https://ik.imagekit.io/asadofc/Images5.png",
    "https://ik.imagekit.io/asadofc/Images6.png",
    "https://ik.imagekit.io/asadofc/Images7.png",
    "https://ik.imagekit.io/asadofc/Images8.png",
    "https://ik.imagekit.io/asadofc/Images9.png",
    "https://ik.imagekit.io/asadofc/Images10.png",
    "https://ik.imagekit.io/asadofc/Images11.png",
    "https://ik.imagekit.io/asadofc/Images12.png",
    "https://ik.imagekit.io/asadofc/Images13.png",
    "https://ik.imagekit.io/asadofc/Images14.png",
    "https://ik.imagekit.io/asadofc/Images15.png",
    "https://ik.imagekit.io/asadofc/Images16.png",
    "https://ik.imagekit.io/asadofc/Images17.png",
    "https://ik.imagekit.io/asadofc/Images18.png",
    "https://ik.imagekit.io/asadofc/Images19.png",
    "https://ik.imagekit.io/asadofc/Images20.png",
    "https://ik.imagekit.io/asadofc/Images21.png",
    "https://ik.imagekit.io/asadofc/Images22.png",
    "https://ik.imagekit.io/asadofc/Images23.png",
    "https://ik.imagekit.io/asadofc/Images24.png",
    "https://ik.imagekit.io/asadofc/Images25.png",
    "https://ik.imagekit.io/asadofc/Images26.png",
    "https://ik.imagekit.io/asadofc/Images27.png",
    "https://ik.imagekit.io/asadofc/Images28.png",
    "https://ik.imagekit.io/asadofc/Images29.png",
    "https://ik.imagekit.io/asadofc/Images30.png",
    "https://ik.imagekit.io/asadofc/Images31.png",
    "https://ik.imagekit.io/asadofc/Images32.png",
    "https://ik.imagekit.io/asadofc/Images33.png",
    "https://ik.imagekit.io/asadofc/Images34.png",
    "https://ik.imagekit.io/asadofc/Images35.png",
    "https://ik.imagekit.io/asadofc/Images36.png",
    "https://ik.imagekit.io/asadofc/Images37.png",
    "https://ik.imagekit.io/asadofc/Images38.png",
    "https://ik.imagekit.io/asadofc/Images39.png",
    "https://ik.imagekit.io/asadofc/Images40.png"
  ]

    selected_image = random.choice(image_urls)

    await bot.send_chat_action(chat_id=chat_id, action=ChatAction.UPLOAD_PHOTO)

    await bot.send_photo(
        chat_id=chat_id,
        photo=selected_image,
        caption=reminder_message,
        parse_mode="HTML",
        reply_markup=keyboard
    )

    logger.info(f"💖 Cute membership reminder sent to {chat_id}")

def check_rate_limit():
    """Check if we're within API rate limits"""
    current_time = time.time()
    global api_request_times
    api_request_times = [t for t in api_request_times if current_time - t < 60]

    if len(api_request_times) >= MAX_REQUESTS_PER_MINUTE:
        return False

    api_request_times.append(current_time)
    return True

def manage_content_cache():
    """Manage content cache size to prevent memory issues"""
    global sent_content_ids
    if len(sent_content_ids) > MAX_CONTENT_CACHE:
        cache_list = list(sent_content_ids)
        sent_content_ids = set(cache_list[len(cache_list)//2:])
        logger.info(f"Content cache cleaned, now has {len(sent_content_ids)} items")

def start_dummy_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), DummyHandler)
    print(f"Dummy server listening on port {port}")
    server.serve_forever()

ANIME_COMMANDS = {
    "naruto": {
        "title": "Naruto", 
        "tags": ["hinata_hyuga", "sakura_haruno", "tsunade", "ino_yamanaka", "temari", "kushina_uzumaki"]
    },
    "kushina": {
        "title": "Kushina Uzumaki",
        "tags": ["kushina_uzumaki", "uzumaki_kushina", "kushina", "nine_tails_jinchuriki"]
    },
    "hinata": {
        "title": "Hinata Hyuga",
        "tags": ["hinata_hyuga", "hyuga_hinata", "hinata_(naruto)", "hinata", "byakugan"]
    },
    "sakura": {
        "title": "Sakura Haruno",
        "tags": ["sakura_haruno", "haruno_sakura", "sakura_(naruto)", "sakura", "medical_ninja"]
    },
    "temari": {
        "title": "Temari",
        "tags": ["temari_(naruto)", "temari", "sand_village", "wind_style", "fan_weapon"]
    },
    "konan": {
        "title": "Konan",
        "tags": ["konan", "paper_jutsu", "akatsuki_member"]
    },
    "ino": {
        "title": "Ino Yamanaka",
        "tags": ["ino_yamanaka", "yamanaka_ino", "ino"]
    },
    "shizune": {
        "title": "Makima",
        "tags": ["shizune", "medical_ninja", "tsunade_assistant", "leaf_village"]
    },
    "tsunade": {
        "title": "Tsunade",
        "tags": ["tsunade", "hokage", "blonde_hair", "medical_ninja", "legendary_sannin"]
    },
    "sarada": {
        "title": "Sarada Uchiha",
        "tags": ["sarada_uchiha"]
    },
    "rin": {
        "title": "Rin Nohara",
        "tags": ["rin_nohara"]
    },
    "tenten": {
        "title": "Tenten",
        "tags": ["tenten"]
    },
    "kurenai": {
        "title": "Kurenai Yuhi",
        "tags": ["kurenai_yuhi"]
    },
    "anko": {
        "title": "Anko Mitarashi",
        "tags": ["anko_mitarashi"]
    },
    "hanabi": {
        "title": "Hanabi Hyuga",
        "tags": ["hanabi_hyuga"]
    },
    "kaguya": {
        "title": "Kaguya Otsutsuki",
        "tags": ["kaguya_otsutsuki"]
    },
    "mei": {
        "title": "Mei Terumi",
        "tags": ["mei_terumi"]
    },
    "karin": {
        "title": "Karin Uzumaki",
        "tags": ["karin_uzumaki"]
    },
    "bleach": {
        "title": "Bleach", 
        "tags": ["orihime_inoue", "rukia_kuchiki", "yoruichi_shihouin", "rangiku_matsumoto", "nelliel_tu_odelschwanck"]
    },
    "rukia": {
        "title": "Rukia Kuchiki",
        "tags": ["rukia_kuchiki", "bleach", "kuchiki_rukia", "soul_reaper", "shinigami", "rukia"]
    },
    "orihime": {
        "title": "Orihime Inoue",
        "tags": ["orihime_inoue", "bleach", "inoue_orihime", "orihime", "human", "fullbringer"]
    },
    "yoruichi": {
        "title": "Yoruichi Shihouin",
        "tags": ["yoruichi_shihouin", "bleach", "shihouin_yoruichi", "yoruichi", "cat_form", "flash_goddess"]
    },
    "rangiku": {
        "title": "Rangiku Matsumoto",
        "tags": ["rangiku_matsumoto"]
    },
    "soifon": {
        "title": "Soi Fon",
        "tags": ["soi_fon"]
    },
    "nemu": {
        "title": "Nemu Kurotsuchi",
        "tags": ["nemu_kurotsuchi"]
    },
    "lisa": {
        "title": "Lisa Yadomaru",
        "tags": ["lisa_yadomaru"]
    },
    "hiyori": {
        "title": "Hiyori Sarugaki",
        "tags": ["hiyori_sarugaki"]
    },
    "mashiro": {
        "title": "Mashiro Kuna",
        "tags": ["mashiro_kuna"]
    },
    "retsu": {
        "title": "Retsu Unohana",
        "tags": ["retsu_unohana"]
    },
    "isane": {
        "title": "Isane Kotetsu",
        "tags": ["isane_kotetsu"]
    },
    "nanao": {
        "title": "Nanao Ise",
        "tags": ["nanao_ise"]
    },
    "yachiru": {
        "title": "Yachiru Kusajishi",
        "tags": ["yachiru_kusajishi"]
    },
    "nelliel": {
        "title": "Nelliel Tu Odelschwanck",
        "tags": ["nelliel_tu_odelschwanck"]
    },
    "katen": {
        "title": "Katen Kyōkotsu",
        "tags": ["katen_kyokotsu"]
    },
    "op": {
        "title": "One Piece", 
        "tags": ["nami_(one_piece)", "nico_robin", "nefeltari_vivi", "perona", "boa_hancock"]
    },
    "nami": {
        "title": "Nami",
        "tags": ["nami_(one_piece)"]
    },
    "hancock": {
        "title": "Boa Hancock",
        "tags": ["boa_hancock"]
    },
    "jjk": {
        "title": "Jujutsu Kaisen", 
        "tags": ["nobara_kugisaki", "maki_zenin", "mei_mei", "utahime_iori"]
    },
    "nobara": {
        "title": "Nobara Kugisaki",
        "tags": ["nobara_kugisaki", "kugisaki_nobara", "nobara", "hammer_and_nails", "blonde_hair", "brown_eyes"]
    },
    "maki": {
        "title": "Maki Zenin",
        "tags": ["maki_zenin"]
    },
    "yuki": {
        "title": "Yuki Tsukumo",
        "tags": ["yuki_tsukumo"]
    },
    "meimei": {
        "title": "Mei Mei",
        "tags": ["mei_mei"]
    },
    "utahime": {
        "title": "Utahime Iori",
        "tags": ["utahime_iori"]
    },
    "kasumi": {
        "title": "Kasumi Miwa",
        "tags": ["kasumi_miwa"]
    },
    "shoko": {
        "title": "Shoko Ieiri",
        "tags": ["shoko_ieiri"]
    },
    "rika": {
        "title": "Rika Orimoto",
        "tags": ["rika_orimoto"]
    },
    "spyfam": {
        "title": "Spy x Family", 
        "tags": ["yor_forger", "spy_x_family", "anya_forger"]
    },
    "yor": {
        "title": "Yor Forger",
        "tags": ["yor_forger"]
    },
    "anya": {
        "title": "Anya Forger",
        "tags": ["anya_forger"]
    },
    "aot": {
        "title": "Attack on Titan", 
        "tags": ["shingeki_no_kyojin", "mikasa_ackerman", "annie_leonhart", "historia_reiss", "pieck_finger"]
    },
    "mikasa": {
        "title": "Mikasa Ackerman",
        "tags": ["mikasa_ackerman"]
    },
    "annie": {
        "title": "Annie Leonhart",
        "tags": ["annie_leonhart"]
    },
    "historia": {
        "title": "Historia Reiss",
        "tags": ["historia_reiss"]
    },
    "sasha": {
        "title": "Sasha Blouse",
        "tags": ["sasha_blouse"]
    },
    "ymir": {
        "title": "Ymir",
        "tags": ["ymir"]
    },
    "hange": {
        "title": "Hange Zoë",
        "tags": ["hange_zoe"]
    },
    "pieck": {
        "title": "Pieck Finger",
        "tags": ["pieck_finger"]
    },
    "gabi": {
        "title": "Gabi Braun",
        "tags": ["gabi_braun"]
    },
    "carla": {
        "title": "Carla Yeager",
        "tags": ["carla_yeager"]
    },
    "frieda": {
        "title": "Frieda Reiss",
        "tags": ["frieda_reiss"]
    },
    "ymirfritz": {
        "title": "Ymir Fritz",
        "tags": ["ymir_fritz"]
    },
    "ds": {
        "title": "Demon Slayer", 
        "tags": ["nezuko_kamado", "shinobu_kocho", "mitsuri_kanroji", "kanao_tsuyuri"]
    },
    "nezuko": {
        "title": "Nezuko Kamado",
        "tags": ["nezuko_kamado", "demon_slayer", "kimetsu_no_yaiba", "kamado_nezuko", "nezuko", "demon_girl"]
    },
    "shinobu": {
        "title": "Shinobu Kocho",
        "tags": ["shinobu_kocho", "demon_slayer", "kimetsu_no_yaiba", "butterfly_hashira", "insect_hashira", "kocho_shinobu"]
    },
    "mitsuri": {
        "title": "Mitsuri Kanroji",
        "tags": ["mitsuri_kanroji", "demon_slayer", "kimetsu_no_yaiba", "love_hashira", "kanroji_mitsuri", "mitsuri"]
    },
    "kanao": {
        "title": "Kanao Tsuyuri",
        "tags": ["kanao_tsuyuri", "demon_slayer", "kimetsu_no_yaiba", "tsuyuri_kanao", "kanao", "flower_breathing"]
    },
    "daki": {
        "title": "Daki",
        "tags": ["daki"]
    },
    "tamayo": {
        "title": "Tamayo",
        "tags": ["tamayo"]
    },
    "aoi": {
        "title": "Aoi Kanzaki",
        "tags": ["aoi_kanzaki"]
    },
    "kanae": {
        "title": "Kanae Kocho",
        "tags": ["kanae_kocho"]
    },
    "amane": {
        "title": "Ubuyashiki Amane",
        "tags": ["ubuyashiki_amane"]
    },
    "vs": {
        "title": "Vinland Saga", 
        "tags": ["vinland_saga", "thorfinn", "askeladd"]
    },
    "helga": {
        "title": "Helga",
        "tags": ["helga"]
    },
    "ylva": {
        "title": "Ylva",
        "tags": ["ylva"]
    },
    "arnheid": {
        "title": "Arnheid",
        "tags": ["arnheid"]
    },
    "gudrid": {
        "title": "Gudrid",
        "tags": ["gudrid"]
    },
    "dand": {
        "title": "Dandadan", 
        "tags": ["dandadan", "momo_ayase", "seiko_ayase"]
    },
    "momoayase": {
        "title": "Momo Ayase",
        "tags": ["momo_ayase"]
    },
    "oka": {
        "title": "Oka Sarutobi",
        "tags": ["oka_sarutobi"]
    },
    "naomidand": {
        "title": "Naomi",
        "tags": ["naomi"]
    },
    "shakunetsu": {
        "title": "Shakunetsu Ayase",
        "tags": ["shakunetsu_ayase"]
    },
    "ikue": {
        "title": "Ikue",
        "tags": ["ikue"]
    },
    "opm": {
        "title": "One Punch Man", 
        "tags": ["fubuki_(one-punch_man)", "tatsumaki"]
    },
    "tatsumaki": {
        "title": "Tatsumaki",
        "tags": ["tatsumaki"]
    },
    "fubuki": {
        "title": "Fubuki",
        "tags": ["fubuki_(one-punch_man)"]
    },
    "cm": {
        "title": "Chainsaw Man", 
        "tags": ["power_(chainsaw_man)", "makima", "chainsaw_man", "kobeni_higashiyama"]
    },
    "power": {
        "title": "Power",
        "tags": ["power_(chainsaw_man)"]
    },
    "makima": {
        "title": "Makima",
        "tags": ["makima"]
    },
    "himeno": {
        "title": "Himeno",
        "tags": ["himeno"]
    },
    "quanxi": {
        "title": "Quanxi",
        "tags": ["quanxi"]
    },
    "reze": {
        "title": "Reze",
        "tags": ["reze"]
    },
    "angel": {
        "title": "Angel Devil",
        "tags": ["angel_devil"]
    },
    "asa": {
        "title": "Asa Mitaka",
        "tags": ["asa_mitaka"]
    },
    "sd": {
        "title": "Sakamoto Days", 
        "tags": ["sakamoto_days", "lu_xiaotang"]
    },
    "osaragi": {
        "title": "Osaragi",
        "tags": ["osaragi_(sakamoto_days)"]
    },
    "drs": {
        "title": "Dr Stone", 
        "tags": ["dr._stone", "kohaku_(dr._stone)", "ruri_(dr._stone)"]
    },
    "yuzuriha": {
        "title": "Yuzuriha Ogawa",
        "tags": ["yuzuriha_ogawa"]
    },
    "kohaku": {
        "title": "Kohaku",
        "tags": ["kohaku_(dr._stone)"]
    },
    "ruri": {
        "title": "Ruri",
        "tags": ["ruri_(dr._stone)"]
    },
    "suika": {
        "title": "Suika",
        "tags": ["suika"]
    },
    "stella": {
        "title": "Stella",
        "tags": ["stella"]
    },
    "overflow": {
        "title": "Overflow", 
        "tags": ["overflow", "kotone_shirakawa", "ayane_shirakawa"]
    },
    "kotone": {
        "title": "Kotone Shirakawa",
        "tags": ["kotone_shirakawa"]
    },
    "ayane": {
        "title": "Ayane Shirakawa",
        "tags": ["ayane_shirakawa"]
    },
    "bnha": {
        "title": "My Hero Academia", 
        "tags": ["ochako_uraraka", "momo_yaoyorozu", "tsuyu_asui", "kyoka_jiro", "mina_ashido", "boku_no_hero_academia"]
    },
    "ochako": {
        "title": "Ochako Uraraka",
        "tags": ["ochako_uraraka", "boku_no_hero_academia"]
    },
    "momo": {
        "title": "Momo Yaoyorozu",
        "tags": ["momo_yaoyorozu", "boku_no_hero_academia"]
    },
    "tsuyu": {
        "title": "Tsuyu Asui",
        "tags": ["tsuyu_asui", "boku_no_hero_academia"]
    },
    "kyoka": {
        "title": "Kyoka Jiro",
        "tags": ["kyoka_jiro", "boku_no_hero_academia"]
    },
    "mina": {
        "title": "Mina Ashido",
        "tags": ["mina_ashido", "boku_no_hero_academia"]
    },
    "toru": {
        "title": "Toru Hagakure",
        "tags": ["toru_hagakure", "boku_no_hero_academia"]
    },
    "nejire": {
        "title": "Nejire Hado",
        "tags": ["nejire_hado", "boku_no_hero_academia"]
    },
    "mt": {
        "title": "Mt. Lady",
        "tags": ["mt._lady", "boku_no_hero_academia"]
    },
    "midnight": {
        "title": "Midnight",
        "tags": ["midnight", "boku_no_hero_academia"]
    },
    "mirko": {
        "title": "Mirko",
        "tags": ["mirko", "boku_no_hero_academia"]
    },
    "bubble": {
        "title": "Bubble Girl",
        "tags": ["bubble_girl", "boku_no_hero_academia"]
    },
    "uwabami": {
        "title": "Uwabami",
        "tags": ["uwabami", "boku_no_hero_academia"]
    },
    "ryukyu": {
        "title": "Ryukyu",
        "tags": ["ryukyu", "boku_no_hero_academia"]
    },
    "pixie": {
        "title": "Pixie-Bob",
        "tags": ["pixie-bob", "boku_no_hero_academia"]
    },
    "mandalay": {
        "title": "Mandalay",
        "tags": ["mandalay", "boku_no_hero_academia"]
    },
    "ragdoll": {
        "title": "Ragdoll",
        "tags": ["ragdoll", "boku_no_hero_academia"]
    },
    "tiger": {
        "title": "Tiger",
        "tags": ["tiger", "boku_no_hero_academia"]
    },
    "thirteen": {
        "title": "Thirteen",
        "tags": ["thirteen", "boku_no_hero_academia"]
    },
    "recovery": {
        "title": "Recovery Girl",
        "tags": ["recovery_girl", "boku_no_hero_academia"]
    },
    "inko": {
        "title": "Inko Midoriya",
        "tags": ["inko_midoriya", "boku_no_hero_academia"]
    },
    "rei": {
        "title": "Rei Todoroki",
        "tags": ["rei_todoroki", "boku_no_hero_academia"]
    },
    "fuyumi": {
        "title": "Fuyumi Todoroki",
        "tags": ["fuyumi_todoroki", "boku_no_hero_academia"]
    },
    "nana": {
        "title": "Nana Shimura",
        "tags": ["nana_shimura", "boku_no_hero_academia"]
    },
    "star": {
        "title": "Star and Stripe",
        "tags": ["star_and_stripe", "boku_no_hero_academia"]
    },
    "lady": {
        "title": "Lady Nagant",
        "tags": ["lady_nagant", "boku_no_hero_academia"]
    },
    "camie": {
        "title": "Camie Utsushimi",
        "tags": ["camie_utsushimi", "boku_no_hero_academia"]
    },
    "yu": {
        "title": "Yu Takeyama",
        "tags": ["yu_takeyama", "boku_no_hero_academia"]
    },
    "nao": {
        "title": "Nao",
        "tags": ["nao", "boku_no_hero_academia"]
    },
    "kendo": {
        "title": "Itsuka Kendo",
        "tags": ["itsuka_kendo", "boku_no_hero_academia"]
    },
    "ibara": {
        "title": "Ibara Shiozaki",
        "tags": ["ibara_shiozaki", "boku_no_hero_academia"]
    },
    "setsuna": {
        "title": "Setsuna Tokage",
        "tags": ["setsuna_tokage", "boku_no_hero_academia"]
    },
    "pony": {
        "title": "Pony Tsunotori",
        "tags": ["pony_tsunotori", "boku_no_hero_academia"]
    },
    "reiko": {
        "title": "Reiko Yanagi",
        "tags": ["reiko_yanagi", "boku_no_hero_academia"]
    },
    "kinoko": {
        "title": "Kinoko Komori",
        "tags": ["kinoko_komori", "boku_no_hero_academia"]
    },
    "shihai": {
        "title": "Shihai Kuroiro",
        "tags": ["shihai_kuroiro", "boku_no_hero_academia"]
    },
    "yui": {
        "title": "Yui Kodai",
        "tags": ["yui_kodai", "boku_no_hero_academia"]
    },
    "hxh": {
        "title": "Hunter x Hunter", 
        "tags": ["hunter_x_hunter", "machi_komacine", "shizuku_murasaki"]
    },
    "biscuit": {
        "title": "Biscuit Krueger",
        "tags": ["biscuit_krueger", "hunter_x_hunter"]
    },
    "machi": {
        "title": "Machi Komacine",
        "tags": ["machi_komacine", "hunter_x_hunter"]
    },
    "neon": {
        "title": "Neon Nostrade",
        "tags": ["neon_nostrade", "hunter_x_hunter"]
    },
    "mha": {
        "title": "My Hero Academia", 
        "tags": ["ochako_uraraka", "momo_yaoyorozu", "tsuyu_asui", "nejire_hado", "boku_no_hero_academia"]
    },
    "ochaco": {
        "title": "Ochaco Uraraka",
        "tags": ["ochako_uraraka", "boku_no_hero_academia"]
    },
    "tsuyu": {
        "title": "Tsuyu Asui",
        "tags": ["tsuyu_asui", "boku_no_hero_academia"]
    },
    "momoyaoyorozu": {
        "title": "Momo Yaoyorozu",
        "tags": ["momo_yaoyorozu", "boku_no_hero_academia"]
    },
    "toga": {
        "title": "Himiko Toga",
        "tags": ["himiko_toga", "boku_no_hero_academia"]
    },
    "kyoka": {
        "title": "Kyoka Jiro",
        "tags": ["kyoka_jiro", "boku_no_hero_academia"]
    },
    "nejire": {
        "title": "Nejire Hado",
        "tags": ["nejire_hado", "boku_no_hero_academia"]
    },
    "mirko": {
        "title": "Mirko",
        "tags": ["mirko", "boku_no_hero_academia"]
    },
    "mina": {
        "title": "Mina Ashido",
        "tags": ["mina_ashido", "boku_no_hero_academia"]
    },
    "star": {
        "title": "Star and Stripe",
        "tags": ["star_and_stripe", "boku_no_hero_academia"]
    },
    "eri": {
        "title": "Eri",
        "tags": ["eri", "boku_no_hero_academia"]
    },
    "fma": {
        "title": "Fullmetal Alchemist", 
        "tags": ["fullmetal_alchemist", "winry_rockbell", "riza_hawkeye", "lust_(fma)", "izumi_curtis"]
    },
    "winry": {
        "title": "Winry Rockbell",
        "tags": ["winry_rockbell", "fullmetal_alchemist"]
    },
    "riza": {
        "title": "Riza Hawkeye",
        "tags": ["riza_hawkeye", "fullmetal_alchemist"]
    },
    "olivier": {
        "title": "Olivier Mira Armstrong",
        "tags": ["olivier_mira_armstrong", "fullmetal_alchemist"]
    },
    "izumi": {
        "title": "Izumi Curtis",
        "tags": ["izumi_curtis", "fullmetal_alchemist"]
    },
    "lanfan": {
        "title": "Lan Fan",
        "tags": ["lan_fan", "fullmetal_alchemist"]
    },
    "meichang": {
        "title": "Mei Chang",
        "tags": ["mei_chang", "fullmetal_alchemist"]
    },
    "rose": {
        "title": "Rose Thomas",
        "tags": ["rose_thomas", "fullmetal_alchemist"]
    },
    "nina": {
        "title": "Nina Tucker",
        "tags": ["nina_tucker", "fullmetal_alchemist"]
    },
    "trisha": {
        "title": "Trisha Elric",
        "tags": ["trisha_elric", "fullmetal_alchemist"]
    },
    "sheska": {
        "title": "Sheska",
        "tags": ["sheska", "fullmetal_alchemist"]
    },
    "dn": {
        "title": "Death Note", 
        "tags": ["death_note", "misa_amane", "naomi_misora"]
    },
    "misa": {
        "title": "Misa Amane",
        "tags": ["misa_amane", "death_note"]
    },
    "naomimisora": {
        "title": "Naomi Misora",
        "tags": ["naomi_misora", "death_note"]
    },
    "kiyomi": {
        "title": "Kiyomi Takada",
        "tags": ["kiyomi_takada", "death_note"]
    },
    "tg": {
        "title": "Tokyo Ghoul", 
        "tags": ["tokyo_ghoul", "touka_kirishima", "rize_kamishiro"]
    },
    "touka": {
        "title": "Touka Kirishima",
        "tags": ["touka_kirishima", "tokyo_ghoul"]
    },
    "eto": {
        "title": "Eto Yoshimura",
        "tags": ["eto_yoshimura", "tokyo_ghoul"]
    },
    "rize": {
        "title": "Rize Kamishiro",
        "tags": ["rize_kamishiro", "tokyo_ghoul"]
    },
    "akira": {
        "title": "Akira Mado",
        "tags": ["akira_mado", "tokyo_ghoul"]
    },
    "hinami": {
        "title": "Hinami Fueguchi",
        "tags": ["hinami_fueguchi", "tokyo_ghoul"]
    },
    "itori": {
        "title": "Itori",
        "tags": ["itori", "tokyo_ghoul"]
    },
    "karren": {
        "title": "Karren von Rosewald",
        "tags": ["karren_von_rosewald", "tokyo_ghoul"]
    },
    "kimi": {
        "title": "Kimi Nishino",
        "tags": ["kimi_nishino", "tokyo_ghoul"]
    },
    "yoriko": {
        "title": "Yoriko Kosaka",
        "tags": ["yoriko_kosaka", "tokyo_ghoul"]
    },
    "roma": {
        "title": "Roma Hoito",
        "tags": ["roma_hoito", "tokyo_ghoul"]
    },
    "mdd": {
        "title": "My Dress-Up Darling", 
        "tags": ["sono_bisque_doll_wa_koi_wo_suru", "marin_kitagawa"]
    },
    "marin": {
        "title": "Marin Kitagawa",
        "tags": ["marin_kitagawa"]
    },
    "sajuna": {
        "title": "Sajuna Inui",
        "tags": ["sajuna_inui"]
    },
    "shinju": {
        "title": "Shinju Inui",
        "tags": ["shinju_inui"]
    },
    "boruto": {
        "title": "Boruto", 
        "tags": ["boruto", "sarada_uchiha", "himawari_uzumaki"]
    },
    "ps": {
        "title": "Prison School", 
        "tags": ["prison_school", "hana_midorikawa", "meiko_shiraki", "mari_kurihara"]
    }
}

PRIORITY_COMMANDS = [
    "start",
    "naruto", "hinata", "sakura", "tsunade", "kushina", "temari", "ino", "konan", "shizune", "sarada", "rin", "tenten", "kurenai", "anko", "hanabi", "kaguya", "mei", "karin",
    "bleach", "rukia", "orihime", "yoruichi", "rangiku", "nelliel", "soifon", "nemu", "lisa", "hiyori",
    "op", "nami", "hancock",
    "jjk", "nobara", "maki", "yuki", "meimei", "utahime",
    "spyfam", "yor", "anya",
    "aot", "mikasa", "annie", "historia", "sasha", "ymir", "pieck",
    "ds", "nezuko", "shinobu", "mitsuri", "daki", "kanao",
    "opm", "tatsumaki", "fubuki",
    "cm", "power", "makima",
    "mha", "ochaco", "tsuyu", "toga", "momoyaoyorozu", "kyoka", "nejire", "mirko", "mina", "eri",
    "fma", "winry", "riza", "olivier", "izumi",
    "dn", "misa",
    "tg", "touka", "rize", "eto", "akira", "hinami",
    "mdd", "marin", "sajuna", "shinju",
    "vs", "dand", "sd", "drs", "overflow", "hxh", "boruto", "ps"
]

REGISTERED_COMMANDS = PRIORITY_COMMANDS[:97] + ["random"]

COMMAND_DESCRIPTIONS = {
    "start": "💖 Meet Makima",
    "random": "🎲 Surprise Me",
    "naruto": "🍃 Ninja World",
    "bleach": "⚔️ Soul Society", 
    "op": "🏴‍☠️ Grand Line",
    "jjk": "✨ Cursed Energy",
    "spyfam": "🕵️ Secret Family",
    "aot": "⚡ Titan World",
    "ds": "🗡️ Demon Hunt",
    "vs": "🛡️ Viking Saga",
    "dand": "👻 Yokai Hunt",
    "opm": "💪 Hero World",
    "cm": "⛓️ Devil Hunt",
    "sd": "🎯 Assassin Life",
    "drs": "🧪 Science World",
    "overflow": "💧 School Days",
    "hxh": "🎮 Hunter Life",
    "mha": "🦸 Hero Academy",
    "fma": "⚗️ Alchemy Art",
    "dn": "📓 Death Gods",
    "tg": "🖤 Ghoul World",
    "mdd": "👗 Cosplay Fun",
    "boruto": "🌟 New Era",
    "ps": "🏫 School Prison",
    "hinata": "💜 Shy Princess",
    "sakura": "🌸 Cherry Blossom",
    "tsunade": "👑 Legendary Sannin",
    "kushina": "❤️ Red Hot",
    "rukia": "❄️ Ice Princess", 
    "orihime": "🧡 Sweet Angel",
    "yoruichi": "⚡ Flash Goddess",
    "mikasa": "⚔️ Warrior Queen",
    "annie": "💎 Crystal Girl",
    "nezuko": "🌺 Bamboo Cutie",
    "shinobu": "🦋 Butterfly Beauty",
    "nobara": "🔨 Strong Girl",
    "maki": "💚 Weapon Master",
    "yor": "🖤 Assassin Mom",
    "anya": "💕 Mind Reader",
    "power": "🩸 Blood Fiend",
    "makima": "🐕 Control Devil",
    "nami": "🍊 Navigator",
    "hancock": "🐍 Snake Princess"
}

BOT_COMMANDS = [
    BotCommand(command=cmd, description=COMMAND_DESCRIPTIONS.get(cmd, f"💖 {cmd.title()}"))
    for cmd in REGISTERED_COMMANDS
]

async def fetch_rule34_media(anime_name: str, media_type: str = "image", user_id: int = 0, max_retries: int = 5):
    """
    Fetches anime-specific NSFW content from Rule34 API using tags
    Returns high-quality content (image/video/gif) with guaranteed success through retries
    Prevents duplicate content using advanced tracking system
    """
    anime_data = ANIME_COMMANDS.get(anime_name)
    if not anime_data:
        logger.error(f"Anime {anime_name} not found in database")
        return None

    tags = anime_data["tags"]
    user_key = f"{user_id}_{anime_name}" if user_id else anime_name

    if user_key not in user_offsets:
        user_offsets[user_key] = 0

    for retry in range(max_retries):
        try:
            character_specific_tags = []
            generic_tags = []

            character_name = anime_data["title"].lower().replace(" ", "_")
            for tag in tags:
                if any(name_part in tag.lower() for name_part in character_name.split("_")):
                    character_specific_tags.append(tag)
                else:
                    generic_tags.append(tag)

            if retry < len(character_specific_tags):
                selected_tags = [character_specific_tags[retry]]
            elif retry < len(character_specific_tags) + len(generic_tags):
                generic_index = retry - len(character_specific_tags)
                selected_tags = [generic_tags[generic_index]]
            else:
                if character_specific_tags:
                    primary_tag = random.choice(character_specific_tags)
                    if len(character_specific_tags) > 1:
                        secondary_tag = random.choice([t for t in character_specific_tags if t != primary_tag])
                        selected_tags = [primary_tag, secondary_tag]
                    else:
                        selected_tags = [primary_tag]
                else:
                    tag_count = min(random.randint(1, 2), len(generic_tags))
                    selected_tags = random.sample(generic_tags, tag_count)

            tag_string = "+".join(selected_tags)

            page_offset = user_offsets[user_key] + retry

            logger.info(f"Attempt {retry + 1}: Searching Rule34 for {anime_name} with tags: {selected_tags}, page: {page_offset}")

            if not check_rate_limit():
                logger.warning("Rate limit reached, waiting 10 seconds...")
                await asyncio.sleep(10)
                continue

            manage_content_cache()

            async with aiohttp.ClientSession() as session:
                params = {
                    "page": "dapi",
                    "s": "post",
                    "q": "index",
                    "tags": tag_string,
                    "limit": 100,
                    "pid": page_offset,
                    "api_key": R34_API_KEY,
                    "user_id": R34_USER_ID
                }

                async with session.get(RULE34_API_BASE, params=params) as response:
                    if response.status == 200:
                        xml_content = await response.text()

                        try:
                            root = ET.fromstring(xml_content)

                            posts = []
                            for post in root.findall('.//post'):
                                post_id = post.get('id')
                                file_url = post.get('file_url')

                                if post_id in sent_content_ids:
                                    continue

                                if file_url and file_url.startswith(('http://', 'https://')):
                                    if media_type == "image" and file_url.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
                                        posts.append({
                                            'url': file_url,
                                            'id': post_id,
                                            'tags': post.get('tags', ''),
                                            'score': int(post.get('score', 0)),
                                            'type': 'image'
                                        })
                                    elif media_type == "gif" and file_url.lower().endswith('.gif'):
                                        posts.append({
                                            'url': file_url,
                                            'id': post_id,
                                            'tags': post.get('tags', ''),
                                            'score': int(post.get('score', 0)),
                                            'type': 'gif'
                                        })
                                    elif media_type == "video" and file_url.lower().endswith(('.mp4', '.webm', '.mov')):
                                        posts.append({
                                            'url': file_url,
                                            'id': post_id,
                                            'tags': post.get('tags', ''),
                                            'score': int(post.get('score', 0)),
                                            'type': 'video'
                                        })

                            if posts:
                                posts.sort(key=lambda x: x['score'], reverse=True)
                                top_posts = posts[:50]
                                selected = random.choice(top_posts)

                                sent_content_ids.add(selected['id'])

                                user_offsets[user_key] += 1

                                logger.info(f"Found fresh {anime_name} content: score {selected['score']}, ID: {selected['id']}")
                                return selected
                        except ET.ParseError as e:
                            logger.warning(f"XML parse error on attempt {retry + 1}: {e}")
                            continue

        except Exception as e:
            logger.warning(f"Attempt {retry + 1} failed for {anime_name}: {e}")
            continue

    logger.info(f"Trying advanced fallback for {anime_name}")

    character_name = anime_data["title"].lower().replace(" ", "_")
    fallback_tags = list(tags) + [character_name]

    for tag in fallback_tags:
        try:
            page_offset = random.randint(0, 10)

            async with aiohttp.ClientSession() as session:
                params = {
                    "page": "dapi",
                    "s": "post", 
                    "q": "index",
                    "tags": tag,
                    "limit": 100,
                    "pid": page_offset,
                    "api_key": R34_API_KEY,
                    "user_id": R34_USER_ID
                }

                async with session.get(RULE34_API_BASE, params=params) as response:
                    if response.status == 200:
                        xml_content = await response.text()
                        try:
                            root = ET.fromstring(xml_content)
                            posts = []
                            for post in root.findall('.//post'):
                                post_id = post.get('id')
                                file_url = post.get('file_url')

                                if post_id in sent_content_ids:
                                    continue

                                if file_url and file_url.startswith(('http://', 'https://')):
                                    if media_type == "image" and file_url.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
                                        posts.append({
                                            'url': file_url,
                                            'id': post_id,
                                            'tags': post.get('tags', ''),
                                            'score': int(post.get('score', 0)),
                                            'type': 'image'
                                        })
                                    elif media_type == "gif" and file_url.lower().endswith('.gif'):
                                        posts.append({
                                            'url': file_url,
                                            'id': post_id,
                                            'tags': post.get('tags', ''),
                                            'score': int(post.get('score', 0)),
                                            'type': 'gif'
                                        })
                                    elif media_type == "video" and file_url.lower().endswith(('.mp4', '.webm', '.mov')):
                                        posts.append({
                                            'url': file_url,
                                            'id': post_id,
                                            'tags': post.get('tags', ''),
                                            'score': int(post.get('score', 0)),
                                            'type': 'video'
                                        })

                            if posts:
                                posts.sort(key=lambda x: x['score'], reverse=True)
                                selected = random.choice(posts[:30])

                                sent_content_ids.add(selected['id'])

                                logger.info(f"Found fallback content for {anime_name} with tag {tag}, ID: {selected['id']}")
                                return selected
                        except ET.ParseError as e:
                            logger.warning(f"Fallback XML parse error for tag {tag}: {e}")
                            continue
        except Exception as e:
            logger.warning(f"Fallback failed for tag {tag}: {e}")
            continue

    logger.error(f"All attempts failed for {anime_name}")
    return None

def create_media_selection_keyboard(anime_name: str):
    """Create beautiful keyboard for media type selection"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🎬 Videos", callback_data=f"select_video_{anime_name}"),
            InlineKeyboardButton(text="🖼️ Images", callback_data=f"select_image_{anime_name}")
        ],
        [
            InlineKeyboardButton(text="🎨 Animations", callback_data=f"select_gif_{anime_name}")
        ]
    ])
    return keyboard

def create_media_navigation_keyboard(anime_name: str, media_type: str, page: int = 1):
    """Create beautiful keyboard for media navigation with Update, Next, Back buttons"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="💞 Refresh", callback_data=f"update_{anime_name}_{media_type}_{page}"),
            InlineKeyboardButton(text="💘 Next", callback_data=f"next_{anime_name}_{media_type}_{page}")
        ],
        [
            InlineKeyboardButton(text="💓 Back", callback_data=f"back_{anime_name}")
        ]
    ])
    return keyboard

async def send_media_selection(anime_name: str, chat_id: int):
    """Send initial image with media type selection buttons"""
    anime_data = ANIME_COMMANDS.get(anime_name)
    if not anime_data:
        return None

    title = anime_data["title"]
    logger.info(f"Sending media selection for {title}")

    post = await fetch_rule34_media(anime_name, "image", chat_id)
    if not post:
        return None

    try:
        keyboard = create_media_selection_keyboard(anime_name)
        caption = f"💖 {title}\n\n✨ What would you like to see?"

        await bot.send_chat_action(chat_id=chat_id, action=ChatAction.UPLOAD_PHOTO)

        sent_msg = await bot.send_photo(
            chat_id=chat_id,
            photo=post['url'],
            caption=caption,
            reply_markup=keyboard,
            has_spoiler=True
        )
        return sent_msg
    except Exception as e:
        logger.error(f"Media selection error: {e}")
        return None

async def send_random_media(chat_id: int, message_id: int | None = None, edit_mode: bool = False, media_type: str = "image", page: int = 1):
    """Send or edit random media with retry system (matching anime command style)"""
    try:
        attempts = 0
        post = None

        while attempts < 3 and not post:
            await asyncio.sleep(0.001)
            post = await fetch_random_content(media_type)
            attempts += 1

        if not post:
            post = await fetch_random_content("image")
        if not post:
            return None

        keyboard = create_random_navigation_keyboard(media_type, page)
        caption = f"🎲 <b>Random {media_type.title()}</b> ✨\n\n💫 Enjoy this surprise!"

        if edit_mode and message_id:
            if media_type == "video":
                await bot.edit_message_media(
                    chat_id=chat_id,
                    message_id=message_id,
                    media=InputMediaVideo(
                        media=post['url'],
                        caption=caption,
                        parse_mode="HTML",
                        has_spoiler=True
                    ),
                    reply_markup=keyboard
                )
            elif media_type == "gif":
                await bot.edit_message_media(
                    chat_id=chat_id,
                    message_id=message_id,
                    media=InputMediaAnimation(
                        media=post['url'],
                        caption=caption,
                        parse_mode="HTML",
                        has_spoiler=True
                    ),
                    reply_markup=keyboard
                )
            else:
                await bot.edit_message_media(
                    chat_id=chat_id,
                    message_id=message_id,
                    media=InputMediaPhoto(
                        media=post['url'],
                        caption=caption,
                        parse_mode="HTML",
                        has_spoiler=True
                    ),
                    reply_markup=keyboard
                )
            logger.info(f"Successfully loaded random {media_type}")
        else:
            if media_type == "video":
                await bot.send_chat_action(chat_id=chat_id, action=ChatAction.UPLOAD_VIDEO)
            else:
                await bot.send_chat_action(chat_id=chat_id, action=ChatAction.UPLOAD_PHOTO)

            if media_type == "video":
                await bot.send_video(
                    chat_id=chat_id,
                    video=post['url'],
                    caption=caption,
                    reply_markup=keyboard,
                    has_spoiler=True
                )
            elif media_type == "gif":
                await bot.send_animation(
                    chat_id=chat_id,
                    animation=post['url'],
                    caption=caption,
                    reply_markup=keyboard,
                    has_spoiler=True
                )
            else:
                await bot.send_photo(
                    chat_id=chat_id,
                    photo=post['url'],
                    caption=caption,
                    reply_markup=keyboard,
                    has_spoiler=True
                )
            logger.info(f"Successfully sent random {media_type}")

        return True
    except Exception as e:
        logger.error(f"Random media send error: {e}")
        return None

async def send_search_media(search_query: str, chat_id: int, message_id: int | None = None, edit_mode: bool = False, media_type: str = "image", page: int = 1):
    """Send or edit search media with retry system (matching anime command style)"""
    try:
        post = await search_rule34_live(search_query, media_type)
        if not post:
            return None

        keyboard = create_search_navigation_keyboard(search_query, media_type, page)
        caption = f"🔍 <b>Search Result</b> ✨\n\n💫 Found: <i>{search_query}</i>"

        if edit_mode and message_id:
            if media_type == "video":
                await bot.edit_message_media(
                    chat_id=chat_id,
                    message_id=message_id,
                    media=InputMediaVideo(
                        media=post['url'],
                        caption=caption,
                        parse_mode="HTML",
                        has_spoiler=True
                    ),
                    reply_markup=keyboard
                )
            elif media_type == "gif":
                await bot.edit_message_media(
                    chat_id=chat_id,
                    message_id=message_id,
                    media=InputMediaAnimation(
                        media=post['url'],
                        caption=caption,
                        parse_mode="HTML",
                        has_spoiler=True
                    ),
                    reply_markup=keyboard
                )
            else:
                await bot.edit_message_media(
                    chat_id=chat_id,
                    message_id=message_id,
                    media=InputMediaPhoto(
                        media=post['url'],
                        caption=caption,
                        parse_mode="HTML",
                        has_spoiler=True
                    ),
                    reply_markup=keyboard
                )
            logger.info(f"Successfully loaded search {media_type} for '{search_query}'")
        else:
            if media_type == "video":
                await bot.send_chat_action(chat_id=chat_id, action=ChatAction.UPLOAD_VIDEO)
            else:
                await bot.send_chat_action(chat_id=chat_id, action=ChatAction.UPLOAD_PHOTO)

            if media_type == "video":
                await bot.send_video(
                    chat_id=chat_id,
                    video=post['url'],
                    caption=caption,
                    reply_markup=keyboard,
                    has_spoiler=True
                )
            elif media_type == "gif":
                await bot.send_animation(
                    chat_id=chat_id,
                    animation=post['url'],
                    caption=caption,
                    reply_markup=keyboard,
                    has_spoiler=True
                )
            else:
                await bot.send_photo(
                    chat_id=chat_id,
                    photo=post['url'],
                    caption=caption,
                    reply_markup=keyboard,
                    has_spoiler=True
                )
            logger.info(f"Successfully sent search {media_type} for '{search_query}'")

        return True
    except Exception as e:
        logger.error(f"Search media send error: {e}")
        return None

async def send_anime_media(anime_name: str, chat_id: int, message_id: int | None = None, edit_mode: bool = False, media_type: str = "image", page: int = 1):
    """Send or edit anime media with retry system"""
    anime_data = ANIME_COMMANDS.get(anime_name)
    if not anime_data:
        return None

    title = anime_data["title"]
    media_emoji = {"image": "🖼️", "video": "🎬", "gif": "🎨"}
    logger.info(f"Fetching {title} {media_type} content using API")

    post = None
    for attempt in range(15):
        post = await fetch_rule34_media(anime_name, media_type, chat_id)
        if post:
            break

        if attempt >= 10 and media_type in ["video", "gif"]:
            logger.info(f"No {media_type} found for {anime_name}, falling back to images")
            post = await fetch_rule34_media(anime_name, "image", chat_id)
            if post:
                break

    if not post:
        logger.error(f"Failed to fetch any media for {anime_name}")
        return None

    try:
        keyboard = create_media_navigation_keyboard(anime_name, media_type, page)
        caption = f"💖 {title} {media_emoji.get(media_type, '')} ✨"

        logger.info(f"Sending {media_type} for {anime_name}: {post['url'][-50:]}")

        if edit_mode and message_id is not None:
            if media_type == "video":
                await bot.edit_message_media(
                    chat_id=chat_id,
                    message_id=message_id,
                    media=InputMediaVideo(
                        media=post['url'],
                        caption=caption,
                        parse_mode="HTML",
                        has_spoiler=True
                    ),
                    reply_markup=keyboard
                )
            elif media_type == "gif":
                await bot.edit_message_media(
                    chat_id=chat_id,
                    message_id=message_id,
                    media=InputMediaAnimation(
                        media=post['url'],
                        caption=caption,
                        parse_mode="HTML",
                        has_spoiler=True
                    ),
                    reply_markup=keyboard
                )
            else:
                await bot.edit_message_media(
                    chat_id=chat_id,
                    message_id=message_id,
                    media=InputMediaPhoto(
                        media=post['url'],
                        caption=caption,
                        parse_mode="HTML",
                        has_spoiler=True
                    ),
                    reply_markup=keyboard
                )
            return None
        else:
            if media_type == "video":
                await bot.send_chat_action(chat_id=chat_id, action=ChatAction.UPLOAD_VIDEO)
            else:
                await bot.send_chat_action(chat_id=chat_id, action=ChatAction.UPLOAD_PHOTO)

            if media_type == "video":
                sent_msg = await bot.send_video(
                    chat_id=chat_id,
                    video=post['url'],
                    caption=caption,
                    reply_markup=keyboard,
                    supports_streaming=True,
                    has_spoiler=True
                )
            elif media_type == "gif":
                sent_msg = await bot.send_animation(
                    chat_id=chat_id,
                    animation=post['url'],
                    caption=caption,
                    reply_markup=keyboard,
                    has_spoiler=True
                )
            else:
                sent_msg = await bot.send_photo(
                    chat_id=chat_id,
                    photo=post['url'],
                    caption=caption,
                    reply_markup=keyboard,
                    has_spoiler=True
                )
            return sent_msg

    except Exception as e:
        logger.warning(f"Send error: {e}")
        return None

async def fetch_random_content(media_type: str = "image"):
    """Fetch completely random content from Rule34"""
    try:
        async with aiohttp.ClientSession() as session:
            params = {
                "page": "dapi",
                "s": "post",
                "q": "index",
                "tags": "",
                "limit": 50,
                "pid": random.randint(0, 100) + int(time.time()) % 100,
                "api_key": R34_API_KEY,
                "user_id": R34_USER_ID
            }

            async with session.get(RULE34_API_BASE, params=params) as response:
                if response.status == 200:
                    xml_content = await response.text()

                    try:
                        root = ET.fromstring(xml_content)
                        posts = []

                        for post in root.findall('.//post'):
                            file_url = post.get('file_url')
                            if file_url and file_url.startswith(('http://', 'https://')):
                                score = int(post.get('score', 0))
                                if score >= 10:
                                    if media_type == "image" and file_url.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
                                        posts.append({
                                            'url': file_url,
                                            'id': post.get('id'),
                                            'tags': post.get('tags', ''),
                                            'score': score,
                                            'type': 'image'
                                        })
                                    elif media_type == "gif" and file_url.lower().endswith('.gif'):
                                        posts.append({
                                            'url': file_url,
                                            'id': post.get('id'),
                                            'tags': post.get('tags', ''),
                                            'score': score,
                                            'type': 'gif'
                                        })
                                    elif media_type == "video" and file_url.lower().endswith(('.mp4', '.webm', '.mov')):
                                        posts.append({
                                            'url': file_url,
                                            'id': post.get('id'),
                                            'tags': post.get('tags', ''),
                                            'score': score,
                                            'type': 'video'
                                        })

                        if posts:
                            random.seed(int(time.time() * 1000000) % 1000000)

                            posts.sort(key=lambda x: x['score'], reverse=True)
                            top_posts = posts[:50]
                            selected = random.choice(top_posts)
                            logger.info(f"Found random content: score {selected['score']}")
                            return selected
                    except ET.ParseError as e:
                        logger.warning(f"Random content XML parse error: {e}")
    except Exception as e:
        logger.error(f"Random content fetch error: {e}")

    return None

async def search_rule34_live(search_query: str, media_type: str = "image"):
    """Search Rule34 API with user's custom query - Enhanced with smart tag conversion"""
    try:
        clean_query = search_query.lower().strip()

        tag_conversions = {
            "kushina uzumaki": "kushina_uzumaki",
            "hinata hyuga": "hinata_hyuga", 
            "sakura haruno": "sakura_haruno",
            "ino yamanaka": "ino_yamanaka",
            "temari nara": "temari",
            "tsunade senju": "tsunade",
            "rukia kuchiki": "rukia_kuchiki",
            "orihime inoue": "orihime_inoue",
            "yoruichi shihouin": "yoruichi_shihouin",
            "rangiku matsumoto": "rangiku_matsumoto",
            "mikasa ackerman": "mikasa_ackerman",
            "annie leonhart": "annie_leonhart",
            "historia reiss": "historia_reiss",
            "sasha blouse": "sasha_blouse",
            "nezuko kamado": "nezuko_kamado",
            "shinobu kocho": "shinobu_kocho",
            "mitsuri kanroji": "mitsuri_kanroji",
            "nobara kugisaki": "nobara_kugisaki",
            "maki zenin": "maki_zenin",
            "power chainsaw": "power",
            "makima chainsaw": "makima",
            "yor forger": "yor_forger",
            "anya forger": "anya_forger",
            "naruto shippuden": "naruto",
            "attack on titan": "shingeki_no_kyojin", 
            "demon slayer": "kimetsu_no_yaiba",
            "my hero academia": "my_hero_academia",
            "jujutsu kaisen": "jujutsu_kaisen",
            "spy x family": "spy_x_family",
            "chainsaw man": "chainsaw_man",
            "one piece": "one_piece",
            "love is war": "kaguya-sama_wa_kokurasetai",
            "dress up darling": "sono_bisque_doll_wa_koi_wo_suru",
            "rent a girlfriend": "kanojo_okarishimasu",
            "one punch man": "one-punch_man",
            "dr stone": "dr._stone",
            "tower of god": "tower_of_god",
            "school uniform": "school_uniform",
            "gym uniform": "gym_uniform",
            "swim suit": "swimsuit",
            "maid outfit": "maid",
            "cat girl": "cat_girl",
            "fox girl": "fox_girl",
            "big breasts": "large_breasts",
            "small breasts": "small_breasts",
            "long hair": "long_hair",
            "short hair": "short_hair",
            "blonde hair": "blonde_hair",
            "brown hair": "brown_hair",
            "black hair": "black_hair",
            "blue hair": "blue_hair",
            "red hair": "red_hair",
            "pink hair": "pink_hair",
            "blue eyes": "blue_eyes",
            "brown eyes": "brown_eyes",
            "green eyes": "green_eyes",
            "red eyes": "red_eyes",
            "purple eyes": "purple_eyes"
        }

        formatted_query = clean_query
        for original, converted in tag_conversions.items():
            if original in formatted_query:
                formatted_query = formatted_query.replace(original, converted)

        formatted_query = formatted_query.replace(" ", "_")

        logger.info(f"Live searching Rule34 for: '{formatted_query}' (original: '{clean_query}')")

        async with aiohttp.ClientSession() as session:
            params = {
                "page": "dapi",
                "s": "post",
                "q": "index",
                "tags": formatted_query,
                "limit": 100,
                "pid": random.randint(0, 100) + int(time.time()) % 100,
                "api_key": R34_API_KEY,
                "user_id": R34_USER_ID
            }

            async with session.get(RULE34_API_BASE, params=params) as response:
                if response.status == 200:
                    xml_content = await response.text()

                    try:
                        root = ET.fromstring(xml_content)
                        posts = []

                        for post in root.findall('.//post'):
                            file_url = post.get('file_url')
                            if file_url and file_url.startswith(('http://', 'https://')):
                                if media_type == "image" and file_url.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
                                    posts.append({
                                        'url': file_url,
                                        'id': post.get('id'),
                                        'tags': post.get('tags', ''),
                                        'score': int(post.get('score', 0)),
                                        'type': 'image'
                                    })
                                elif media_type == "gif" and file_url.lower().endswith('.gif'):
                                    posts.append({
                                        'url': file_url,
                                        'id': post.get('id'),
                                        'tags': post.get('tags', ''),
                                        'score': int(post.get('score', 0)),
                                        'type': 'gif'
                                    })
                                elif media_type == "video" and file_url.lower().endswith(('.mp4', '.webm', '.mov')):
                                    posts.append({
                                        'url': file_url,
                                        'id': post.get('id'),
                                        'tags': post.get('tags', ''),
                                        'score': int(post.get('score', 0)),
                                        'type': 'video'
                                    })

                        if posts:
                            random.seed(int(time.time() * 1000000) % 1000000)

                            posts.sort(key=lambda x: x['score'], reverse=True)
                            top_posts = posts[:50]
                            selected = random.choice(top_posts)
                            logger.info(f"Found search result for '{search_query}': score {selected['score']}")
                            return selected
                    except ET.ParseError as e:
                        logger.warning(f"Search XML parse error: {e}")
    except Exception as e:
        logger.error(f"Live search error: {e}")

    return None

def create_random_selection_keyboard():
    """Create media type selection keyboard for random content (like anime commands)"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🎬 Videos", callback_data="select_video_random"),
            InlineKeyboardButton(text="🖼️ Images️", callback_data="select_image_random")
        ],
        [
            InlineKeyboardButton(text="🎨 Animations", callback_data="select_gif_random")
        ]
    ])
    return keyboard

def create_random_navigation_keyboard(media_type: str = "image", page: int = 1):
    """Create navigation keyboard for random content (matching anime command style)"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="💞 Refresh", callback_data=f"update_random_{media_type}_{page}"),
            InlineKeyboardButton(text="💘 Next", callback_data=f"next_random_{media_type}_{page}")
        ],
        [
            InlineKeyboardButton(text="💓 Back", callback_data="back_random")
        ]
    ])
    return keyboard

def create_search_selection_keyboard(search_query: str):
    """Create media type selection keyboard for search results (like anime commands)"""
    encoded_query = search_query.replace(" ", "_")[:20]

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🎬 Videos", callback_data=f"select_video_{encoded_query}"),
            InlineKeyboardButton(text="🖼️ Images️", callback_data=f"select_image_{encoded_query}")
        ],
        [
            InlineKeyboardButton(text="🎨 Animations", callback_data=f"select_gif_{encoded_query}")
        ]
    ])
    return keyboard

def create_search_navigation_keyboard(search_query: str, media_type: str = "image", page: int = 1):
    """Create navigation keyboard for search results (matching anime command style)"""
    encoded_query = search_query.replace(" ", "_")[:20]

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="💞 Refresh", callback_data=f"update_{encoded_query}_{media_type}_{page}"),
            InlineKeyboardButton(text="💘 Next", callback_data=f"next_{encoded_query}_{media_type}_{page}")
        ],
        [
            InlineKeyboardButton(text="💓 Back", callback_data=f"back_{encoded_query}")
        ]
    ])
    return keyboard

def make_anime_handler(anime_name):
    async def handler(msg: Message):
        if msg.from_user and should_check_membership(msg.from_user.id):
            if not check_membership(msg.from_user.id):
                await send_membership_reminder(msg.chat.id, msg.from_user.id, msg.from_user.full_name)
                return
        await send_media_selection(anime_name, msg.chat.id)
    return handler

for anime_name in ANIME_COMMANDS:
    dp.message.register(make_anime_handler(anime_name), Command(anime_name))

@dp.message(Command("start"))
async def cmd_start(msg: Message):

    await bot.send_chat_action(msg.chat.id, action="upload_photo")

    if msg.from_user and should_check_membership(msg.from_user.id):
        if not check_membership(msg.from_user.id):
            await send_membership_reminder(
                chat_id=msg.chat.id,
                user_id=msg.from_user.id,
                user_name=msg.from_user.full_name
            )
            return

    user_name = msg.from_user.full_name if msg.from_user else "User"
    user_id = msg.from_user.id if msg.from_user else ""

    bot_info = await bot.get_me()
    bot_username = bot_info.username

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="💟 Updates", url="https://t.me/WorkGlows"),
            InlineKeyboardButton(text="Support 💞", url="https://t.me/SoulMeetsHQ")
        ],
        [
            InlineKeyboardButton(text="💗️ Add Me To Your Group 💗", url=f"https://t.me/{bot_username}?startgroup=true&admin=delete_messages+ban_users+invite_users+pin_messages+manage_chat+manage_video_chats+post_messages+edit_messages+manage_topics+add_admins")
        ]
    ])

    welcome_text = f"""
💖 <b>Hey there</b> <a href="tg://user?id={user_id}"><b>{user_name}</b></a>, <b>Welcome!</b>

<b>Makima</b> here, to brighten your day! 🌸

🎀 Enjoy <b>150+ anime commands</b> and <b>amazing content</b> from <b>22+ series.</b> All super easy to explore!

<blockquote><i>💌 Use any anime command to begin your journey!</i></blockquote>
"""

    image_urls = [
    "https://ik.imagekit.io/asadofc/Images1.png",
    "https://ik.imagekit.io/asadofc/Images2.png",
    "https://ik.imagekit.io/asadofc/Images3.png",
    "https://ik.imagekit.io/asadofc/Images4.png",
    "https://ik.imagekit.io/asadofc/Images5.png",
    "https://ik.imagekit.io/asadofc/Images6.png",
    "https://ik.imagekit.io/asadofc/Images7.png",
    "https://ik.imagekit.io/asadofc/Images8.png",
    "https://ik.imagekit.io/asadofc/Images9.png",
    "https://ik.imagekit.io/asadofc/Images10.png",
    "https://ik.imagekit.io/asadofc/Images11.png",
    "https://ik.imagekit.io/asadofc/Images12.png",
    "https://ik.imagekit.io/asadofc/Images13.png",
    "https://ik.imagekit.io/asadofc/Images14.png",
    "https://ik.imagekit.io/asadofc/Images15.png",
    "https://ik.imagekit.io/asadofc/Images16.png",
    "https://ik.imagekit.io/asadofc/Images17.png",
    "https://ik.imagekit.io/asadofc/Images18.png",
    "https://ik.imagekit.io/asadofc/Images19.png",
    "https://ik.imagekit.io/asadofc/Images20.png",
    "https://ik.imagekit.io/asadofc/Images21.png",
    "https://ik.imagekit.io/asadofc/Images22.png",
    "https://ik.imagekit.io/asadofc/Images23.png",
    "https://ik.imagekit.io/asadofc/Images24.png",
    "https://ik.imagekit.io/asadofc/Images25.png",
    "https://ik.imagekit.io/asadofc/Images26.png",
    "https://ik.imagekit.io/asadofc/Images27.png",
    "https://ik.imagekit.io/asadofc/Images28.png",
    "https://ik.imagekit.io/asadofc/Images29.png",
    "https://ik.imagekit.io/asadofc/Images30.png",
    "https://ik.imagekit.io/asadofc/Images31.png",
    "https://ik.imagekit.io/asadofc/Images32.png",
    "https://ik.imagekit.io/asadofc/Images33.png",
    "https://ik.imagekit.io/asadofc/Images34.png",
    "https://ik.imagekit.io/asadofc/Images35.png",
    "https://ik.imagekit.io/asadofc/Images36.png",
    "https://ik.imagekit.io/asadofc/Images37.png",
    "https://ik.imagekit.io/asadofc/Images38.png",
    "https://ik.imagekit.io/asadofc/Images39.png",
    "https://ik.imagekit.io/asadofc/Images40.png"
  ]

    selected_image = random.choice(image_urls)

    await msg.answer_photo(
        photo=selected_image,
        caption=welcome_text,
        parse_mode="HTML",
        reply_markup=keyboard
    )



async def send_random_selection(chat_id: int):
    """Send initial random content with media type selection buttons (like anime commands)"""
    logger.info("Sending random media selection")

    await bot.send_chat_action(chat_id, action="upload_photo")

    post = await fetch_random_content("image")
    if not post:
        return None

    try:
        keyboard = create_random_selection_keyboard()
        caption = "🎲 <b>Random Content</b> ✨\n\n💫 What would you like to see?"

        await bot.send_photo(
            chat_id=chat_id,
            photo=post['url'],
            caption=caption,
            reply_markup=keyboard,
            has_spoiler=True
        )
        logger.info("Random media selection sent successfully")
        return True
    except Exception as e:
        logger.error(f"Random selection send error: {e}")
        return None

@dp.message(Command("random"))
async def cmd_random(msg: Message):
    """Handle random content command"""
    if msg.from_user and should_check_membership(msg.from_user.id):
        if not check_membership(msg.from_user.id):
            await send_membership_reminder(msg.chat.id, msg.from_user.id, msg.from_user.full_name)
            return

    logger.info("Random command requested")

    await bot.send_chat_action(msg.chat.id, action="upload_photo")

    try:
        await send_random_selection(msg.chat.id)
    except Exception as e:
        logger.error(f"Random command error: {e}")



@dp.message(Command("privacy"))
async def cmd_privacy(msg: Message):
    """Handle privacy mode command (owner only)"""
    global privacy_mode

    if not msg.from_user:
        return

    user_id = msg.from_user.id
    full_name = msg.from_user.full_name if msg.from_user else "Unknown User"

    logger.info(f"🔒 Privacy command attempted by {full_name}")

    if user_id != OWNER_ID:
        logger.info(f"🚫 Non-owner attempted privacy command | User ID: {user_id}")
        return

    await bot.send_chat_action(msg.chat.id, ChatAction.TYPING)

    current_mode = privacy_mode
    mode_emoji = "🔓" if current_mode == "public" else "🔒"
    mode_text = "Public" if current_mode == "public" else "Normal (Membership Required)"

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="🔓 Set Public Mode" if current_mode == "normal" else "🔓 Public Mode ✓", 
                callback_data="privacy_public"
            )
        ],
        [
            InlineKeyboardButton(
                text="🔒 Set Normal Mode" if current_mode == "public" else "🔒 Normal Mode ✓", 
                callback_data="privacy_normal"
            )
        ],
        [
            InlineKeyboardButton(text="📊 View Status", callback_data="privacy_status")
        ]
    ])

    privacy_text = f"""
🔐 <b>Privacy Mode Settings</b>

<b>Current Mode:</b> {mode_emoji} <b>{mode_text}</b>

<blockquote>╭─<b> 🔓 Public Mode</b>
├─ Everyone can use the bot
├─ No membership requirements
╰─ Works in groups and private chats</blockquote>

<blockquote>╭─<b> 🔒 Normal Mode</b>
├─ Membership verification required
├─ Users must join channel & group
╰─ Default secure behavior</blockquote>

<b>👑 Owner always has full access regardless of mode</b>
"""

    await msg.answer(privacy_text, reply_markup=keyboard)
    logger.info(f"✅ Privacy settings sent to owner")

@dp.message(F.text == "/ping")
async def ping_command(msg: Message):
    """Respond with latency - works for everyone, replies in groups, direct message in private"""
    user_id = msg.from_user.id if msg.from_user else 0
    username = msg.from_user.username if msg.from_user else "Unknown"
    full_name = msg.from_user.full_name if msg.from_user else "Unknown User"
    chat_title = msg.chat.title or msg.chat.first_name or "" if msg.chat else ""
    chat_type = msg.chat.type if msg.chat else "unknown"
    chat_id = msg.chat.id if msg.chat else 0

    logger.info(f"📥 /ping received | Name: {full_name} | Username: @{username} | User ID: {user_id} | Chat: {chat_title} ({chat_type}) | Chat ID: {chat_id}")

    try:
        start = time.perf_counter()

        if msg.chat.type == "private":
            response = await msg.answer("🛰️ Pinging...")
        else:
            response = await msg.reply("🛰️ Pinging...")

        end = time.perf_counter()
        latency_ms = (end - start) * 1000

        await response.edit_text(
            f"🏓 <a href='https://t.me/SoulMeetsHQ'>Pong!</a> {latency_ms:.2f}ms",
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=True
        )

        logger.info(f"✅ Pong sent | Latency: {latency_ms:.2f}ms | Name: {full_name} | Username: @{username} | User ID: {user_id} | Chat: {chat_title} ({chat_type}) | Chat ID: {chat_id}")

    except Exception as e:
        logger.error(f"❌ /ping failed | Name: {full_name} | Username: @{username} | User ID: {user_id} | Chat ID: {chat_id} | Error: {str(e)}")

@dp.message(F.chat.type == "private")
async def handle_live_search(msg: Message):
    """Handle live search in private messages"""
    if msg.from_user and should_check_membership(msg.from_user.id):
        if not check_membership(msg.from_user.id):
            await send_membership_reminder(msg.chat.id, msg.from_user.id, msg.from_user.full_name)
            return

    if not msg.text:
        return

    if msg.text.startswith('/'):
        return

    search_text = msg.text.strip()
    if not search_text:
        return

    words = search_text.split()
    if len(words) == 1:
        search_query = words[0].lower()

        if search_query in ANIME_COMMANDS:
            await send_media_selection(search_query, msg.chat.id)
            return

    guidance_text = f"""
🔍 <b>Live Search Mode</b> 💫

<i>Searching for:</i> <b>"{search_text}"</b>

<blockquote>╭─ 🌟 <b>Search Tips:</b>
├─ Use character names: "sakura"
├─ Try anime names: "naruto", "bleach"
├─ Use underscores: "yor_forger"
╰─ Combine tags: "big_breasts"</blockquote>

<blockquote>╭─ 💡 <b>Popular searches:</b>
├─ Character names from any anime
├─ Series names with specific tags
╰─ Art styles like "anime", "manga", "3d"</blockquote>

⏳ <i>Searching live from internet...</i>
"""

    guidance_msg = await msg.answer(guidance_text)

    post = await search_rule34_live(search_text, "image")

    if not post and " " in search_text:
        alt_search = search_text.replace(" ", "_")
        post = await search_rule34_live(alt_search, "image")

    if not post and len(search_text.split()) > 1:
        first_word = search_text.split()[0]
        post = await search_rule34_live(first_word, "image")

    if not post and len(search_text.split()) > 1:
        last_word = search_text.split()[-1]
        post = await search_rule34_live(last_word, "image")

    if not post:
        clean_name = search_text.replace(" uzumaki", "").replace(" uchiha", "").replace(" hyuga", "").replace(" kamado", "").replace(" kuchiki", "")
        if clean_name != search_text:
            post = await search_rule34_live(clean_name, "image")

    if not post:
        no_results_text = f"""
🔍 <b>No Results Found</b> 😔

<i>Searched for:</i> <b>"{search_text}"</b>

<blockquote>╭─ 💡 <b>Try these instead:</b>
├─ Use underscores: "{search_text.replace(' ', '_')}"
├─ Try character first name only
├─ Check spelling of character names
╰─ Use /random for surprise content</blockquote>

<blockquote>╭─ 🌸 <b>Or try these popular characters:</b>
├─ hinata, sakura, tsunade (Naruto)
├─ rukia, orihime, yoruichi (Bleach)
╰─ mikasa, annie, historia (AOT)</blockquote>
"""
        await bot.edit_message_text(
            text=no_results_text,
            chat_id=msg.chat.id,
            message_id=guidance_msg.message_id
        )
        return

    try:
        await bot.delete_message(msg.chat.id, guidance_msg.message_id)

        keyboard = create_search_selection_keyboard(search_text)
        caption = f"🔍 <b>Search Result</b> ✨\n\n💫 Found: <i>{search_text}</i>\n\n✨ What would you like to see?"

        await bot.send_chat_action(msg.chat.id, action="upload_photo")

        await bot.send_photo(
            chat_id=msg.chat.id,
            photo=post['url'],
            caption=caption,
            reply_markup=keyboard,
            has_spoiler=True
        )
        logger.info(f"Live search selection sent for: {search_text}")
    except Exception as e:
        logger.error(f"Live search send error: {e}")
        pass

@dp.callback_query()
async def handle_callbacks(callback: CallbackQuery):
    """Handle all callback queries with membership verification for the new media selection workflow"""
    logger.info(f"Callback received: {callback.data}")

    if not callback.data or not callback.message:
        await callback.answer("Invalid button")
        return

    if callback.data == "check_membership":
        user_id = callback.from_user.id
        if check_membership(user_id):
            await callback.answer("🎀 Yay! Welcome to our loving family, sweetheart! 💖", show_alert=True)
            try:
                response_text = (
    "🌸 <b>You're now officially part of our little world!</b> 💕\n\n"
    "🥰 I'm really happy to have you here. You can now enjoy all the special features and content waiting for you.\n\n"
    "<blockquote><b><i>I can't wait to share my favorite anime moments with you, sweetheart 🌺</i></b></blockquote>\n\n"
    "✨ Type <b>/start</b> to begin your journey with me! 🎀"
        )

                if callback.message.content_type == "photo":
                    await bot.edit_message_caption(
                        caption=response_text,
                        chat_id=callback.message.chat.id,
                        message_id=callback.message.message_id,
                        parse_mode="HTML"
                    )
                else:
                    await bot.edit_message_text(
                        text=response_text,
                        chat_id=callback.message.chat.id,
                        message_id=callback.message.message_id,
                        parse_mode="HTML"
                    )
            except Exception as e:
                logger.error(f"❌ Failed to edit membership message: {e}")
        else:
            await callback.answer("💘 You're not part of our cozy little family yet. Come join us, we're waiting with open arms 💅", show_alert=True)
        return

    if callback.data.startswith('privacy_'):
        global privacy_mode

        if callback.from_user.id != OWNER_ID:
            await callback.answer("⛔ This command is restricted.", show_alert=True)
            return

        if callback.data == "privacy_public":
            privacy_mode = "public"
            await callback.answer("🔓 Bot set to Public Mode - Everyone can use it now!", show_alert=True)
            logger.info(f"👑 Owner set bot to PUBLIC mode")

        elif callback.data == "privacy_normal":
            privacy_mode = "normal"
            await callback.answer("🔒 Bot set to Normal Mode - Membership required!", show_alert=True)
            logger.info(f"👑 Owner set bot to NORMAL mode")

        elif callback.data == "privacy_status":
            mode_text = "Public (Everyone)" if privacy_mode == "public" else "Normal (Membership Required)"
            await callback.answer(f"📊 Current mode: {mode_text}", show_alert=True)
            return

        current_mode = privacy_mode
        mode_emoji = "🔓" if current_mode == "public" else "🔒"
        mode_text = "Public" if current_mode == "public" else "Normal (Membership Required)"

        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🔓 Set Public Mode" if current_mode == "normal" else "🔓 Public Mode ✓", 
                    callback_data="privacy_public"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🔒 Set Normal Mode" if current_mode == "public" else "🔒 Normal Mode ✓", 
                    callback_data="privacy_normal"
                )
            ],
            [
                InlineKeyboardButton(text="📊 View Status", callback_data="privacy_status")
            ]
        ])

        privacy_text = f"""
🔐 <b>Privacy Mode Settings</b>

<b>Current Mode:</b> {mode_emoji} <b>{mode_text}</b>

<blockquote>╭─<b> 🔓 Public Mode</b>
├─ Everyone can use the bot
├─ No membership requirements
╰─ Works in groups and private chats</blockquote>

<blockquote>╭─<b> 🔒 Normal Mode</b>
├─ Membership verification required
├─ Users must join channel & group
╰─ Default secure behavior</blockquote>

<b>👑 Owner always has full access regardless of mode</b>
"""

        try:
            await bot.edit_message_text(
                text=privacy_text,
                chat_id=callback.message.chat.id,
                message_id=callback.message.message_id,
                reply_markup=keyboard
            )
        except Exception as e:
            logger.error(f"❌ Failed to edit privacy message: {e}")
        return

    if callback.from_user and should_check_membership(callback.from_user.id):
        if not check_membership(callback.from_user.id):
            await callback.answer("🥀️ You were here, part of our little family. Come back so we can continue this beautiful journey together ❤️‍🩹", show_alert=True)

            await send_membership_reminder(
                chat_id=callback.message.chat.id,
                user_id=callback.from_user.id,
                user_name=callback.from_user.full_name
            )
            return

    data_parts = callback.data.split("_")
    action = data_parts[0]

    if len(data_parts) < 2:
        await callback.answer("Invalid button format")
        return

    if action == "select":
        media_type = data_parts[1]
        target = data_parts[2]

        logger.info(f"Media type {media_type} selected for: {target}")

        if target == "random":
            await callback.answer(f"💞 Loading random {media_type}...")
            try:
                await send_random_media(
                    chat_id=callback.message.chat.id,
                    message_id=callback.message.message_id,
                    edit_mode=True,
                    media_type=media_type,
                    page=1
                )
                logger.info(f"Successfully loaded random {media_type}")
            except Exception as e:
                logger.error(f"Random selection error: {e}")
                await callback.answer("Failed to load random content", show_alert=True)
        elif target in ANIME_COMMANDS:
            await callback.answer(f"💞 Loading {media_type}...")
            try:
                await send_anime_media(
                    anime_name=target,
                    chat_id=callback.message.chat.id,
                    message_id=callback.message.message_id,
                    edit_mode=True,
                    media_type=media_type,
                    page=1
                )
                logger.info(f"Successfully loaded {media_type} for {target}")
            except Exception as e:
                logger.error(f"Anime selection error: {e}")
                await callback.answer("Failed to load anime content", show_alert=True)
        else:
            search_query = target.replace("_", " ")
            await callback.answer(f"💞 Loading {media_type} for '{search_query}'...")
            try:
                await send_search_media(
                    search_query=search_query,
                    chat_id=callback.message.chat.id,
                    message_id=callback.message.message_id,
                    edit_mode=True,
                    media_type=media_type,
                    page=1
                )
                logger.info(f"Successfully loaded search {media_type} for '{search_query}'")
            except Exception as e:
                logger.error(f"Search selection error: {e}")
                await callback.answer(f"Failed to load search content", show_alert=True)

    elif action in ["update", "next"]:
        anime_name = data_parts[1]
        media_type = data_parts[2] if len(data_parts) > 2 else "image"
        page = int(data_parts[3]) if len(data_parts) > 3 else 1

        if action == "update":
            logger.info(f"Update button pressed for: {anime_name} ({media_type}, page {page})")
            await callback.answer("✨ Getting fresh content...")

            try:
                if anime_name == "random":
                    await send_random_media(
                        chat_id=callback.message.chat.id,
                        message_id=callback.message.message_id,
                        edit_mode=True,
                        media_type=media_type,
                        page=page
                    )
                elif anime_name in ANIME_COMMANDS:
                    await send_anime_media(
                        anime_name=anime_name,
                        chat_id=callback.message.chat.id,
                        message_id=callback.message.message_id,
                        edit_mode=True,
                        media_type=media_type,
                        page=page
                    )
                else:
                    search_query = anime_name.replace("_", " ")
                    await send_search_media(
                        search_query=search_query,
                        chat_id=callback.message.chat.id,
                        message_id=callback.message.message_id,
                        edit_mode=True,
                        media_type=media_type,
                        page=page
                    )
                logger.info(f"Successfully updated {media_type} for {anime_name}")
            except Exception as e:
                logger.error(f"Update callback error: {e}")

        elif action == "next":
            logger.info(f"Next button pressed for: {anime_name} ({media_type}, page {page})")
            await callback.answer("💞 Loading more content...")

            try:
                if anime_name == "random":
                    await send_random_media(
                        chat_id=callback.message.chat.id,
                        edit_mode=False,
                        media_type=media_type,
                        page=page + 1
                    )
                elif anime_name in ANIME_COMMANDS:
                    await send_anime_media(
                        anime_name=anime_name,
                        chat_id=callback.message.chat.id,
                        edit_mode=False,
                        media_type=media_type,
                        page=page + 1
                    )
                else:
                    search_query = anime_name.replace("_", " ")
                    await send_search_media(
                        search_query=search_query,
                        chat_id=callback.message.chat.id,
                        edit_mode=False,
                        media_type=media_type,
                        page=page + 1
                    )
                logger.info(f"Successfully sent next {media_type} for {anime_name}")
            except Exception as e:
                logger.error(f"Next callback error: {e}")

    elif callback.data == "back_to_menu":
        logger.info("Back to menu button pressed")
        await callback.answer("💕 Returning to main menu...")

        user_name = callback.from_user.full_name if callback.from_user else "User"
        user_id = callback.from_user.id if callback.from_user else ""

        welcome_text = f"""
💖 <b>Hey there</b> <a href="tg://user?id={user_id}"><b>{user_name}</b></a>, <b>Welcome!</b>

<b>Makima</b> here, to brighten your day! 🌸

🎀 Enjoy <b>150+ anime commands</b> and <b>amazing content</b> from <b>22+ series.</b> All super easy to explore!

<blockquote><i>💌 Use any anime command to begin your journey!</i></blockquote>
"""

        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="💟 Updates", url="https://t.me/WorkGlows"),
                InlineKeyboardButton(text="Support 💞", url="https://t.me/SoulMeetsHQ")
            ],
            [
                InlineKeyboardButton(text="💗️ Add Me To Your Group 💗️", url=f"https://t.me/{(await bot.get_me()).username}?startgroup=true&admin=delete_messages+ban_users+invite_users+pin_messages+manage_chat+manage_video_chats+post_messages+edit_messages+manage_topics+add_admins")
            ]
        ])

        try:
            await bot.edit_message_text(
                text=welcome_text,
                chat_id=callback.message.chat.id,
                message_id=callback.message.message_id,
                reply_markup=keyboard
            )
            logger.info("Successfully returned to main menu")
        except Exception as e:
            logger.error(f"Back to menu error: {e}")
            await callback.answer("Failed to return to menu", show_alert=True)
        return

    elif action == "back":
        target = data_parts[1]
        logger.info(f"Back button pressed for: {target}")
        await callback.answer("💕 Going back to selection...")

        try:
            if target == "random":
                keyboard = create_random_selection_keyboard()
                caption = "🎲 <b>Random Content</b> ✨\n\n💫 What would you like to see?"
            elif target in ANIME_COMMANDS:
                anime_data = ANIME_COMMANDS.get(target)
                keyboard = create_media_selection_keyboard(target)
                if anime_data:
                    caption = f"💖 {anime_data['title']}\n\n✨ What would you like to see?"
                else:
                    caption = f"💖 {target.title()}\n\n✨ What would you like to see?"
            else:
                search_query = target.replace("_", " ")
                keyboard = create_search_selection_keyboard(search_query)
                caption = f"🔍 <b>Search Result</b> ✨\n\n💫 Found: <i>{search_query}</i>\n\n✨ What would you like to see?"

            await bot.edit_message_caption(
                chat_id=callback.message.chat.id,
                message_id=callback.message.message_id,
                caption=caption,
                reply_markup=keyboard
            )
            logger.info(f"Successfully returned to media selection for {target}")
        except Exception as e:
            logger.error(f"Back button error: {e}")
            await callback.answer("Failed to go back", show_alert=True)


    else:
        await callback.answer("Unknown button")

def log_performance_stats():
    """Log current performance statistics"""
    logger.info(f"📊 Performance Stats:")
    logger.info(f"   Content cache size: {len(sent_content_ids)}")
    logger.info(f"   User offsets tracked: {len(user_offsets)}")
    logger.info(f"   Recent API requests: {len(api_request_times)}")

async def main():

    threading.Thread(target=start_dummy_server, daemon=True).start()

    logger.info("🌸 Starting Makima - Your Anime Companion...")

    try:
        await bot.set_my_commands(BOT_COMMANDS)
        logger.info(f"✨ Beautiful commands registered: {len(BOT_COMMANDS)} commands set")
        logger.info("💖 Makima is ready to serve! Press Ctrl+C to stop.")

        log_performance_stats()

        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f"Failed to start bot: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
