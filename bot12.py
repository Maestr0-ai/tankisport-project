import datetime
import json
import logging
import sys
import re
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

try:
    import aiohttp
    import discord
    from discord.ext import commands, tasks
    from discord.ui import View, Button
except ImportError as e:
    print(f"Ошибка: Необходимый модуль не установлен. Установите его с помощью 'pip install {e.name}'. Выход.")
    sys.exit(1)

# Настройка
TOKEN = os.getenv("DISCORD_TOKEN")
if not TOKEN:
    raise RuntimeError("❌ DISCORD_TOKEN не найден. Проверь .env файл.")
CHANNEL_ID = 1369812225883246662
TEAM_URLS = [
    "https://tankisport.com/api/teams/show/15818",
    "https://tankisport.com/api/teams/show/14834",
    "https://tankisport.com/api/teams/show/15672",
    "https://tankisport.com/api/teams/show/15601",
    "https://tankisport.com/api/teams/show/15209",
    "https://tankisport.com/api/teams/show/15923",
    "https://tankisport.com/api/teams/show/15204",
    "https://tankisport.com/api/teams/show/15919",
    "https://tankisport.com/api/teams/show/15846",
    "https://tankisport.com/api/teams/show/15932",
    "https://tankisport.com/api/teams/show/15783",
    "https://tankisport.com/api/teams/show/15917",
    "https://tankisport.com/api/teams/show/15854",
    "https://tankisport.com/api/teams/show/15702",
    "https://tankisport.com/api/teams/show/14286",
    "https://tankisport.com/api/teams/show/11093",
    "https://tankisport.com/api/teams/show/15916",
    "https://tankisport.com/api/teams/show/14679",
    "https://tankisport.com/api/teams/show/15719",
    "https://tankisport.com/api/teams/show/14062",
    "https://tankisport.com/api/teams/show/14357",
    "https://tankisport.com/api/teams/show/15886",
    "https://tankisport.com/api/teams/show/15525",
    "https://tankisport.com/api/teams/show/15703",
    "https://tankisport.com/api/teams/show/15819",
    "https://tankisport.com/api/teams/show/15941",
    "https://tankisport.com/api/teams/show/12945",
    "https://tankisport.com/api/teams/show/15401",
    "https://tankisport.com/api/teams/show/15745",
    "https://tankisport.com/api/teams/show/15330",
    "https://tankisport.com/api/teams/show/15834",
    "https://tankisport.com/api/teams/show/15320",
    "https://tankisport.com/api/teams/show/15504",
    "https://tankisport.com/api/teams/show/15786",
    "https://tankisport.com/api/teams/show/15524",
    "https://tankisport.com/api/teams/show/15107",
    "https://tankisport.com/api/teams/show/15772",
    "https://tankisport.com/api/teams/show/15963",
    "https://tankisport.com/api/teams/show/15284",
    "https://tankisport.com/api/teams/show/15793",
    "https://tankisport.com/api/teams/show/15035",
    "https://tankisport.com/api/teams/show/13683",
    "https://tankisport.com/api/teams/show/15891",
    "https://tankisport.com/api/teams/show/15267",
    "https://tankisport.com/api/teams/show/15698",
    "https://tankisport.com/api/teams/show/15520",
    "https://tankisport.com/api/teams/show/14727",
    "https://tankisport.com/api/teams/show/14821",
    "https://tankisport.com/api/teams/show/15369",
    "https://tankisport.com/api/teams/show/14434",
    "https://tankisport.com/api/teams/show/15367",
    "https://tankisport.com/api/teams/show/15309",
    "https://tankisport.com/api/teams/show/15276",
    "https://tankisport.com/api/teams/show/15404",
    "https://tankisport.com/api/teams/show/15477",
    "https://tankisport.com/api/teams/show/15693",
    "https://tankisport.com/api/teams/show/14576",
    "https://tankisport.com/api/teams/show/11389",
    "https://tankisport.com/api/teams/show/15481",
    "https://tankisport.com/api/teams/show/15024",
    "https://tankisport.com/api/teams/show/15668",
    "https://tankisport.com/api/teams/show/15674",
    "https://tankisport.com/api/teams/show/15055",
    "https://tankisport.com/api/teams/show/15317",
    "https://tankisport.com/api/teams/show/15814",
    "https://tankisport.com/api/teams/show/15400",
    "https://tankisport.com/api/teams/show/15803",
    "https://tankisport.com/api/teams/show/14727",
    "https://tankisport.com/api/teams/show/14290",
    "https://tankisport.com/api/teams/show/15316",
    "https://tankisport.com/api/teams/show/13100",
    "https://tankisport.com/api/teams/show/15778",
    "https://tankisport.com/api/teams/show/14978",
    "https://tankisport.com/api/teams/show/15806",
    "https://tankisport.com/api/teams/show/15382",
    "https://tankisport.com/api/teams/show/15548",
    "https://tankisport.com/api/teams/show/15506",
    "https://tankisport.com/api/teams/show/15201",
    "https://tankisport.com/api/teams/show/15496",
    "https://tankisport.com/api/teams/show/15624",
    "https://tankisport.com/api/teams/show/15404",
    "https://tankisport.com/api/teams/show/15855",
    "https://tankisport.com/api/teams/show/8779",
    "https://tankisport.com/api/teams/show/15659",
    "https://tankisport.com/api/teams/show/15370",
    "https://tankisport.com/api/teams/show/15094",
    "https://tankisport.com/api/teams/show/15942",
    "https://tankisport.com/api/teams/show/15939",
    "https://tankisport.com/api/teams/show/15938",
    "https://tankisport.com/api/teams/show/15858",
    "https://tankisport.com/api/teams/show/15920",
    "https://tankisport.com/api/teams/show/15925",
    "https://tankisport.com/api/teams/show/15618",
    "https://tankisport.com/api/teams/show/15014",
    "https://tankisport.com/api/teams/show/15664",
    "https://tankisport.com/api/teams/show/15511",
    "https://tankisport.com/api/teams/show/15259",
    "https://tankisport.com/api/teams/show/15493",
    "https://tankisport.com/api/teams/show/15505",
    "https://tankisport.com/api/teams/show/15474",
    "https://tankisport.com/api/teams/show/14993",
    "https://tankisport.com/api/teams/show/15544",
    "https://tankisport.com/api/teams/show/14985",
    "https://tankisport.com/api/teams/show/15327",
    "https://tankisport.com/api/teams/show/15954",
    "https://tankisport.com/api/teams/show/15882",
    "https://tankisport.com/api/teams/show/15885",
    "https://tankisport.com/api/teams/show/15372",
    "https://tankisport.com/api/teams/show/15887",
    "https://tankisport.com/api/teams/show/15889",
    "https://tankisport.com/api/teams/show/14865",
    "https://tankisport.com/api/teams/show/15122",
    "https://tankisport.com/api/teams/show/14098",
    "https://tankisport.com/api/teams/show/7525",
    "https://tankisport.com/api/teams/show/14655",
    "https://tankisport.com/api/teams/show/15635",
    "https://tankisport.com/api/teams/show/13318",
    "https://tankisport.com/api/teams/show/15816",
    "https://tankisport.com/api/teams/show/14291",
    "https://tankisport.com/api/teams/show/15873",
    "https://tankisport.com/api/teams/show/15125",
    "https://tankisport.com/api/teams/show/15974",
    "https://tankisport.com/api/teams/show/15303",
    "https://tankisport.com/api/teams/show/15787",
    "https://tankisport.com/api/teams/show/15329",
    "https://tankisport.com/api/teams/show/15877",
    "https://tankisport.com/api/teams/show/15976",
    "https://tankisport.com/api/teams/show/15966",
    "https://tankisport.com/api/teams/show/15977",
    "https://tankisport.com/api/teams/show/15892",
    "https://tankisport.com/api/teams/show/15983",
    "https://tankisport.com/api/teams/show/15200",
    "https://tankisport.com/api/teams/show/15890",
    "https://tankisport.com/api/teams/show/15378",
    "https://tankisport.com/api/teams/show/14098",
    "https://tankisport.com/api/teams/show/15889",
    "https://tankisport.com/api/teams/show/15372",
    "https://tankisport.com/api/teams/show/15883",
    "https://tankisport.com/api/teams/show/15627",
    "https://tankisport.com/api/teams/show/15878",
    "https://tankisport.com/api/teams/show/14084",
    "https://tankisport.com/api/teams/show/14850",
    "https://tankisport.com/api/teams/show/15987",
    "https://tankisport.com/api/teams/show/15981",
    "https://tankisport.com/api/teams/show/14582",
    "https://tankisport.com/api/teams/show/15204",
    "https://tankisport.com/api/teams/show/15992",
    "https://tankisport.com/api/teams/show/15993",
    "https://tankisport.com/api/teams/show/16043",
    "https://tankisport.com/api/teams/show/15595",
    "https://tankisport.com/api/teams/show/15995",
    "https://tankisport.com/api/teams/show/16000",
    "https://tankisport.com/api/teams/show/15985",
    "https://tankisport.com/api/teams/show/16001",
    "https://tankisport.com/api/teams/show/15964",
    "https://tankisport.com/api/teams/show/15997",
    "https://tankisport.com/api/teams/show/15993",
    "https://tankisport.com/api/teams/show/16003",
    "https://tankisport.com/api/teams/show/16005",
    "https://tankisport.com/api/teams/show/14044",
    "https://tankisport.com/api/teams/show/15964",
    "https://tankisport.com/api/teams/show/16011",
    "https://tankisport.com/api/teams/show/15896",
    "https://tankisport.com/api/teams/show/16014",
    "https://tankisport.com/api/teams/show/16011",
    "https://tankisport.com/api/teams/show/16031",
    "https://tankisport.com/api/teams/show/14057",
    "https://tankisport.com/api/teams/show/16042",
    "https://tankisport.com/api/teams/show/15925",
    "https://tankisport.com/api/teams/show/16045",
    "https://tankisport.com/api/teams/show/16044",
    "https://tankisport.com/api/teams/show/16032",
    "https://tankisport.com/api/teams/show/16046",
    "https://tankisport.com/api/teams/show/14726",
    "https://tankisport.com/api/teams/show/16016",
    "https://tankisport.com/api/teams/show/16047",
    "https://tankisport.com/api/teams/show/16048",
    "https://tankisport.com/api/teams/show/16050",
    "https://tankisport.com/api/teams/show/16062",
    "https://tankisport.com/api/teams/show/15808",
    "https://tankisport.com/api/teams/show/16054",
    "https://tankisport.com/api/teams/show/11753",
    "https://tankisport.com/api/teams/show/14892",
    "https://tankisport.com/api/teams/show/16056",
    "https://tankisport.com/api/teams/show/16063",
    "https://tankisport.com/api/teams/show/16051",
    "https://tankisport.com/api/teams/show/16052",
    "https://tankisport.com/api/teams/show/15999",
    "https://tankisport.com/api/teams/show/15746",
    "https://tankisport.com/api/teams/show/15494"
]
TOURNAMENT_URL = "https://tankisport.com/api/tournaments/show/842"

