from datetime import datetime

class Defect():
	def __init__(self, **kwargs):
		if(kwargs):
			_flow = kwargs.get('flow')
			_photos = kwargs.get('photos')
			self.__flow = _flow if _flow else []
			self.__photos = _photos if _photos else []		
		else:
			self.__flow = []
			self.__photos = []
	
	def get_flow(self):
		return self.__flow
	def get_photos(self):
		return self.__photos
	def set_flow(self, flow):
		self.__flow = flow
	def set_photos(self, photos):
		self.__photos = photos
	
	def add_step(self, step):
		self.__flow.append(step)
	
	def pop_step(self):
		step = None
		len_flow = len(self.__flow)
		if len_flow > 0:
			step = self.__flow[len_flow - 1]
			del self.__flow[len_flow - 1]
		return step

	def add_photo(self, photo):
		self.__photos.append(photo)
	
	def pop_photo(self):
		photo = None
		len_photos = len(self.__photos)
		if len_photos > 0:
			photo = self.__photos[len_photos - 1]
			del self.__photos[len_photos - 1]
		return photo

	def to_json(self):
		out = {
			"flow": self.__flow,
			"photos": self.__photos
		}
		return out


class Inspection():
	def __init__(self, **kwargs):
		_inspec = kwargs.get('inspec')
		if(_inspec):
			self.__code = _inspec['code']
			self.__trafo = _inspec['trafo']
			self.__created_at = _inspec['created_at']
			self.__last_update = _inspec['last_update']
			self.__latitude = _inspec['latitude']
			self.__longitude = _inspec['longitude']
			self.__defects = [ Defect(flow=defect['flow'], photos=defect['photos']) for defect in _inspec['defects'] ]
			self.__defects.append(Defect())
		else:
			self.__code = kwargs.get('code')
			self.__trafo = kwargs.get('trafo')
			self.__created_at = datetime.now().strftime("%d/%m/%Y")
			self.__last_update = None
			self.__latitude = kwargs.get('latitude')
			self.__longitude = kwargs.get('longitude')
			self.__defects = []


	def get_code(self):
		return self.__code
	def get_created_at(self):
		return self.__created_at
	def get_last_update(self):
		return self.__last_update
	def get_latitute(self):
		return self.__latitude
	def get_longitude(self):
		return self.__longitude
	def get_trafo(self):
		return self.__trafo
	def get_defects(self):
		return self.__defects
	def set_code(self, thing):
		self.__last_update = datetime.now().strftime("%d/%m/%Y")
		self.__code = thing
	def set_created_at(self, thing):
		self.__last_update = datetime.now().strftime("%d/%m/%Y")
		self.__created_at = thing
	def set_last_update(self, thing):
		self.__last_update = datetime.now().strftime("%d/%m/%Y")
		self.__last_update = thing
	def set_latitude(self, thing):
		self.__last_update = datetime.now().strftime("%d/%m/%Y")
		self.__latitude = thing
	def set_longitude(self, thing):
		self.__last_update = datetime.now().strftime("%d/%m/%Y")
		self.__longitude = thing
	def set_trafo(self, thing):
		self.__last_update = datetime.now().strftime("%d/%m/%Y")
		self.__trafo = thing
	def set_defects(self, thing):
		self.__last_update = datetime.now().strftime("%d/%m/%Y")
		self.__defects = thing
	
	def generate_report(self):
		header = "RESUMO\n"
		header += "Código {}\n".format(self.__code)
		header += "Trafo: {}\n".format(self.__trafo)
		header += "Iniciada em: {}\n".format(self.__created_at)
		header += "Última modificação: {}\n".format(self.__last_update)
		header += "Latitude: {}\n".format(self.__latitude)
		header += "Longitude: {}\n".format(self.__longitude)

		defects_report = "\n---- Defeitos ----\n"
		i = 1
		for defect in self.__defects:
			defect_flow = defect.get_flow()
			flow = "Defeito {}\n".format(i)
			for step in defect_flow:
				flow += str(step) + ">"
			flow += "\n"
			n_photos = len( defect.get_photos() )
			n_photos = "Imagens: {}\n\n".format(n_photos)
			defects_report += flow + n_photos
			i += 1
		report = header + defects_report
		return report

	def add_step(self, step):
		defects = self.get_defects()
		len_defects = len(defects)
		if len_defects > 0:
			defect = defects[len_defects - 1]
		else:
			defect = Defect()

		defect.add_step(step)
		if len_defects > 0 :
			defects[len_defects - 1] = defect
		else:
			defects.append(defect)

		self.set_defects(defects)
	
	def pop_step(self):
		step = None
		defects = self.get_defects()
		len_defects = len(defects)
		if len_defects > 0:
			defect = defects[len_defects - 1]
			step = defect.pop_step()
			defects[len_defects - 1] = defect
			
		self.set_defects(defects)
		return step

	def add_defect(self):
		defects = self.get_defects()
		new_defect = Defect()
		defects.append(new_defect)
		self.set_defects(defects)
		
	def pop_defect(self):
		defect = None
		defects = self.get_defects()
		len_defects = len(defects)
		if len_defects > 0:
			defect = defects[len_defects - 1]
			del defects[len_defects - 1]
		self.set_defects(defects)
		return defect
	
	def add_photo(self, photo_path):
		defects = self.get_defects()
		len_defects = len(defects)
		if len_defects > 0:
			defects[len_defects - 1].add_photo(photo_path)
		self.set_defects(defects)
		
	def to_json(self):
		out = {
			"code":self.__code,
			"trafo":self.__trafo,
			"created_at":self.__created_at,
			"last_update":self.__last_update,
			"latitude":self.__latitude,
			"longitude":self.__longitude,
			"defects":[defect.to_json() for defect in self.__defects]
		}
		return out