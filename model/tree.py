class Tree(object):
	def __init__(self, data, parent=None):
		self.__data = data
		self.__children = []
		self.__parent = parent

	def get_data(self):
		return self.__data

	def set_data(self, data):
		self.__data = data

	def get_children(self):
		return self.__children

	def set_children(self, children):
		self.__children = children
	
	def get_parent(self):
		return self.__parent
	
	def set_parent(self, parent):
		self.__parent = parent

	
	def add_child(self, child):
		self.__children.append(child)
	
	def remove_child(self, data, compare):
		for child in self.__children:
			child_data = child.get_data()
			if compare( child_data, data ):
				self.__children.remove( child )
	
	def show(self, recursive=False, level=0):
		print('-'*level, end="")
		print(self.__data)
		
		if recursive:
			for child in self.__children:
				child.show(recursive=recursive, level=level+1)
	
	def __str__(self):
		return "{}".format(self.__data)


def setup_tree(content, parent=None):
	data = {
		"content":"root",
		"type":"root",
	}
	if parent is not None:
		data["content"] = content["content"]
		data["type"] = content["type"]
		children = content["children"]
	else:
		children = content["root"]

	t  = Tree(data=data, parent=parent)
	for child in children:
		c = setup_tree(child, t)
		t.add_child(c)

	return t