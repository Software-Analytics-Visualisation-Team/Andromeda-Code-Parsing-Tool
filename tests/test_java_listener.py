import unittest
from test_base_class import TestBaseClass
from test_base_context_interpreter import Context
from antlr4 import FileStream, CommonTokenStream
from antlr_generated_code.java.JavaLexer import JavaLexer
from antlr_generated_code.java.JavaParser import JavaParser

class TestJavaListener(TestBaseClass, unittest.TestCase):
    testFilePath = 'tests/java_test.java'
    methodInstance = TestBaseClass._custom_instances_namespace[f'main_{TestBaseClass.mock_id}']
    javaContext = {
        Context.FILE_DEFINITION: 'compilationUnit',
        Context.METHOD_DECLARATOR: 'methodDeclaration',
        Context.DEFAULT_DEFINITION: 'classDeclaration',
    }
    ruleNames = JavaParser.ruleNames

    def setUpClass():
        print('''
        These tests run the JavaListener class in the JavaListener.py file.
        Currently they are only being run for the methods inherited from the OWLConstructor class.
        ''')

    def tearDownClass():
        print('''
        Finshed testing the JavaListener class.
        ''')
    
    def getContext(self, context_type=Context.DEFAULT_DEFINITION):
        """
        Returns the specified context type from the parsed Java code.
        Parameters: context_type (str): The type of context to retrieve. Defaults to 'classDeclaration'.
        Returns: The specified context type from the parsed Java code.
        Raises: AttributeError: If the specified context type does not exist in the parser object.
        """
        input_stream = FileStream(self.testFilePath)
        lexer = JavaLexer(input_stream)
        token_stream = CommonTokenStream(lexer)
        parser = JavaParser(token_stream)
        if (context_type == Context.FILE_DEFINITION):
            return parser.compilationUnit()
        ctx = self.getContextRecursively(parser.compilationUnit(), self.javaContext[context_type])
        if ctx is None:
            raise AttributeError(f"Context type {context_type.value} not found in the parsed Java code.")
        return ctx
    
    def getMethodName(self, ctx):
        return ctx.identifier().getText()