# Хранилище данных
TEAM_MAPPING = {}
team_name_history = {}
tournament_progress = {}

# Список ID команд "Empty slot" и их названий
EMPTY_SLOT_IDS = {6798, 6799, 6800, 6801, 6802, 6803, 6804, 6805, 6806}
EMPTY_SLOT_NAMES = {
    6798: "Empty slot",
    6799: "Empty slot2",
    6800: "Empty slot3",
    6801: "Empty slot4",
    6802: "Empty slot5",
    6803: "Empty slot6",
    6804: "Empty slot7",
    6805: "Empty slot8",
    6806: "Empty slot9"
}

# Количество матчей по раундам
ROUND_MATCHES = {1: 16, 2: 16, 3: 16, 4: 16, 5: 14, 6: 10, 7: 5}
TOTAL_MATCHES = 93

# Настройка логирования
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Настройка бота
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Хранилище данных
team_states = {}
tournament_states = {}

# Загрузка данных из файлов
try:
    with open("team_data.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        team_states = data.get("team_states", {})
        tournament_states = data.get("tournament_states", {})
        for state in team_states.values():
            if "players" not in state:
                state["players"] = {}
            if "last_updated" not in state:
                state["last_updated"] = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=3))).isoformat()
        for state in tournament_states.values():
            if "notified_results" in state and not isinstance(state["notified_results"], set):
                state["notified_results"] = set(state["notified_results"])
            if "notified_rounds" in state and not isinstance(state["notified_rounds"], set):
                state["notified_rounds"] = set(state["notified_rounds"])
            if "notified_reminders" in state and not isinstance(state["notified_reminders"], set):
                state["notified_reminders"] = set(state["notified_reminders"])
            if "notified_start_notifications" in state and not isinstance(state["notified_start_notifications"], set):
                state["notified_start_notifications"] = set(state["notified_start_notifications"])
            if "notified_new_rounds" in state and not isinstance(state["notified_new_rounds"], set):
                state["notified_new_rounds"] = set(state["notified_new_rounds"])
            if "notified_new_matches" not in state:
                state["notified_new_matches"] = set()
except FileNotFoundError:
    team_states = {}
    tournament_states = {}

