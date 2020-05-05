import telebot
from source import utils
from model import tree

config = utils.read_json("data/configs.json")
_TOKEN = config["TOKEN"]
bot = telebot.TeleBot(_TOKEN)
_content = utils.read_json("data/routes.json")
context_tree = tree.setup_tree(_content)
