import unittest
from test_base_class import TestBaseClass
from test_base_context_interpreter import Context
from antlr4 import FileStream, CommonTokenStream
from antlr_generated_code.cpp.CPP14Lexer import CPP14Lexer
from antlr_generated_code.cpp.CPP14Parser import CPP14Parser

class TestCPPListener(TestBaseClass, unittest.TestCase):
    testFilePath = 'tests/cpp_test.cpp'
    methodInstance = TestBaseClass._custom_instances_namespace[f'main_{TestBaseClass.mock_id}']
    cppContext = {
        Context.FILE_DEFINITION: 'translationUnit',
        Context.METHOD_DECLARATOR: 'functionDefinition',
        Context.DEFAULT_DEFINITION: 'functionDefinition',
    }
    ruleNames = CPP14Parser.ruleNames

    def setUpClass():
        print('''
        These tests run the CPPListener class in the CPPListener.py file.
        Currently they are only being run for the methods inherited from the OWLConstructor class.
        ''')

    def tearDownClass():
        print('''
        Finshed testing the CPPListener class.
        ''')
    
    def getContext(self, context_type=Context.DEFAULT_DEFINITION):
        """
        Returns the specified context type from the parsed CPP code.
        Parameters: context_type (str): The type of context to retrieve. Defaults to 'functionDefinition'.
        Returns: The specified context type from the parsed CPP code.
        Raises: AttributeError: If the specified context type does not exist in the parser object.
        """
        input_stream = FileStream(self.testFilePath, encoding='utf-8')
        lexer = CPP14Lexer(input_stream)
        token_stream = CommonTokenStream(lexer)
        parser = CPP14Parser(token_stream)
        if (context_type == Context.FILE_DEFINITION):
            return parser.translationUnit()
        ctx = self.getContextRecursively(parser.translationUnit(), self.cppContext[context_type])
        if ctx is None:
            raise AttributeError(f"Context type {context_type.value} not found in the parsed cpp code.")
        return ctx
    
    def getMethodFromContext(self, ctx):
        return ctx.declarator().pointerDeclarator().noPointerDeclarator().noPointerDeclarator()
