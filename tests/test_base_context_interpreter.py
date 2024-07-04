import re
from unittest.mock import patch, MagicMock
from context_interpreter import ContextInterpreter
from enum import Enum

class Context(Enum):
    DEFAULT_DEFINITION = 'default_definition'
    FILE_DEFINITION = 'file_definition'
    METHOD_DECLARATOR = 'method_declarator'

class TestBaseContextInterpreter:
    target: ContextInterpreter

    # This setup runs before every test case
    def setUp(self):
        self.target = ContextInterpreter()

    def test_filename_from_ctx(self):
        """
        Test filename_from_ctx method
        """
        try:
            ctx = self.getContext(Context.FILE_DEFINITION)
        except NotImplementedError:
            pass
        else:
            self.assertEqual(self.target.filename_from_ctx(ctx), self.testFilePath)

    @patch('hashlib.sha256')
    def test_create_deterministic_node_id_from_filename_line_column(self, mock_sha256):
        """
        Test create_deterministic_node_id_from_filename_line_column method
        """
        mock_hexdigest = MagicMock(return_value="123456789") # base16 (4886718345)
        mock_sha256.return_value = MagicMock(hexdigest=mock_hexdigest)
        id = self.target.create_deterministic_node_id_from_filename_line_column('test', 1, 1)
        self.assertEqual(id, '1_1_4886718345')

    @patch('hashlib.sha256')
    def test_create_deterministic_node_id(self, mock_sha256):
        """
        Test _create_deterministic_node_id method
        """
        mock_hexdigest = MagicMock(return_value="123456789") # base16 (4886718345)
        mock_sha256.return_value = MagicMock(hexdigest=mock_hexdigest)
        try:
            ctx = self.getContext()
        except NotImplementedError:
            node_id = self.target.create_deterministic_node_id_from_ctx(None)
            ID_PATTERN = re.compile(r'^[\da-f]{8}_([\da-f]{4}_){3}[\da-f]{12}$', re.IGNORECASE)
            self.assertTrue(bool(ID_PATTERN.match(node_id)), 'No context node ID is not uuid')
        else:
            if hasattr(ctx, 'identifier'):
                column = ctx.identifier().start.column
            else:
                column = ctx.start.column
            line = ctx.start.line
            expectedId = str(line) + '_' + str(column) + '_4886718345'
            id = self.target.create_deterministic_node_id_from_ctx(ctx)
            self.assertEqual(id, expectedId)

            ### BEGIN HELPER METHODS ###

    def getContext(self, context_type = None):
        raise NotImplementedError
    
    def getContextRecursively(self, ctx, context_type):
        if not hasattr(ctx, 'children'):
            return None

        for child in ctx.children:
            if not hasattr(child, 'getRuleIndex'):
                context = self.getContextRecursively(child, context_type)
            else:
                rule_index = child.getRuleIndex()
                if context_type == self.ruleNames[rule_index]:
                    return child
                context = self.getContextRecursively(child, context_type)

            if context is not None:
                return context
        return None

    
    def getMethodFromContext(self, ctx):
        return ctx
    
    def getMethodName(self, ctx):
        return ctx.getText()
    