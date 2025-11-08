from __future__ import annotations

from unittest.mock import Mock

import pytest

from app.application.doc_units.events import HierarchyLoaded
from app.application.doc_units.use_cases.hierarchy.load_hierarchy import LoadHierarchy
from app.domain.doc_units.entities import HierarchyNode
from app.domain.doc_units.value_objects import DocUnitId


def test_load_hierarchy_fetches_and_publishes_event():
    hierarchy = HierarchyNode(
        node_id="root",
        name="Chapter",
        node_type=HierarchyNode.FOLDER_TYPE,
        settings={},
        children=[],
    )

    repository = Mock()
    repository.get_hierarchy.return_value = hierarchy

    active_store = Mock()
    active_store.get.return_value = DocUnitId("unit-1")

    events = Mock()

    use_case = LoadHierarchy(repository, active_store, events)
    result = use_case.execute()

    assert result is hierarchy
    repository.get_hierarchy.assert_called_once_with(DocUnitId("unit-1"))

    events.publish.assert_called_once()
    event = events.publish.call_args[0][0]
    assert isinstance(event, HierarchyLoaded)
    assert event.unit_id == "unit-1"
    assert event.root is hierarchy


def test_load_hierarchy_requires_active_unit():
    repository = Mock()
    active_store = Mock()
    active_store.get.return_value = None
    events = Mock()

    use_case = LoadHierarchy(repository, active_store, events)

    with pytest.raises(RuntimeError):
        use_case.execute()

    repository.get_hierarchy.assert_not_called()
    events.publish.assert_not_called()