try:
    with open("team_history.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        TEAM_MAPPING.update(data.get("TEAM_MAPPING", {}))
        team_name_history.update(data.get("team_name_history", {}))
    logger.info(f"Загружено TEAM_MAPPING: {len(TEAM_MAPPING)} команд")
except FileNotFoundError:
    logger.info("Файл team_history.json не найден, TEAM_MAPPING остаётся пустым")

try:
    with open("tournament_progress.json", "r", encoding="utf-8") as f:
        tournament_progress.update(json.load(f))
    logger.info(f"Загружено tournament_progress: {len(tournament_progress)} турниров")
except FileNotFoundError:
    logger.info("Файл tournament_progress.json не найден, tournament_progress остаётся пустым")

# Вспомогательные функции
def datetime_to_str(obj):
    if isinstance(obj, datetime.datetime):
        return obj.isoformat()
    elif isinstance(obj, set):
        return list(obj)
    logger.debug(f"⚠️ Неизвестный тип для сериализации: {type(obj)}, объект: {obj}. Преобразование в строку.")
    return str(obj)

def parse_iso_date(date_str):
    try:
        dt = datetime.datetime.fromisoformat(date_str.replace('Z', ''))
        return dt.replace(tzinfo=datetime.timezone(datetime.timedelta(hours=3)))
    except Exception:
        return datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=3)))

def get_progress_bar(progress_percent):
    filled = int(progress_percent // 5)  # Каждый блок = 5%
    return "".join("■" if i < filled else "□" for i in range(20))

def get_tournament_stages(tournament_id, current_round=None):
    stages = []
    match_results = tournament_states.get(tournament_id, {}).get("match_results", {})
    for round_num in range(1, 8):
        completed_matches = len(match_results.get(str(round_num), set()))
        total_matches = ROUND_MATCHES.get(round_num, 0)
        if completed_matches >= total_matches and total_matches > 0:
            stages.append(f"- **Р{round_num}**: ✅ **Завершено** ({completed_matches}/{total_matches} матчей)")
        elif completed_matches > 0 or (current_round and round_num == current_round):
            stages.append(f"- **Р{round_num}**: ▶ **В процессе** ({completed_matches}/{total_matches} матчей)")
            if round_num < 7:
                stages.append(f"- **Р{round_num + 1}–Р7**: ⏳ **Ожидаются**")
            break
        else:
            stages.append(f"- **Р{round_num}–Р7**: ⏳ **Ожидаются**")
            break
    return stages

def replace_team_ids_with_names(result_str):
    """Заменяем Team_<ID> на реальные названия из TEAM_MAPPING."""
    def replace_team(match):
        team_id = match.group(1)
        return TEAM_MAPPING.get(team_id, f"Team_{team_id}")
    
    # Регулярное выражение для поиска Team_<ID>
    pattern = r'\bTeam_(\d+)\b'
    return re.sub(pattern, replace_team, result_str)

# Класс для пагинации
class Paginator(View):
    def __init__(self, pages):
        super().__init__(timeout=None)  # Кнопки активны всегда
        self.pages = pages
        self.current_page = 0
        self.previous.disabled = True
        if len(pages) == 1:
            self.next.disabled = True

    @discord.ui.button(label="⬅️", style=discord.ButtonStyle.secondary)
    async def previous(self, interaction: discord.Interaction, button: Button):
        self.current_page -= 1
        self.previous.disabled = (self.current_page == 0)
        self.next.disabled = (self.current_page == len(self.pages) - 1)
        await interaction.response.edit_message(embed=self.pages[self.current_page], view=self)

    @discord.ui.button(label="➡️", style=discord.ButtonStyle.secondary)
    async def next(self, interaction: discord.Interaction, button: Button):
        self.current_page += 1
        self.previous.disabled = (self.current_page == 0)
        self.next.disabled = (self.current_page == len(self.pages) - 1)
        await interaction.response.edit_message(embed=self.pages[self.current_page], view=self)

    @discord.ui.button(label="🏠", style=discord.ButtonStyle.primary)
    async def home(self, interaction: discord.Interaction, button: Button):
        self.current_page = 0
        self.previous.disabled = True
        self.next.disabled = (len(self.pages) == 1)
        await interaction.response.edit_message(embed=self.pages[self.current_page], view=self)

async def fetch_team_data(url, retries=3):
    headers = {"User-Agent": "Mozilla/5.0", "Accept": "application/json", "Cache-Control": "no-cache"}
    logger.debug(f"Проверка URL команды: {url}")
    for attempt in range(retries):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=30)) as response:
                    if response.status == 200:
                        data = await response.json()
                        logger.debug(f"Успешно получены данные для {url}")
                        return data
                    else:
                        logger.error(f"❌ Ошибка API: код {response.status} для URL {url} (попытка {attempt + 1}/{retries})")
        except Exception as e:
            logger.error(f"❌ Ошибка запроса к API: {e} для URL {url} (попытка {attempt + 1}/{retries})")
        if attempt < retries - 1:
            await asyncio.sleep(2)  # Пауза перед повторной попыткой
    return None

async def fetch_tournament_data(url):
    headers = {"User-Agent": "Mozilla/5.0", "Accept": "application/json", "Cache-Control": "no-cache"}
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=30)) as response:
                if response.status == 200:
                    data = await response.json()
                    logger.info(f"📥 Получены данные турнира по URL {url}: {len(data.get('data', {}).get('teams', []))} команд")
                    return data
                else:
                    logger.error(f"❌ Ошибка API: код {response.status} для URL {url}")
                    return None
    except Exception as e:
        logger.error(f"❌ Ошибка запроса к API: {e} для URL {url}")
        return None

