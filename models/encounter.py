import uuid

class Encounter:
	def __init__(self):
		self.id = str(uuid.uuid4())
		self.parent = None
		self.name = None
		self.slug = None
		self.combatants = []
		self.meta = {}
   	