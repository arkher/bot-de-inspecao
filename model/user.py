class User():
	def __init__(self, username, first_name, last_name, insp_code=None, date=None, trafo_board=None, defects=[]):
		self.username = username
		self.insp_code = insp_code
		self.first_name = first_name
		self.last_name = last_name
		self.date = date
		self.trafo_board = trafo_board
		self.defects = defects
		self.__current_defect = len(self.defects)-1
	



















def get_data_insp(user):
	inspec_content = {
		'insp_code': user.insp_code,
		'username': user.username,
		'nome': user.first_name,
		'sobrenome': user.last_name,
		'data': user.date,
		'placa': user.trafo_board,
		'defeitos':[]
	}
	
	for defect in user.defects:
		if 'fotos' not in defect.keys():
			defect['fotos'] = []
		inspec_content['defeitos'].append(defect)
	
	return inspec_content

def generate_report(insepc_content):
	date = insepc_content['data']
	trafo_board = insepc_content['placa']
	
	report = 'Data: {}\n'.format(date)
	report += 'Trafo: {}\n'.format(trafo_board)
	
	i = 1
	defect_report = '---- Defeitos ----\n'
	for defect in insepc_content['defeitos']:
		defect_report += '*Defeito {}*\n'.format(i)
		defect_report += 'Grupo: {}\n'.format(defect['grupo'])
		if('tipo' in defect):
			defect_report += 'Tipo: {}\n'.format(defect['tipo'])
		if('subtipo' in defect):
			defect_report += 'Subtipo: {}\n'.format(defect['subtipo'])
		if('localização' in defect):
			defect_report += 'Latitude: {}\n'.format(defect['localização']['latitude'])
			defect_report += 'Longitude: {}\n\n'.format(defect['localização']['longitude'])
		i += 1
	
	report += defect_report
	return report
