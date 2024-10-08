from dynpy.core import context, reader
from dynpy.core.context import DynamoFileContext

from tests.helper import DYNAMO_FILE, create_test_file


def test_write_same_structure():
    dyn_content = reader.read_json(DYNAMO_FILE)
    test_file = create_test_file(DYNAMO_FILE)
    with DynamoFileContext(test_file) as ctx:
        node_id = context.node_uuid(ctx.nodes[0])
        ctx.replace_code(node_id, "print('Hello World')")
    test_content = reader.read_json(test_file)
    for dyn_key, test_key in zip(dyn_content.keys(), test_content.keys()):
        assert dyn_key == test_key
