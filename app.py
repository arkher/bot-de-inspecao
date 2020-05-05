from source import utils
from model.tree import Tree
from model.inspection import Inspection, Defect
from source.bot import bot, context_tree, _TOKEN
from telebot import types
import requests
import os

USERS = {}

@bot.message_handler(commands=['help', 'start'])
def send_welcome(message):
	first_name = message.from_user.first_name
	msg = bot.reply_to(message, "Olá {}!".format(first_name))
	init_service(message)


def init_service(message):
	markup = types.ReplyKeyboardMarkup(resize_keyboard=1, one_time_keyboard=True)
	itembtn1 = types.KeyboardButton('Iniciar inspeção')
	itembtn2 = types.KeyboardButton('Continuar inspeção')
	markup.row(itembtn1)
	markup.row(itembtn2)
	msg = bot.send_message(message.chat.id, "Selecione a opção desejada.", reply_markup=markup)
	bot.clear_reply_handlers(message)
	bot.clear_step_handler_by_chat_id(message.chat.id)
	bot.register_next_step_handler(msg, decision_inspec)


def decision_inspec(message):
	text = message.text
	chat_id = message.chat.id
	
	first_name = message.from_user.first_name
	last_name = message.from_user.last_name
	username = message.from_user.username

	if (text == "Iniciar inspeção"):
		inspec_code = utils.generate_insp_code() 
		USERS[username] = {
			"context": context_tree,
			"inspection": Inspection(
				code=inspec_code,
				trafo="Sem placa",
				latitude=0,
				longitude=0
			),
			"first_name": first_name,
			"last_name": last_name,
			"username": username
		}

		msg = bot.send_message(chat_id, "ok, iniciando inspeção.\nSeu código é:")
		msg = bot.send_message(chat_id, "{}".format(inspec_code))
		init_inspec(message)

	elif (text == "Continuar inspeção"):
		# TODO: Criar o fluxo de continuar inspeção
		USERS[username] = {
			"context": context_tree,
			"inspection": None,
			"first_name": first_name,
			"last_name": last_name,
			"username": username
		}
		msg = bot.send_message(chat_id, "ok, continuando inspeção. Digite o código da inspeção que deseja continuar")
		bot.clear_reply_handlers(message)
		bot.clear_step_handler_by_chat_id(message.chat.id)
		bot.register_next_step_handler(msg, continue_inspec)

	else:
		msg = bot.send_message(chat_id, "ops, selecione uma opção válida.")
		bot.clear_reply_handlers(message)
		bot.clear_step_handler_by_chat_id(chat_id)
		bot.register_next_step_handler(msg, init_service)

def continue_inspec(message):
	username = message.from_user.username
	user = USERS[username]

	file_path = './data/inspecs/inspec_{}.json'.format(message.text)
	if os.path.exists(file_path):
		_inspec = utils.read_json(file_path)
		user["inspection"] = Inspection(inspec=_inspec)
		show_screen(message)
	else:
		markup = types.ReplyKeyboardMarkup(resize_keyboard=1)
		itembtn1 = types.KeyboardButton('Voltar')
		markup.row(itembtn1)
		msg = bot.reply_to(message, 'O código informado é inválido ou não foi encontrado.', reply_markup=markup)
		bot.clear_reply_handlers(message)
		bot.clear_step_handler_by_chat_id(message.chat.id)
		bot.register_next_step_handler(msg, init_service)       


def init_inspec(message):
	chat_id = message.chat.id	
	markup = types.ReplyKeyboardMarkup(resize_keyboard=1, one_time_keyboard=True)
	itembtn1 = types.KeyboardButton('Sem placa')
	markup.row(itembtn1)
	msg = bot.send_message(chat_id, "Informe a placa do trafo inspecionado.", reply_markup=markup)
	bot.clear_reply_handlers(message)
	bot.clear_step_handler_by_chat_id(message.chat.id)
	bot.register_next_step_handler(msg, confirm_placa)


def confirm_placa(message):
	username = message.from_user.username
	user = USERS[username]
	text = message.text

	user["inspection"].set_trafo(text)
	bot.clear_reply_handlers(message)
	bot.clear_step_handler_by_chat_id(message.chat.id)
	show_screen(message)


def show_screen(message):
	""" Apresenta estado atual da árvore de contexto """
	current_context = USERS[message.from_user.username]["context"]
	markup = utils.generate_keyboard_markup(current_context)
	msg = bot.send_message(message.chat.id, "Selecione a opção desejada.", reply_markup=markup)
	bot.clear_reply_handlers(message)
	bot.clear_step_handler_by_chat_id(message.chat.id)
	
	bot.register_next_step_handler(msg, check_context)


