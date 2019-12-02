import uuid

class Map:
	def __init__(self):
		self.id = str(uuid.uuid4())
		self.parent = None
		self.name = None
		self.slug = None
		self.gridColor = None
		self.gridSize = None
		self.gridOffsetX = None
		self.gridOffsetY = None
		self.image = None
		self.video = None
		self.scale = None
		self.markers = []
		self.meta = {}
   	