async def check_team_updates(channel):
    global team_states, TEAM_MAPPING, team_name_history
    now_msk = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=3)))
    logger.info("Начало check_team_updates")
    
    # Параллельная загрузка данных команд
    results = await asyncio.gather(
        *[fetch_team_data(url) for url in TEAM_URLS],
        return_exceptions=True
    )
    
    success_count = 0
    error_count = 0
    for team_url, team_data in zip(TEAM_URLS, results):
        if isinstance(team_data, Exception) or not team_data or "data" not in team_data:
            logger.error(f"❌ Не удалось получить данные для {team_url}")
            error_count += 1
            continue
        team_id = str(team_data["data"].get("id"))
        team_name = team_data["data"].get("name")
        players = {str(player["id"]): {"name": player["User"].get("username", f"Игрок_{player['id']}"), "wins": player.get("wins", 0)} for player in team_data["data"].get("players", [])}
        last_updated = parse_iso_date(team_data["data"].get("updated_at", now_msk.isoformat()))
        
        if team_id not in team_states:
            team_states[team_id] = {"name": team_name, "players": players, "last_updated": last_updated.isoformat()}
        current_state = team_states[team_id]
        
        if team_id not in TEAM_MAPPING:
            TEAM_MAPPING[team_id] = team_name
            logger.debug(f"Добавлено в TEAM_MAPPING: {team_id} -> {team_name}")
        elif TEAM_MAPPING[team_id] != team_name:
            embed = discord.Embed(title="🔄 Обновление команды!", color=0x00ff00)
            embed.add_field(name="Старое название", value=TEAM_MAPPING[team_id], inline=True)
            embed.add_field(name="Новое название", value=team_name, inline=True)
            embed.set_footer(text=f"─────────────────────────\n🕒 {now_msk.strftime('%d.%m.%Y | %H:%M')} MCK")
            await channel.send(embed=embed)
            if team_id not in team_name_history:
                team_name_history[team_id] = []
            if TEAM_MAPPING[team_id] not in team_name_history[team_id]:
                team_name_history[team_id].append(TEAM_MAPPING[team_id])
            TEAM_MAPPING[team_id] = team_name
        
        if current_state["name"] != team_name:
            if current_state["name"] and current_state["name"] not in team_name_history.get(team_id, []):
                if team_id not in team_name_history:
                    team_name_history[team_id] = []
                team_name_history[team_id].append(current_state["name"])
            embed = discord.Embed(title="🔄 Обновление команды!", color=0x00ff00)
            embed.add_field(name="Старое название", value=current_state["name"] if current_state["name"] else "Не указано", inline=True)
            embed.add_field(name="Новое название", value=team_name, inline=True)
            embed.set_footer(text=f"─────────────────────────\n🕒 {now_msk.strftime('%d.%m.%Y | %H:%M')} MCK")
            await channel.send(embed=embed)
            current_state["name"] = team_name
        
        current_player_ids = set(current_state["players"].keys())
        new_player_ids = set(players.keys())
        for player_id in current_player_ids & new_player_ids:
            if current_state["players"][player_id]["name"] != players[player_id]["name"]:
                old_name = current_state["players"][player_id]["name"]
                new_name = players[player_id]["name"]
                embed = discord.Embed(title="🔄 Изменение ника игрока", color=0x800080)
                embed.add_field(name=f"Команда: {team_name}", value=f"С {old_name} на {new_name}", inline=False)
                embed.set_footer(text=f"─────────────────────────\n🕒 {now_msk.strftime('%d.%m.%Y | %H:%M')} MCK")
                await channel.send(embed=embed)
                current_state["players"][player_id]["name"] = new_name
        
        left_players = current_player_ids - new_player_ids
        for player_id in left_players:
            player_name = current_state["players"][player_id]["name"]
            current_state["players"].pop(player_id)
            player_list = [f"➡ **{p['name']}**" for p in current_state["players"].values()]
            embed = discord.Embed(title="🔄 Обновление состава!", color=0x00ff00)
            embed.add_field(name="⛔ Игрок ушёл:", value=f"**{player_name}** из **{team_name}**", inline=False)
            embed.add_field(name="📋 Актуальный состав:", value='\n'.join(player_list) if player_list else "Нет игроков", inline=False)
            embed.set_footer(text=f"─────────────────────────\n🕒 {now_msk.strftime('%d.%m.%Y | %H:%M')} MCK")
            await channel.send(embed=embed)
        
        new_players = new_player_ids - current_player_ids
        for player_id in new_players:
            player_name = players[player_id]["name"]
            current_state["players"][player_id] = players[player_id]
            player_list = [f"➡ **{p['name']}**" for p in current_state["players"].values()]
            new_player_index = next((i for i, p in enumerate(current_state["players"].values()) if p["name"] == player_name), -1)
            new_player_display = f"➡ ✨ **{player_name}**" if new_player_index == len(player_list) - 1 else f"➡ **{player_name}**"
            player_list_with_new = [f"➡ **{p['name']}**" for p in current_state["players"].values()]
            player_list_with_new[new_player_index] = new_player_display
            embed = discord.Embed(title="🔄 Новый игрок!", color=0x00ff00)
            embed.add_field(name="✅ Игрок присоединился:", value=f"**{player_name}** в **{team_name}**", inline=False)
            embed.add_field(name="📋 Актуальный состав:", value='\n'.join(player_list_with_new), inline=False)
            embed.set_footer(text=f"─────────────────────────\n🕒 {now_msk.strftime('%d.%m.%Y | %H:%M')} MCK")
            await channel.send(embed=embed)
        
        current_state["players"] = players
        current_state["last_updated"] = last_updated.isoformat()
        success_count += 1
        logger.debug(f"Обновлено состояние команды {team_name}: {len(players)} игроков")
    
    logger.info(f"Завершено check_team_updates: успешно обновлено {success_count} команд, ошибок: {error_count}")

