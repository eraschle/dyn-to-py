#!/usr/bin/env python3


from dynpy.core import factory
from dynpy.core.models import NodeInfo, PythonEngine


def test_node_info_to_string():
    """Test NodeInfo im- and export from python file"""
    node_info = NodeInfo(
        uuid='some-uuid', engine=PythonEngine.IRON_PYTHON_2, path='test'
    )
    node_str = (
        "# -*- node-uuid: some-uuid; node-engine: IronPython2; node-path: test"
    )
    assert factory._info_as_str(node_info) == node_str

    restored_info = factory.node_info(node_str)
    assert restored_info == node_info


def test_node_info_to_dict():
    node_info = NodeInfo(
        uuid='some-uuid', engine=PythonEngine.IRON_PYTHON_2, path='test'
    )
    node_dict = factory.node_info_to_dict(node_info)
    assert all(key.startswith("node-") for key in node_dict.keys())
