import os
from PyFlow.Core.PackageBase import PackageBase

class MangaTranslator(PackageBase):
	def __init__(self):
		super(MangaTranslator, self).__init__()
		self.analyzePackage( os.path.dirname(__file__))