async def check_tournament_schedule(channel):
    global tournament_states
    now_msk = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=3)))
    logger.info("Начало check_tournament_schedule")
    tournament_data = await fetch_tournament_data(TOURNAMENT_URL)
    if not tournament_data or "data" not in tournament_data:
        logger.error("Не удалось получить данные турнира")
        return
    tournament_id = str(tournament_data["data"].get("id"))
    if tournament_id not in tournament_states:
        tournament_states[tournament_id] = {
            "last_updated": now_msk.isoformat(),
            "match_results": {},
            "schedule": {},
            "notified_results": set(),
            "notified_rounds": set(),
            "notified_reminders": set(),
            "notified_start_notifications": set(),
            "notified_new_rounds": set(),
            "notified_new_matches": set()
        }
    current_state = tournament_states[tournament_id]
    matches = tournament_data["data"].get("child", [{}])[0].get("matches", [])
    new_schedule = {}

    # Формируем новое расписание и проверяем переносы
    for match in matches:
        match_id = str(match.get("id"))
        round_num = str(match.get("connection", {}).get("stage", 1))
        team1_id = match.get("team1", {}).get("id")
        team2_id = match.get("team2", {}).get("id")
        match_time_str = match.get("date")
        if not team1_id or not team2_id or not match_time_str:
            logger.debug(f"Пропущен матч {match_id}: отсутствуют team1_id, team2_id или date")
            continue
        if match.get("status") != 0 or match.get("result1", 0) > 0 or match.get("result2", 0) > 0 or match.get("winner"):
            continue
        team1_name = EMPTY_SLOT_NAMES.get(team1_id, TEAM_MAPPING.get(str(team1_id), f"Team_{team1_id}"))
        team2_name = EMPTY_SLOT_NAMES.get(team2_id, TEAM_MAPPING.get(str(team2_id), f"Team_{team2_id}"))
        match_time = parse_iso_date(match_time_str)
        match_detail = f"🕗 {match_time.strftime('%H:%M')} — **{team1_name}** 🆚 **{team2_name}**"
        
        new_schedule.setdefault(round_num, []).append({
            "match_id": match_id,
            "time": match_time_str,
            "teams": {"team1_id": team1_id, "team2_id": team2_id},
            "detail": match_detail
        })

    # Проверяем переносы матчей
    for round_num in current_state["schedule"]:
        for existing_match in current_state["schedule"][round_num][:]:
            match_id = existing_match["match_id"]
            old_time = parse_iso_date(existing_match["time"])
            old_date_str = old_time.strftime("%d.%m.%Y")
            old_time_str = old_time.strftime("%H:%M")
            # Ищем матч с тем же ID в новом расписании
            found = False
            for new_round_num, new_matches in new_schedule.items():
                for new_match in new_matches:
                    if new_match["match_id"] == match_id:
                        found = True
                        new_time = parse_iso_date(new_match["time"])
                        new_date_str = new_time.strftime("%d.%m.%Y")
                        new_time_str = new_time.strftime("%H:%M")
                        if new_time != old_time:
                            # Матч перенесён
                            team1_name = EMPTY_SLOT_NAMES.get(existing_match["teams"]["team1_id"], 
                                                              TEAM_MAPPING.get(str(existing_match["teams"]["team1_id"]), f"Team_{existing_match['teams']['team1_id']}"))
                            team2_name = EMPTY_SLOT_NAMES.get(existing_match["teams"]["team2_id"], 
                                                              TEAM_MAPPING.get(str(existing_match["teams"]["team2_id"]), f"Team_{existing_match['teams']['team2_id']}"))
                            embed = discord.Embed(
                                title=f"🔄 Матч перенесён — Раунд {round_num}",
                                color=0xFFA500,
                                timestamp=now_msk
                            )
                            embed.add_field(
                                name="Матч",
                                value=f"**{team1_name}** 🆚 **{team2_name}**",
                                inline=False
                            )
                            embed.add_field(
                                name="Старое время",
                                value=f"{old_date_str} {old_time_str}",
                                inline=True
                            )
                            embed.add_field(
                                name="Новое время",
                                value=f"{new_date_str} {new_time_str}",
                                inline=True
                            )
                            embed.set_footer(text=f"─────────────────────────\n🕒 {now_msk.strftime('%d.%m.%Y | %H:%M')} MCK")
                            await channel.send(embed=embed)
                            logger.info(f"🔔 Уведомление о переносе матча {match_id}: с {old_date_str} {old_time_str} на {new_date_str} {new_time_str}")
                            # Обновляем расписание
                            current_state["schedule"][round_num].remove(existing_match)
                            current_state["schedule"].setdefault(new_round_num, []).append(new_match)
                            # Сохраняем изменения сразу
                            with open("team_data.json", "w", encoding="utf-8") as f:
                                json.dump({"team_states": team_states, "tournament_states": tournament_states}, 
                                         f, indent=4, ensure_ascii=False, default=datetime_to_str)
                        break
                if found:
                    break
            if not found:
                # Матч больше не существует в API, удаляем его из расписания
                current_state["schedule"][round_num].remove(existing_match)
                logger.debug(f"Матч {match_id} удалён из расписания: отсутствует в API")
                with open("team_data.json", "w", encoding="utf-8") as f:
                    json.dump({"team_states": team_states, "tournament_states": tournament_states}, 
                             f, indent=4, ensure_ascii=False, default=datetime_to_str)

    # Добавляем новые матчи
    existing_rounds = set(current_state["schedule"].keys())
    for round_num in new_schedule:
        if round_num not in current_state["schedule"]:
            current_state["schedule"][round_num] = []
        for match in new_schedule[round_num]:
            if match["match_id"] not in current_state["notified_new_matches"] and \
               match["match_id"] not in [m["match_id"] for m in current_state["schedule"].get(round_num, [])]:
                current_state["schedule"][round_num].append(match)
                with open("team_data.json", "w", encoding="utf-8") as f:
                    json.dump({"team_states": team_states, "tournament_states": tournament_states}, 
                             f, indent=4, ensure_ascii=False, default=datetime_to_str)

    # Формируем уведомления о новых матчах
    matches_by_date = {}
    for round_num, match_list in new_schedule.items():
        for match in match_list:
            match_time = parse_iso_date(match["time"])
            date_str = match_time.strftime("%d.%m.%Y")
            if date_str not in matches_by_date:
                matches_by_date[date_str] = []
            matches_by_date[date_str].append((match_time, match["detail"], match["match_id"]))

    for date_str in sorted(matches_by_date.keys()):
        new_matches = [(t, d, m_id) for t, d, m_id in matches_by_date[date_str] if m_id not in current_state["notified_new_matches"]]
        if new_matches:
            embed = discord.Embed(
                title=f"🔔 Матч добавлен в расписание — {date_str}",
                color=0x00ff00,
                timestamp=now_msk
            )
            for match_time, match_detail, match_id in sorted(new_matches, key=lambda x: x[0]):
                emoji = "🕗" if match_time.hour == 20 else "🕘" if match_time.hour == 21 else "🕗"
                embed.add_field(name=f"{emoji} {match_time.strftime('%H:%M')}", value=match_detail.split(" — ", 1)[1], inline=False)
            embed.set_footer(text=f"─────────────────────────\n🕒 {now_msk.strftime('%d.%m.%Y | %H:%M')} MCK")
            await channel.send(embed=embed)
            logger.info(f"🔔 Уведомление о новом матче на дате {date_str}: {', '.join([m[1].split(' — ')[1] for m in new_matches])}")
            for _, _, match_id in new_matches:
                current_state["notified_new_matches"].add(match_id)
                with open("team_data.json", "w", encoding="utf-8") as f:
                    json.dump({"team_states": team_states, "tournament_states": tournament_states}, 
                             f, indent=4, ensure_ascii=False, default=datetime_to_str)

    # Уведомления о новых раундах
    new_rounds = set(new_schedule.keys()) - existing_rounds
    for round_num in new_rounds:
        prev_round = str(int(round_num) - 1)
        if prev_round in current_state["match_results"]:
            completed_matches = len(current_state["match_results"].get(prev_round, set()))
            total_matches = ROUND_MATCHES.get(int(prev_round), 0)
            if completed_matches >= total_matches and total_matches > 0 and round_num not in current_state["notified_new_rounds"]:
                matches_by_date = {}
                for match in current_state["schedule"][round_num]:
                    match_time = parse_iso_date(match["time"])
                    date_str = match_time.strftime("%d.%m.%Y")
                    if date_str not in matches_by_date:
                        matches_by_date[date_str] = []
                    match_detail = match["detail"].split(" — ", 1)[1] if " — " in match["detail"] else match["detail"]
                    matches_by_date[date_str].append((match_time, match_detail))
                
                notification_pages = []
                for i, date_str in enumerate(sorted(matches_by_date.keys()), 1):
                    embed = discord.Embed(
                        title=f"🔔 Новые матчи добавлены в Раунд {round_num} — {date_str}",
                        color=0x00ff00,
                        timestamp=now_msk
                    )
                    for match_time, match_detail in sorted(matches_by_date[date_str], key=lambda x: x[0])[:5]:
                        emoji = "🕗" if match_time.hour == 20 else "🕘" if match_time.hour == 21 else "🕗"
                        embed.add_field(name=f"{emoji} {match_time.strftime('%H:%M')}", value=match_detail, inline=False)
                    embed.set_footer(text=f"Страница {i}/{len(matches_by_date)}\n─────────────────────────\n🕒 {now_msk.strftime('%d.%m.%Y | %H:%M')} MCK")
                    notification_pages.append(embed)
                
                if notification_pages:
                    view = Paginator(notification_pages) if len(notification_pages) > 1 else None
                    await channel.send(embed=notification_pages[0], view=view)
                    current_state["notified_new_rounds"].add(round_num)
                    for match in current_state["schedule"][round_num]:
                        current_state["notified_new_matches"].add(match["match_id"])
                    logger.info(f"🔔 Отправлено уведомление о новых матчах в Раунде {round_num}")
    
    logger.info("Завершено check_tournament_schedule")

