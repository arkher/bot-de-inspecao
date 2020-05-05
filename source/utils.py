import json
from telebot import types
from datetime import datetime

def read_json(path:str):
	try:
		with open(path, encoding="utf-8") as f:
			content = f.read()
			return json.loads(content)
	except FileNotFoundError as e:
		raise e

def generate_keyboard_markup(node):
	markup = types.ReplyKeyboardMarkup(resize_keyboard=1, one_time_keyboard=True)
	children = node.get_children()
	
	buttons = []
	for child in children:
		data = child.get_data()
		btn = types.KeyboardButton(data["content"])
		buttons.append(btn)
		if len(buttons) == 2:
			markup.row(buttons[0], buttons[1])
			buttons = []
	
	if buttons != []:
		markup.row(buttons[0])

	return markup

def get_child_by_content(content, node):
	children = node.get_children()
	for child in children:
		data = child.get_data()
		if data["content"] == content:
			return child
	return None

def generate_insp_code():
	return datetime.now().strftime("%Y%m%d%H%M%S")

def read_inspec(path):
    with open(path, encoding="utf-8") as f:
        return json.loads(f.read())

def save_json(path, content):
	with open(path, "w", encoding="utf-8") as outfile:
		json.dump(content, outfile, ensure_ascii=False, indent=4)

#------- Condition tests -------
def _condition_has_child(node):
	children = node.get_children()
	return ( children != [])

def _condition_is_child_content(text, node):
	children = node.get_children()
	for child in children:
		data = child.get_data()
		if text == data["content"]:
			return True
	return False

def _condition_is_back_node(node):
	data = node.get_data()
	return (data["type"] == "control" and data["content"] == "Voltar")

def _condition_is_root(node):
	data = node.get_data()
	return data["type"] == "root"

def _condition_is_cancel_inspec(node):
	data = node.get_data()
	return (data["type"] == "control" and data["content"] == "Cancelar inspeção")

def _condition_is_finish_inspec(node):
	data = node.get_data()
	return (data["type"] == "control" and data["content"] == "Finalizar inspeção")

def _condition_is_leaf_node(node):
	has_child = _condition_has_child(node)
	return (has_child == False)

CONDITION_MAP = {}
# ---------------- Tree ----------------
CONDITION_MAP["has_child"] = _condition_has_child
CONDITION_MAP["in_context"] = _condition_is_child_content
CONDITION_MAP["is_back_node"] = _condition_is_back_node
CONDITION_MAP["is_root_node"] = _condition_is_root
CONDITION_MAP["is_cancel_node"] = _condition_is_cancel_inspec
CONDITION_MAP["is_finish_node"] = _condition_is_finish_inspec
CONDITION_MAP["is_leaf_node"] = _condition_is_leaf_node

# ---------------- Message ----------------
CONDITION_MAP['messageIsDocument'] = lambda message: message.content_type == 'document'
CONDITION_MAP['messageIsPhoto'] = lambda message: message.content_type == 'photo'

# ---------------- User ----------------
CONDITION_MAP["is_active"] = lambda username, user_dict: username in user_dict.keys()