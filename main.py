# --- CONFIGURATION ---
TWITCH_TOKEN = ""
CLIENT_ID = ""
CLIENT_SECRET = ""
CHANNEL_NAME = ""
MY_TWITCH_ID = ""

UPCOMING_FILE = "upcoming.txt"
# ------------------------------






import os
import time
import psutil
import asyncio
from twitchio.ext import commands, routines
import twitchio
import datetime
import aiohttp
import random

GAME_TEMPLATES = {
    "Minecraft": [
        "Punching trees like it's a profession",
        "Hardcore mode but emotionally fragile",
        "Building badly, confidently",
        "Villagers judging my life choices"
    ],
    "Grey Hack": [
        "Definitely not hacking the Pentagon",
        "Ethical hacking but morally questionable",
        "Cybercrime but make it cozy",
        "sudo make me funny"
    ],
    "Just Chatting": [
        "Professional oversharing session",
        "Talking because gameplay is hard",
        "No plan, just vibes",
        "Stalling until inspiration arrives"
    ],
    "Cry of Fear": [
        "Screaming at pixels since 2012",
        "Horror games but make it a comedy",
        "Jump scares and bad jokes",
        "Surviving nightmares one scream at a time"
    ],
    "It's Always Monday": [
        "Living the eternal Monday dream",
        "Work hard, nap harder",
        "Office simulator but make it existential",
        "Pretending to be productive since 2024"
    ],
    "Layers of Fear (2016)": [
        "Painting my way through madness",
        "Art therapy but with more screams",
        "Exploring the fine line between genius and insanity",
        "Creating masterpieces while losing my mind"
    ]
}




# Map your .exe names to the exact Twitch category name
GAME_PROCESSES = {
    "javaw.exe": "Minecraft",
    "Grey Hack.exe": "Grey Hack",
    "cof.exe": "Cry of Fear",
    "it's always monday.exe": "It's Always Monday",
    "Layers of FearSub.exe": "Layers of Fear (2016)"
}

class Bot(commands.Bot):
    def __init__(self):
        super().__init__(
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
            bot_id=MY_TWITCH_ID,
            owner_id=MY_TWITCH_ID,
            prefix="!",
            initial_channels=[CHANNEL_NAME]
        )
    last_game = "Just Chatting"

    async def event_ready(self):
        print(f"Logged in as {self.user.name}")
        try:
            self.main_updater.start()
        except RuntimeError:
            pass

    def get_joke(self, game_name):
        jokes = GAME_TEMPLATES.get(game_name, GAME_TEMPLATES["Just Chatting"])
        return random.choice(jokes)



    def get_game(self):
        for proc in psutil.process_iter(['name']):
            try:
                name = proc.info['name'].lower()
                if name in GAME_PROCESSES:
                    return GAME_PROCESSES[name]
            except: continue
        return "Just Chatting"

    async def update_twitch_title(self, title: str, game_id: str):
        url = "https://api.twitch.tv/helix/channels"
        headers = {
            "Authorization": f"Bearer {TWITCH_TOKEN}",
            "Client-Id": CLIENT_ID,
            "Content-Type": "application/json"
        }
        params = {"broadcaster_id": MY_TWITCH_ID}
        payload = {"title": title, "game_id": game_id}

        async with aiohttp.ClientSession() as session:
            async with session.patch(url, headers=headers, params=params, json=payload) as response:
                if response.status != 204:
                    text = await response.text()
                    raise Exception(f"Twitch API error {response.status}: {text}")

    # --- THE ROUTINE ---
    @routines.routine(delta=datetime.timedelta(minutes=5))
    async def main_updater(self):
        game_name = self.get_game()
        joke = self.get_joke(game_name)
        

        upcoming = "Streaming now"
        if os.path.exists(UPCOMING_FILE):
            with open(UPCOMING_FILE, 'r') as f:
                upcoming = f.read().strip() or "Streaming now"

        # if game_name == self.last_game:
        #    print("Game unchanged — skipping title update.")
        #return

        print(f"Game changed to {game_name} — updating title.")

        joke = self.get_joke(game_name)

        new_title = f"{joke} | {game_name} | {upcoming}"

        try:
            games = await self.fetch_games(names=[game_name])
            target_game_id = games[0].id if games else "509658"  # Just Chatting fallback

            await self.update_twitch_title(new_title, target_game_id)

            print(f"Update Success: {new_title}")

        except Exception as e:
            print(f"Update Error: {e}")



async def main():
    bot = Bot()
    await bot.start()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot shut down.")
