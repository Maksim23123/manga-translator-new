import importlib

import pytest

NodeBaseModule = importlib.import_module("PyFlow.Core.NodeBase")
from PyFlow.Packages.MangaTranslator.Pins import PIN_REGISTRY
from PyFlow.Packages.MangaTranslator.logic import Hierarchy
from PyFlow.Packages.PyFlowBase.Pins.IntPin import IntPin
from PyFlow.Packages.PyFlowBase.Pins.StringPin import StringPin


@pytest.fixture(autouse=True)
def patch_create_raw_pin(monkeypatch):
    """Provide PyFlow with our custom pins without initializing full package registry."""

    def factory(name, owningNode, dataType, direction, **kwargs):
        pin_cls = PIN_REGISTRY.get(dataType)
        if pin_cls is None and dataType == "IntPin":
            pin_cls = IntPin
        if pin_cls is None and dataType == "StringPin":
            pin_cls = StringPin
        if pin_cls is None:
            raise KeyError(f"Unknown pin type requested: {dataType}")
        return pin_cls(name, owningNode, direction, **kwargs)

    monkeypatch.setattr(NodeBaseModule, "CreateRawPin", factory, raising=False)
    yield


def test_text_detector_produces_hierarchy():
    from PyFlow.Packages.MangaTranslator.Nodes.TextDetectorNode import TextDetectorNode

    node = TextDetectorNode("detector")
    node.text_detector = type("StubDetector", (), {"detect": lambda self, image: Hierarchy()})()
    node.image_inp_pin.setData([1, 2, 3])

    node.compute()

    assert isinstance(node.hierarchy_out_pin.getData(), Hierarchy)
    assert node._lastError is None


def test_translation_node_translates_text():
    from PyFlow.Packages.MangaTranslator.Nodes.TranslationNode import TranslationNode

    node = TranslationNode("translator")
    node.translator = type("StubTranslator", (), {"translate": lambda self, texts: [f"stub {t}" for t in texts]})()
    node.text_inp_pin.setData(["hello"])

    node.compute()

    translation = node.translated_text_out_pin.getData()
    assert len(translation) == 1
    assert isinstance(translation[0], str)
    assert translation[0] != ""
    assert node._lastError is None


def test_text_inserter_validates_lengths():
    from PyFlow.Packages.MangaTranslator.Nodes.TextInserterNode import TextInserterNode

    node = TextInserterNode("inserter")
    node.image_inp_pin.setData([1, 2, 3])
    node.text_areas_inp_pin.setData([(0, 0, 1, 1), (1, 1, 2, 2)])
    node.text_inp_pin.setData(["a"])

    node.compute()

    assert "length mismatch" in node._lastError


def test_text_inserter_happy_path():
    from PyFlow.Packages.MangaTranslator.Nodes.TextInserterNode import TextInserterNode

    node = TextInserterNode("inserter")
    node.text_inserter = type("StubInserter", (), {"insert": lambda self, image, areas, texts: image})()
    node.image_inp_pin.setData([1, 2, 3])
    node.text_areas_inp_pin.setData([(0, 0, 1, 1)])
    node.text_inp_pin.setData(["a"])

    node.compute()

    assert node.image_with_text_out_pin.getData() == [1, 2, 3]
    assert node._lastError is None


def test_pipeline_input_node_imports(monkeypatch, tmp_path):
    from PyFlow.Packages.MangaTranslator.Nodes.PipelineInputImageNode import PipelineInputImageNode
    from PyFlow.Packages.MangaTranslator.logic.image_import import ImageImportLogic

    monkeypatch.setattr(ImageImportLogic, "run", lambda self, path: ["imported"])
    image_path = tmp_path / "img.bin"
    image_path.write_bytes(b"data")

    node = PipelineInputImageNode("input")
    node._image_path = str(image_path)

    node.compute()

    assert node.image_out_pin.getData() == ["imported"]
