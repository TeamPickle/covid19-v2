import os
import dotenv
from bot import CovidBot

dotenv.load_dotenv()

extension_base = "cogs"
extensions = []

bot = CovidBot()

for ext in extensions:
    bot.load_extension(extension_base + ext)

bot.run(os.getenv("TOKEN"))