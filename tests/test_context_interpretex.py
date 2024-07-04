import unittest
from test_base_context_interpreter import TestBaseContextInterpreter

## This class runs tests for the OWLConstructor class, which are in the TestBaseClass.
class TestOWLConstructor(TestBaseContextInterpreter, unittest.TestCase):
    def setUpClass():
        print('''
        These tests run the ContextInterpreter class in the owl_constructor.py file.
        ''')

    def tearDownClass():
        print('''
        Finshed testing the ContextInterpreter class.
        ''')

if __name__ == '__main__':
    unittest.main()
