from PyFlow.Core import NodeBase
from PyFlow.Core.NodeBase import NodePinsSuggestionsHelper
from PyFlow.Core.Common import *

from PyFlow.Packages.MangaTranslator.logic import NodeLogicError, TranslationLogic


class TranslationNode(NodeBase):
    def __init__(self, name):
        super(TranslationNode, self).__init__(name)

        self.translator = TranslationLogic()

        self.text_inp_pin = self.createInputPin('Text', 'StringPin', structure=StructureType.Array)
        self.translated_text_out_pin = self.createOutputPin('Translation', 'StringPin', structure=StructureType.Array)

    @staticmethod
    def pinTypeHints():
        helper = NodePinsSuggestionsHelper()
        helper.addInputDataType('StringPin')
        helper.addOutputDataType('StringPin')
        helper.addInputStruct(StructureType.Array)
        helper.addOutputStruct(StructureType.Array)
        return helper

    @staticmethod
    def category():
        return 'Translation'

    @staticmethod
    def keywords():
        return []

    @staticmethod
    def description():
        return "Translates text and gives list of 1 : 1 size of input list with translations."

    def compute(self, *args, **kwargs):
        text_list = self.text_inp_pin.getData()
        
        if text_list is None:
            self.setError("Text input missing")
            return
        
        try:
            translation = self.translator.run(text_list)
        except NodeLogicError as exc:
            self.setError(str(exc))
            return

        self.translated_text_out_pin.setData(translation)