async def check_match_results(channel):
    global tournament_states, tournament_progress
    now_msk = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=3)))
    logger.info("Начало check_match_results")
    tournament_data = await fetch_tournament_data(TOURNAMENT_URL)
    if not tournament_data or "data" not in tournament_data:
        logger.error("Не удалось получить данные турнира")
        return
    tournament_id = str(tournament_data["data"].get("id"))
    if tournament_id not in tournament_states:
        tournament_states[tournament_id] = {
            "last_updated": now_msk.isoformat(),
            "match_results": {},
            "schedule": {},
            "notified_results": set(),
            "notified_rounds": set(),
            "notified_reminders": set(),
            "notified_start_notifications": set(),
            "notified_new_rounds": set(),
            "notified_new_matches": set()
        }
    if tournament_id not in tournament_progress:
        tournament_progress[tournament_id] = {
            "total_matches": TOTAL_MATCHES,
            "completed_matches": 0
        }
    current_state = tournament_states[tournament_id]
    
    # Подсчитываем общее количество завершенных матчей
    total_completed_matches = sum(len(results) for results in current_state["match_results"].values())
    tournament_progress[tournament_id]["completed_matches"] = total_completed_matches
    
    matches = tournament_data["data"].get("child", [{}])[0].get("matches", [])
    for match in matches:
        match_id = str(match.get("id"))
        round_num = str(match.get("connection", {}).get("stage", 1))
        winner = match.get("winner")
        team1_id = match.get("team1", {}).get("id")
        team2_id = match.get("team2", {}).get("id")
        team1_score = match.get("result1", 0)
        team2_score = match.get("result2", 0)
        if not winner or not team1_id or not team2_id:
            continue
        if match_id not in current_state["notified_results"]:
            team1_name = EMPTY_SLOT_NAMES.get(team1_id, TEAM_MAPPING.get(str(team1_id), f"Team_{team1_id}"))
            team2_name = EMPTY_SLOT_NAMES.get(team2_id, TEAM_MAPPING.get(str(team2_id), f"Team_{team2_id}"))
            result = f"⭐ **{team1_name}** ({team1_score}) — {team2_name} ({team2_score})" if winner == team1_id else f"⭐ {team1_name} ({team1_score}) — **{team2_name}** ({team2_score})"
            current_state["match_results"].setdefault(round_num, set()).add(result)
            current_state["notified_results"].add(match_id)
            tournament_progress[tournament_id]["completed_matches"] += 1

            # Удаляем завершённый матч из расписания
            if round_num in current_state["schedule"]:
                current_state["schedule"][round_num] = [
                    m for m in current_state["schedule"][round_num] if m["match_id"] != match_id
                ]
                if not current_state["schedule"][round_num]:
                    del current_state["schedule"][round_num]
                with open("team_data.json", "w", encoding="utf-8") as f:
                    json.dump({"team_states": team_states, "tournament_states": tournament_states}, 
                             f, indent=4, ensure_ascii=False, default=datetime_to_str)

            total_completed_matches = tournament_progress[tournament_id]["completed_matches"]
            progress_percent = (total_completed_matches / TOTAL_MATCHES) * 100
            progress_bar = get_progress_bar(progress_percent)
            current_round_matches = len(current_state["match_results"].get(round_num, set()))
            total_round_matches = ROUND_MATCHES.get(int(round_num), 0)
            round_progress = f"📅 Текущий этап: **Р{round_num}** ▶ В процессе ({current_round_matches}/{total_round_matches} матчей)"
            embed = discord.Embed(
                title=f"Результат матча (Р{round_num})",
                color=0xa6a22a,
                timestamp=now_msk
            )
            embed.add_field(name="", value="\n" + result, inline=False)
            embed.add_field(name="", value="─────────────────────────", inline=False)
            embed.add_field(
                name="",
                value=f"📊 Прогресс турнира: **{progress_percent:.1f}%** ({total_completed_matches}/{TOTAL_MATCHES} матчей)\n🟦 [{progress_bar}] {progress_percent:.1f}%",
                inline=False
            )
            embed.add_field(name="", value="─────────────────────────", inline=False)
            embed.add_field(
                name="",
                value=round_progress,
                inline=False
            )
            embed.add_field(name="", value="─────────────────────────", inline=False)
            embed.add_field(
                name="",
                value="📅 Этапы турнира:\n" + "\n".join(get_tournament_stages(tournament_id, int(round_num))),
                inline=False
            )
            embed.set_footer(text=f"─────────────────────────\n🕘 {now_msk.strftime('%d.%m.%Y | %H:%M')} MCK")
            await channel.send(embed=embed)
    
    logger.info("Завершено check_match_results")

async def check_match_reminders(channel):
    global tournament_states
    now_msk = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=3)))
    logger.info("Начало check_match_reminders")
    tournament_data = await fetch_tournament_data(TOURNAMENT_URL)
    if not tournament_data or "data" not in tournament_data:
        logger.error("Не удалось получить данные турнира")
        return
    tournament_id = str(tournament_data["data"].get("id"))
    if tournament_id not in tournament_states:
        tournament_states[tournament_id] = {
            "last_updated": now_msk.isoformat(),
            "match_results": {},
            "schedule": {},
            "notified_results": set(),
            "notified_rounds": set(),
            "notified_reminders": set(),
            "notified_start_notifications": set(),
            "notified_new_rounds": set(),
            "notified_new_matches": set()
        }
    current_state = tournament_states[tournament_id]
    matches = tournament_data["data"].get("child", [{}])[0].get("matches", [])
    for match in matches:
        team1_id = match.get("team1", {}).get("id")
        team2_id = match.get("team2", {}).get("id")
        if team1_id is None or team2_id is None:
            continue
        match_time = parse_iso_date(match.get("date", now_msk.isoformat()))
        match_key = f"{team1_id}_{team2_id}"
        time_until_match = match_time - now_msk
        if (0 <= time_until_match.total_seconds() <= 1200 and match_key not in current_state["notified_reminders"] and 
            match.get("status") == 0 and not (match.get("result1", 0) > 0 or match.get("result2", 0) > 0 or match.get("winner"))):
            team1_name = EMPTY_SLOT_NAMES.get(team1_id, TEAM_MAPPING.get(str(team1_id), f"Team_{team1_id}"))
            team2_name = EMPTY_SLOT_NAMES.get(team2_id, TEAM_MAPPING.get(str(team2_id), f"Team_{team2_id}"))
            reminder_time = match_time.strftime("%H:%M")
            minutes_left = int(time_until_match.total_seconds() / 60)
            embed = discord.Embed(title="🔴 Напоминание!", color=0xFFA500)
            embed.add_field(name="Матч", value=f"**{team1_name}** 🆚 **{team2_name}**", inline=True)
            embed.add_field(name="Осталось", value=f"{minutes_left} минут", inline=True)
            embed.add_field(name="Начало", value=reminder_time, inline=True)
            embed.set_footer(text=f"─────────────────────────\n🕒 {now_msk.strftime('%d.%m.%Y | %H:%M')} MCK")
            await channel.send(embed=embed)
            current_state["notified_reminders"].add(match_key)
    
    logger.info("Завершено check_match_reminders")

