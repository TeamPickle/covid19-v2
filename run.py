import os
import dotenv
from bot import CovidBot
import dbl

dotenv.load_dotenv()

extension_base = "cogs."
extensions = [
    "help",
    "ping",
    "symptom",
    "disaster",
    "hospital",
    "status",
    "graphic",
    "prefix",
    "map",
    "channel",
    "position",
    "admin"
]

bot = CovidBot()

for ext in extensions:
    bot.load_extension(extension_base + ext)

bot.run(os.getenv("TOKEN"))
if token := os.getenv("DBL_TOKEN"):
    dbl.DBLClient(bot, token)