def check_context(message):
	text = message.text
	current_context = USERS[message.from_user.username]["context"]
	if utils.CONDITION_MAP["in_context"](text, current_context):
		next_context = utils.get_child_by_content(text, current_context)
		
		# Se nó de voltar, atualizar o estado do usuário para o contexto anterior
		if utils.CONDITION_MAP["is_back_node"](next_context):
			prev_context = current_context.get_parent()
			# TODO: undo user step
			user = USERS[message.from_user.username]
			user_inspec = user["inspection"]
			step = user_inspec.pop_step()
			print(user["username"], "pop step: {}".format(step))
			user["context"] = prev_context
			bot.clear_reply_handlers(message)
			bot.clear_step_handler_by_chat_id(message.chat.id)
			show_screen(message)

		elif utils.CONDITION_MAP["is_cancel_node"](next_context):
			msg = bot.send_message(message.chat.id, "Inspeção cancelada")
			# TODO: cancel inspec
			USERS[message.from_user.username]["context"] = context_tree
			bot.clear_reply_handlers(message)
			bot.clear_step_handler_by_chat_id(message.chat.id)
			send_welcome(message)

		elif utils.CONDITION_MAP["is_finish_node"](next_context):
			USERS[message.from_user.username]["context"] = context_tree
			bot.clear_reply_handlers(message)
			bot.clear_step_handler_by_chat_id(message.chat.id)
			check_inspec_end(message)
		
		elif utils.CONDITION_MAP["is_leaf_node"](next_context):
			user = USERS[message.from_user.username]
			user["inspection"].add_step(text)
			# TODO: save route and checks for a new route or a finishing inspec
			user["context"] = context_tree
			bot.clear_reply_handlers(message)
			bot.clear_step_handler_by_chat_id(message.chat.id)
			send_location(message)
		
		else:
			# Está indo para o próximo nó de contexto
			user = USERS[message.from_user.username]
			user_inspec = user["inspection"]
			user_inspec.add_step(text)
			user["context"] = next_context
			bot.clear_reply_handlers(message)
			bot.clear_step_handler_by_chat_id(message.chat.id)
			show_screen(message)

	else:
		msg = bot.send_message(message.chat.id, "Não entendi.")
		show_screen(message)


def send_location(message):
	user = USERS[message.from_user.username]
	user["context"] = context_tree

	if (message.location == None):
		if (message.text == "Cancelar"):
			defect = user["inspection"].pop_defect()
			print(user["username"], "pop defect: {}".format(defect.get_flow()))
			show_screen(message)
		else:
			markup = types.ReplyKeyboardMarkup(resize_keyboard=1, one_time_keyboard=True)
			item = types.KeyboardButton("Cancelar")
			markup.row(item)
			msg = bot.send_message(message.chat.id, "Por favor, envie sua localização.", reply_markup=markup)
			bot.clear_reply_handlers(message)
			bot.clear_step_handler_by_chat_id(message.chat.id)
			bot.register_next_step_handler(msg, send_location)
	else:
		location = message.location
		user["inspection"].set_latitude(location.latitude)
		user["inspection"].set_longitude(location.longitude)
		msg = bot.send_message(message.chat.id, "Você está em: {}".format(location) )
		bot.clear_reply_handlers(message)
		bot.clear_step_handler_by_chat_id(message.chat.id)
		send_local_photo(msg)


def send_local_photo(message):
	markup = types.ReplyKeyboardMarkup(resize_keyboard=1, row_width=1)
	itembtn1 = types.KeyboardButton('Concluir')
	markup.row(itembtn1)
	msg = bot.send_message(message.chat.id, "Envie as fotos (uma por vez) e selecione a opção concluir quando terminar.", reply_markup=markup)
	bot.clear_reply_handlers(message)
	bot.clear_step_handler_by_chat_id(message.chat.id)
	bot.register_next_step_handler(msg, confirm_send_local_photo)


def confirm_send_local_photo(message):
	__isDocument = utils.CONDITION_MAP['messageIsDocument'](message)
	__isPhoto = utils.CONDITION_MAP['messageIsPhoto'](message)

	if __isDocument or __isPhoto:
		if __isDocument:
			file_id = message.document.file_id
			file_info = bot.get_file(file_id)
		elif __isPhoto:
			file_id = message.photo[len(message.photo)-1].file_id
			file_info = bot.get_file(file_id)
		
		file = requests.get('https://api.telegram.org/file/bot{0}/{1}'.format(_TOKEN, file_info.file_path))
		
		username = message.from_user.username
		user = USERS[username]

		with open('data/images/{}.jpg'.format(file_info.file_id), 'wb') as f:
			f.write(file.content)
			photo_path = os.path.abspath('data/images/{}.jpg'.format(file_info.file_id))
			user["inspection"].add_photo(photo_path)

		with open('data/images/{}.jpg'.format(file_info.file_id), 'rb') as f:
			msg = bot.reply_to(message, 'recebi sua imagem')
			bot.clear_reply_handlers(message)
			bot.clear_step_handler_by_chat_id(message.chat.id)
			bot.register_next_step_handler(msg, confirm_send_local_photo)

	elif(message.text=='Concluir'):
		username = message.from_user.username
		user = USERS[username]

		inspec_json = user["inspection"].to_json()
		utils.save_json(path="data/inspecs/inspec_{}.json".format(user["inspection"].get_code()),
			content=inspec_json)

		markup = types.ReplyKeyboardMarkup(resize_keyboard=1)
		itembtn1 = types.KeyboardButton('Finalizar Inspeção')
		itembtn2 = types.KeyboardButton('Registrar Novo Defeito')
		markup.row(itembtn1)
		markup.row(itembtn2)
		msg = bot.reply_to(message, "Defeito cadastrado.\nFinalizar Inspeção?", reply_markup=markup)
		bot.clear_reply_handlers(message)
		bot.clear_step_handler_by_chat_id(message.chat.id)
		bot.register_next_step_handler(msg, check_inspec_end)

	else:
		msg = bot.reply_to(message, "ops, envie uma foto por vez e selecione concluir quando terminar")
		bot.clear_reply_handlers(message)
		bot.clear_step_handler_by_chat_id(message.chat.id)
		bot.register_next_step_handler(msg, confirm_send_local_photo)


