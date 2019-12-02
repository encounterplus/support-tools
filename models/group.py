import uuid

class Group:
	def __init__(self):
		self.id = str(uuid.uuid4())
		self.parent = None
		self.name = None
		self.slug = None