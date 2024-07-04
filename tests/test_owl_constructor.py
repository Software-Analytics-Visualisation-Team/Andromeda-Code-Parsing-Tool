import unittest
from test_base_class import TestBaseClass

## This class runs tests for the OWLConstructor class, which are in the TestBaseClass.
class TestOWLConstructor(TestBaseClass, unittest.TestCase):
    def setUpClass():
        print('''
        These tests run the OWLConstructor class in the owl_constructor.py file.
        ''')

    def tearDownClass():
        print('''
        Finshed testing the OWLConstructor class.
        ''')

if __name__ == '__main__':
    unittest.main()
