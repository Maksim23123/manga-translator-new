import os
from PyFlow.Core.PackageBase import PackageBase

class PyFlowBase(PackageBase):
    """Base pyflow package
    """
    def __init__(self):
        super(PyFlowBase, self).__init__()
        self.analyzePackage(os.path.dirname(__file__))