def check_inspec_end(message):
	if message.text == 'Registrar Novo Defeito':
		user = USERS[message.from_user.username]
		user["inspection"].add_defect()
		show_screen(message)
	elif message.text.lower() == 'finalizar inspeção':
		markup = types.ReplyKeyboardMarkup(resize_keyboard=1)
		itembtn1 = types.KeyboardButton('Sim')
		itembtn2 = types.KeyboardButton('Não, registrar novo defeito')
		markup.row(itembtn1)
		markup.row(itembtn2)
		
		msg = bot.reply_to(message, "Deseja finalizar a inspeção?", reply_markup=markup)
		bot.clear_reply_handlers(message)
		bot.clear_step_handler_by_chat_id(message.chat.id)
		bot.register_next_step_handler(msg, process_inspec_end)

	else:
		markup = types.ReplyKeyboardMarkup(resize_keyboard=1)
		itembtn1 = types.KeyboardButton('Finalizar Inspeção')
		itembtn2 = types.KeyboardButton('Registrar Novo Defeito')
		markup.row(itembtn1)
		markup.row(itembtn2)
		
		msg = bot.reply_to(message, "Ops! Não reconheço esse comando.\nFinalizar Inspeção?", reply_markup=markup)
		bot.clear_reply_handlers(message)
		bot.clear_step_handler_by_chat_id(message.chat.id)
		bot.register_next_step_handler(msg, check_inspec_end)


def process_inspec_end(message):
	username = message.from_user.username
	user = USERS[username]
	if message.text == 'Sim':
		user_inspec = user["inspection"]
		if user_inspec.get_defects() != []:
			inspec_json = user_inspec.to_json()
			utils.save_json("data/inspecs/inspec_{}.json".format(user_inspec.get_code()),
				content=inspec_json)

			markup = types.ReplyKeyboardMarkup(resize_keyboard=1)
			itembtn1 = types.KeyboardButton('OK')
			markup.row(itembtn1)
			
			report = user_inspec.generate_report()
			msg = bot.reply_to(message, "Inspeção finalizada. Seu código de inspeção é:")
			bot.send_message(message.chat.id, user_inspec.get_code())
			msg = bot.send_message(message.chat.id, report, reply_markup=markup)
			
			msg.text = 'inicio'
			bot.clear_reply_handlers(message)
			bot.clear_step_handler_by_chat_id(message.chat.id)
			bot.register_next_step_handler(msg, init_service)
			del  USERS[username]
		
		else:
			markup = types.ReplyKeyboardMarkup(resize_keyboard=1)
			itembtn1 = types.KeyboardButton('Registrar novo defeito')
			markup.row(itembtn1)
			
			msg = bot.reply_to(message, "Por favor, adicione pelo menos um defeito antes de finalizar a inspeção. Caso deseje, pode Cancelar a inspeção também.", reply_markup=markup)
			bot.clear_reply_handlers(message)
			bot.clear_step_handler_by_chat_id(message.chat.id)
			bot.register_next_step_handler(msg, process_inspec_end)
		
	elif message.text == 'Não, registrar novo defeito' or message.text == 'Registrar novo defeito':
		user = USERS[message.from_user.username]
		user["inspection"].add_defect()
		show_screen(message)

	else:
		markup = types.ReplyKeyboardMarkup(resize_keyboard=1)
		itembtn1 = types.KeyboardButton('Registrar novo defeito')
		markup.row(itembtn1)
		
		msg = bot.reply_to(message, "Ops! algo deu errado.", reply_markup=markup)
		bot.clear_reply_handlers(message)
		bot.clear_step_handler_by_chat_id(message.chat.id)
		bot.register_next_step_handler(msg, process_inspec_end)



if __name__ == "__main__":
	print("Starting service bot")
	bot.polling()