async def check_match_start_notifications(channel):
    global tournament_states
    now_msk = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=3)))
    logger.info("Начало check_match_start_notifications")
    tournament_data = await fetch_tournament_data(TOURNAMENT_URL)
    if not tournament_data or "data" not in tournament_data:
        logger.error("Не удалось получить данные турнира")
        return
    tournament_id = str(tournament_data["data"].get("id"))
    if tournament_id not in tournament_states:
        tournament_states[tournament_id] = {
            "last_updated": now_msk.isoformat(),
            "match_results": {},
            "schedule": {},
            "notified_results": set(),
            "notified_rounds": set(),
            "notified_reminders": set(),
            "notified_start_notifications": set(),
            "notified_new_rounds": set(),
            "notified_new_matches": set()
        }
    current_state = tournament_states[tournament_id]
    matches = tournament_data["data"].get("child", [{}])[0].get("matches", [])
    for match in matches:
        team1_id = match.get("team1", {}).get("id")
        team2_id = match.get("team2", {}).get("id")
        if team1_id is None or team2_id is None:
            continue
        match_time = parse_iso_date(match.get("date", now_msk.isoformat()))
        match_key = f"{team1_id}_{team2_id}"
        time_difference = (match_time - now_msk).total_seconds()
        if (-60 <= time_difference <= 60 and match_key not in current_state["notified_start_notifications"] and 
            match.get("status") == 0 and not (match.get("result1", 0) > 0 or match.get("result2", 0) > 0 or match.get("winner"))):
            team1_name = EMPTY_SLOT_NAMES.get(team1_id, TEAM_MAPPING.get(str(team1_id), f"Team_{team1_id}"))
            team2_name = EMPTY_SLOT_NAMES.get(team2_id, TEAM_MAPPING.get(str(team2_id), f"Team_{team2_id}"))
            embed = discord.Embed(title="✅ Матч начался!", color=0x00ff00)
            embed.add_field(name="Матч", value=f"**{team1_name}** 🆚 **{team2_name}**", inline=False)
            embed.set_footer(text=f"─────────────────────────\n🕒 {now_msk.strftime('%d.%m.%Y | %H:%M')} MCK")
            await channel.send(embed=embed)
            current_state["notified_start_notifications"].add(match_key)
    
    logger.info("Завершено check_match_start_notifications")

@bot.command()
async def results(ctx):
    global tournament_states
    now_msk = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=3)))
    logger.info("Команда !results вызвана")
    tournament_id = next(iter(tournament_states.keys()), None)
    if not tournament_id or not tournament_states[tournament_id].get("match_results"):
        await ctx.send("⚠️ Нет доступных результатов матчей на данный момент, пожалуйста, следите за уведомлениями.")
        return
    results_pages = []
    for round_num in sorted(tournament_states[tournament_id]["match_results"].keys(), key=int):
        embed = discord.Embed(
            title=f"📝 Результаты — Раунд {round_num}",
            color=0x00CED1,
            timestamp=now_msk
        )
        embed.set_author(name="Summer Major Rankings I 2026")
        for result in sorted(tournament_states[tournament_id]["match_results"][round_num]):
            updated_result = replace_team_ids_with_names(result)
            embed.add_field(name="Матч", value=updated_result, inline=False)
        results_pages.append(embed)
    
    if not results_pages:
        await ctx.send("⚠️ Нет доступных результатов матчей на данный момент, пожалуйста, следите за уведомлениями.")
        return
    
    # Устанавливаем правильный номер страницы и общее количество страниц
    for i, embed in enumerate(results_pages, 1):
        embed.set_footer(text=f"Страница {i}/{len(results_pages)}\n─────────────────────────\n🕒 {now_msk.strftime('%d.%m.%Y | %H:%M')} MCK")
    
    view = Paginator(results_pages)
    await ctx.send(embed=results_pages[0], view=view)

@bot.command()
async def schedule(ctx):
    global tournament_states
    now_msk = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=3)))
    logger.info("Команда !schedule вызвана")
    tournament_id = next(iter(tournament_states.keys()), None)
    if not tournament_id or not tournament_states[tournament_id].get("schedule"):
        await ctx.send("⚠️ Нет доступного расписания на данный момент, пожалуйста, следите за уведомлениями.")
        return
    matches_by_date = {}
    for round_num, match_list in tournament_states[tournament_id]["schedule"].items():
        for match in match_list:
            if isinstance(match, dict) and "teams" in match:
                match_id = match["match_id"]
                match_time = parse_iso_date(match["time"])
                date_str = match_time.strftime("%d.%m.%Y")
                team1_id = match["teams"]["team1_id"]
                team2_id = match["teams"]["team2_id"]
                team1_name = EMPTY_SLOT_NAMES.get(team1_id, TEAM_MAPPING.get(str(team1_id), f"Team_{team1_id}"))
                team2_name = EMPTY_SLOT_NAMES.get(team2_id, TEAM_MAPPING.get(str(team2_id), f"Team_{team2_id}"))
                has_result = any(
                    f"{team1_name}" in result and f"{team2_name}" in result
                    for result in tournament_states[tournament_id].get("match_results", {}).get(round_num, [])
                ) or match_id in tournament_states[tournament_id]["notified_results"]
                if not has_result:
                    if date_str not in matches_by_date:
                        matches_by_date[date_str] = []
                    match_detail = f"**{team1_name}** 🆚 **{team2_name}**"
                    matches_by_date[date_str].append((match_time, match_detail, match_id))
                    logger.info(f"Матч добавлен в расписание команды !schedule: {match_id}, {match_detail}, {match_time}")
                else:
                    logger.info(f"Матч {match_id} исключён из расписания команды !schedule: имеет результат")

    # Фильтруем пустые даты
    matches_by_date = {date: matches for date, matches in matches_by_date.items() if matches}
    
    # Подсчитываем общее количество страниц
    matches_per_page = 16
    total_pages = 0
    for date_str in sorted(matches_by_date.keys()):
        matches = sorted(matches_by_date[date_str], key=lambda x: x[0])
        total_pages += (len(matches) + matches_per_page - 1) // matches_per_page
    
    # Создаём страницы
    schedule_pages = []
    page_index = 0
    for date_str in sorted(matches_by_date.keys()):
        matches = sorted(matches_by_date[date_str], key=lambda x: x[0])
        for i in range(0, len(matches), matches_per_page):
            page_index += 1
            embed = discord.Embed(
                title=f"📅 Расписание матчей — {date_str}",
                color=0x00ff00,
                timestamp=now_msk
            )
            for match_time, match_detail, match_id in matches[i:i + matches_per_page]:
                emoji = "🕗" if match_time.hour == 20 else "🕘" if match_time.hour == 21 else "🕗"
                embed.add_field(name=f"{emoji} {match_time.strftime('%H:%M')}", value=match_detail, inline=False)
            embed.set_footer(text=f"Страница {page_index}/{total_pages}\n─────────────────────────\n🕒 {now_msk.strftime('%d.%m.%Y | %H:%M')} MCK")
            schedule_pages.append(embed)
    
    if not schedule_pages:
        await ctx.send("⚠️ Нет доступного расписания на данный момент, пожалуйста, следите за уведомлениями.")
        return
    
    view = Paginator(schedule_pages)
    await ctx.send(embed=schedule_pages[0], view=view)

