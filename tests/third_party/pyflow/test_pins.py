from PyFlow.Core.Common import PinDirection
from PyFlow.Core.NodeBase import NodeBase

from PyFlow.Packages.MangaTranslator.Pins import HierarchyPin, ImageArrayPin
from PyFlow.Packages.MangaTranslator.logic import Hierarchy


class DummyNode(NodeBase):
    def __init__(self):
        super().__init__("dummy")


def test_image_array_pin_serialization_drops_data():
    node = DummyNode()
    pin = ImageArrayPin("Image", node, PinDirection.Input)
    pin.setData([1, 2, 3])

    pin.serialize()

    assert pin._data is None


def test_hierarchy_pin_defaults_and_serialization():
    node = DummyNode()
    pin = HierarchyPin("Hierarchy", node, PinDirection.Input)

    assert isinstance(pin.defaultValue(), Hierarchy)

    hierarchy = Hierarchy(text_chunks=["chunk"])
    pin.setData(hierarchy)
    pin.serialize()

    assert pin._data is None
