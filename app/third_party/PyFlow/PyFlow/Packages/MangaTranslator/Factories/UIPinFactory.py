from PyFlow.UI.Canvas.UIPinBase import UIPinBase
from PyFlow.Packages.MangaTranslator.UI.UIDemoPin import UIDemoPin


def createUIPin(owningNode, raw_instance):
    if raw_instance.__class__.__name__ == "DemoPin":
        return UIDemoPin(owningNode, raw_instance)
    else:
        return UIPinBase(owningNode, raw_instance)