@bot.command()
async def progress(ctx):
    global tournament_states, tournament_progress
    now_msk = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=3)))
    logger.info("Команда !progress вызвана")
    tournament_id = "842"
    if tournament_id not in tournament_progress:
        tournament_progress[tournament_id] = {
            "total_matches": TOTAL_MATCHES,
            "completed_matches": 0
        }
    total_completed_matches = sum(len(results) for results in tournament_states.get(tournament_id, {}).get("match_results", {}).values())
    tournament_progress[tournament_id]["completed_matches"] = total_completed_matches
    progress_percent = (total_completed_matches / TOTAL_MATCHES) * 100
    progress_bar = get_progress_bar(progress_percent)
    current_round = 1
    current_round_matches = 0
    for round_num in sorted(tournament_states.get(tournament_id, {}).get("match_results", {}).keys(), key=int):
        completed_matches = len(tournament_states[tournament_id]["match_results"][round_num])
        total_matches = ROUND_MATCHES.get(int(round_num), 0)
        if completed_matches < total_matches or (completed_matches == total_matches and int(round_num) == current_round):
            current_round = int(round_num)
            current_round_matches = completed_matches
            break
    embed = discord.Embed(title="Статистика **Summer Major Rankings I 2026**", color=0xa6a22a, timestamp=now_msk)
    embed.add_field(
        name="",
        value=f"📊 Прогресс турнира: **{progress_percent:.1f}%** ({total_completed_matches}/{TOTAL_MATCHES} матчей)\n🟦 [{progress_bar}] {progress_percent:.1f}%",
        inline=False
    )
    embed.add_field(name="", value="─────────────────────────", inline=False)
    embed.add_field(
        name="",
        value=f"🔄 Текущий раунд: **Р{current_round}** ({current_round_matches}/{ROUND_MATCHES.get(current_round, 0)} матчей сыграно)",
        inline=False
    )
    embed.add_field(name="", value="─────────────────────────", inline=False)
    embed.add_field(
        name="",
        value="📅 Этапы турнира:\n" + "\n".join(get_tournament_stages(tournament_id, current_round)),
        inline=False
    )
    embed.set_footer(text=f"─────────────────────────\n🕒 {now_msk.strftime('%d.%m.%Y | %H:%M')} MCK")
    await ctx.send(embed=embed)

@bot.command()
async def reset_results(ctx):
    global tournament_states, tournament_progress
    logger.info("Команда !reset_results вызвана")
    tournament_id = "842"
    if tournament_id in tournament_states:
        tournament_states[tournament_id]["match_results"] = {}
        tournament_states[tournament_id]["notified_results"] = set()
        tournament_progress[tournament_id]["completed_matches"] = 0
        logger.info("Сброшены результаты матчей и уведомления")
        with open("team_data.json", "w", encoding="utf-8") as f:
            json.dump({"team_states": team_states, "tournament_states": tournament_states}, f, indent=4, ensure_ascii=False, default=datetime_to_str)
        with open("tournament_progress.json", "w", encoding="utf-8") as f:
            json.dump(tournament_progress, f, indent=4, ensure_ascii=False, default=datetime_to_str)
        await ctx.send("✅ Результаты матчей сброшены. Новые результаты будут загружены при следующем обновлении.")
    else:
        await ctx.send("⚠️ Нет данных о турнире для сброса.")

@tasks.loop(minutes=1)
async def update_task():
    channel = bot.get_channel(CHANNEL_ID)
    if not channel:
        logger.error(f"❌ Канал не найден. Проверь CHANNEL_ID: {CHANNEL_ID}")
        return
    try:
        await check_team_updates(channel)
        await check_tournament_schedule(channel)
        await check_match_results(channel)
        await check_match_reminders(channel)
        await check_match_start_notifications(channel)
        logger.info("🔄 Цикл проверки команд, расписания, результатов, напоминаний и уведомлений завершён")
        logger.debug(f"Содержимое team_states перед сохранением: {team_states}")
        logger.debug(f"Содержимое tournament_states перед сохранением: {tournament_states}")
        logger.debug(f"Содержимое TEAM_MAPPING перед сохранением: {TEAM_MAPPING}")
        logger.debug(f"Содержимое team_name_history перед сохранением: {team_name_history}")
        logger.debug(f"Содержимое tournament_progress перед сохранением: {tournament_progress}")
        with open("team_data.json", "w", encoding="utf-8") as f:
            json.dump({"team_states": team_states, "tournament_states": tournament_states}, f, indent=4, ensure_ascii=False, default=datetime_to_str)
        with open("team_history.json", "w", encoding="utf-8") as f:
            json.dump({"TEAM_MAPPING": TEAM_MAPPING, "team_name_history": team_name_history}, f, indent=4, ensure_ascii=False, default=datetime_to_str)
        with open("tournament_progress.json", "w", encoding="utf-8") as f:
            json.dump(tournament_progress, f, indent=4, ensure_ascii=False, default=datetime_to_str)
        logger.debug("Данные успешно сохранены в team_data.json, team_history.json и tournament_progress.json")
    except Exception as e:
        logger.error(f"❌ Ошибка в цикле проверки: {str(e)}")

@bot.event
async def on_ready():
    logger.info(f'🤖 Бот запущен как {bot.user}')
    channel = bot.get_channel(CHANNEL_ID)
    if channel:
        await channel.send("✅ Бот запущен и следит за изменениями.")
    else:
        logger.error("❌ Канал не найден. Проверь CHANNEL_ID.")
    if not update_task.is_running():
        update_task.start()

bot.run(TOKEN)