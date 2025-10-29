from PyFlow.Core import NodeBase
from PyFlow.Core.NodeBase import NodePinsSuggestionsHelper
from PyFlow.Core.Common import *
from core.core import Core


class PipelineOutputNode(NodeBase):
    def __init__(self, name):
        super(PipelineOutputNode, self).__init__(name)
        self.core = Core()
        self.remove_post_create = False
        
        self.pipeline_result_image_input_pin = self.createInputPin('Image', 'ImageArrayPin')

        self._register_as_output_node()


    def postCreate(self, jsonTemplate=None):
        super().postCreate(jsonTemplate)
        if self.remove_post_create:
            self.kill()
    

    @staticmethod
    def pinTypeHints():
        helper = NodePinsSuggestionsHelper()
        helper.addInputDataType('ImageArrayPin')
        helper.addInputStruct(StructureType.Single)
        return helper

    @staticmethod
    def category():
        return 'Pipeline output'

    @staticmethod
    def keywords():
        return ['pipeline']

    @staticmethod
    def description():
        return "Description in rst format."
    

    def isCallable(self):
        return True
    

    def _register_as_output_node(self):
        self.core.pipelines_manager.pyflow_interaction_manager.set_output_node(self)


    def compute(self, *args, **kwargs):
        print("Pipeline output comput")
        resulting_image = self.pipeline_result_image_input_pin.getData()
        return resulting_image
        
