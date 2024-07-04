from owl_constructor import OWLConstructor
from rdflib import Namespace, Graph, RDF, Literal
from test_base_context_interpreter import TestBaseContextInterpreter, Context
from unittest.mock import patch, MagicMock
import uuid

## This is the base class for all the test classes.
## It contains all the test cases relevant for the OWLConstructor class, 
## which is the parent class of all the Listener classes.
class TestBaseClass(TestBaseContextInterpreter):
    target: OWLConstructor
    custom_UUID = '00000000_0000_0000_0000_000000000001'
    _custom_definitions_namespace = Namespace("http://definitions.moonshot.sep/_#")
    _custom_instances_namespace = Namespace("http://instances.moonshot.sep/_#")
    _SEON_general = Namespace("http://www.w3.org/2002/07/owl")
    _SEON_main = Namespace("http://se-on.org/ontologies/general/2012/2/main.owl#")
    _SEON_code = Namespace("http://se-on.org/ontologies/domain-specific/2012/02/code.owl#")
    testFilePath = None
    testFileInstance = None
    methodInstance = None
    ruleNames = None
    mock_id = '1_1_4886718345'

    # Instances used to test methods
    class_instance = _custom_instances_namespace[f'Class_{mock_id}c']
    method_instance = _custom_instances_namespace[f'Method_{mock_id}m']
    parent_class_instance = _custom_instances_namespace[f'SuperClass_{mock_id}p']
    datatype_instance_1 = _custom_instances_namespace[f'String_{mock_id}_1']
    duplicated_datatype_instance_1 = _custom_instances_namespace[f'String_{mock_id}_1']
    datatype_instance_2 = _custom_instances_namespace[f'String_{mock_id}_2']
    datatype_instance_3 = _custom_instances_namespace[f'List%3CString%3E_{mock_id}']

    # Define classes
    _OWL_classes = {
        "PrimitiveType": _SEON_code.PrimitiveType,
        "Method": _SEON_code.Method,
        "ClassType": _SEON_code.ClassType,
        "Datatype": _SEON_code.Datatype,
    }

    _OWL_object_properties = {
            "declaresMethod": _SEON_code.declaresMethod,
            "hasSubClass": _SEON_code.hasSubClass,
            "hasSuperClass": _SEON_code.hasSuperClass,
            "isDeclaredMethodOf": _SEON_code.isDeclaredMethodOf,
    }

    _OWL_data_properties = {
        "hasIdentifier": _SEON_code.hasIdentifier,
        "hasCodeIdentifier": _SEON_code.hasCodeIdentifier,
        "isStatic": _SEON_code.isStatic,
    }

    # This setup runs before every test case
    def setUp(self):
        self.target = OWLConstructor(None)
        if self.testFilePath is not None:
            self.target.currentFilePath = self.testFilePath
            self.testFileInstance = self._custom_instances_namespace[f'{self.testFilePath}_{self.mock_id}']
            self.target.currentFileInstance = self.testFileInstance

    ### BEGIN TEST CASES ###
    def test_setup(self):
        """
        Test setup and initialization of the OWLConstructor class
        """
        expectedGraph = Graph()
        expectedGraph.bind("ns1", self._custom_definitions_namespace)
        expectedGraph.bind("SEON_general", self._SEON_general)
        expectedGraph.bind("SEON_main", self._SEON_main)
        expectedGraph.bind("SEON_code", self._SEON_code)
        self.assertGraphs(expectedGraph, self.target.get_graph())

    @patch.object(OWLConstructor, 'create_deterministic_node_id_from_filename_line_column')
    def test_create_node_for_current_file(self, unique_id):
        """
        Test create_node_for_current_file method
        """
        try:
            ctx = self.getContext(Context.FILE_DEFINITION)
        except NotImplementedError:
            pass
        else:
            unique_id.return_value = self.mock_id
            self.target.create_node_for_current_file(ctx)
            self.assertEqual(self.target.currentFileInstance, self.testFileInstance)
            self.assertTrue(self.target.currentFileInstance in self.target.fileInstances)

    def test_clean_instance_name(self):
        """
        Test _clean_instance_name method
        """
        resultNone = self.target._clean_instance_name('')
        resultBrackets = self.target._clean_instance_name('ClassName[0]')
        resultArrows = self.target._clean_instance_name('Class<Parameter>')
        self.assertIsNone(resultNone)
        self.assertEqual(resultBrackets, "ClassName")
        self.assertEqual(resultArrows, "Class%3CParameter%3E")
    
    @patch.object(OWLConstructor, 'create_deterministic_node_id_from_filename_line_column')
    @patch('uuid.uuid4') #NOTE another test can be included to test the hasCodeEntity relationship
    def test_create_OWL_class_instance(self, mock_uuid4, unique_id):
        """
        Test create_OWL_class_instance method
        """
        mock_uuid4.return_value = uuid.UUID('00000000-0000-0000-0000-000000000001')
        unique_id.return_value = self.mock_id
        try:
            ctx = self.getContext(Context.METHOD_DECLARATOR)
        except NotImplementedError:
            pass
        else:
            method_ctx = self.getMethodFromContext(ctx)
            instance = self.target.create_OWL_class_instance(method_ctx, 'Method', self.getMethodName(method_ctx))
            self.assertClassTypeOfInstance(instance, self.target.get_graph(), self._OWL_classes['Method'])
            self.assertDataPropertyInGraph(instance, self.target.get_graph(), self.mock_id)
            self.assertObjectPropertyInGraph(self.target.get_graph(), self.testFileInstance, instance, 'containsCodeEntity')
            self.assertEqual(instance, self.methodInstance)
        
        expectedInstance = self._custom_instances_namespace[f"int_{self.custom_UUID}"]
        self.target.initializationPhase = False
        instance = self.target.create_OWL_class_instance(None, 'PrimitiveType', 'int')
        self.assertDataPropertyNotInGraph(self.target.get_graph(), self.custom_UUID)
        self.assertEqual(instance, expectedInstance)

        self.target.initializationPhase = True
        instance = self.target.create_OWL_class_instance(None, 'PrimitiveType', 'int')
        self.assertDataPropertyInGraph(expectedInstance, self.target.get_graph(), self.custom_UUID)
        self.assertEqual(instance, expectedInstance)
    
    def test_create_OWL_object_property_instance(self):
        """
        Test create_OWL_object_property_instance method
        """
        self.createClassAndMethodNodes()

        def addObjectPropsToGraph():
            self.target.create_OWL_object_property_instance(self.class_instance, self.parent_class_instance, 'hasSuperClass')
            self.target.create_OWL_object_property_instance(self.parent_class_instance, self.class_instance, 'hasSubClass')
            self.target.create_OWL_object_property_instance(self.class_instance, self.method_instance, 'declaresMethod')
            self.target.create_OWL_object_property_instance(self.method_instance, self.class_instance, 'isDeclaredMethodOf')
        
        addObjectPropsToGraph()
        self.assertObjectPropertyNotInGraph(self.target.get_graph(), self.class_instance, self.parent_class_instance, 'hasSuperClass')
        self.assertObjectPropertyNotInGraph(self.target.get_graph(), self.parent_class_instance, self.class_instance, 'hasSubClass')
        self.assertObjectPropertyInGraph(self.target.get_graph(), self.class_instance, self.method_instance, 'declaresMethod')
        self.assertObjectPropertyInGraph(self.target.get_graph(), self.method_instance, self.class_instance, 'isDeclaredMethodOf')

        self.target.initializationPhase = False
        addObjectPropsToGraph()
        self.assertObjectPropertyInGraph(self.target.get_graph(), self.class_instance, self.parent_class_instance, 'hasSuperClass')
        self.assertObjectPropertyInGraph(self.target.get_graph(), self.parent_class_instance, self.class_instance, 'hasSubClass')
        self.assertObjectPropertyInGraph(self.target.get_graph(), self.class_instance, self.method_instance, 'declaresMethod')
        self.assertObjectPropertyInGraph(self.target.get_graph(), self.method_instance, self.class_instance, 'isDeclaredMethodOf')
    
    def test_create_OWL_data_property_instance(self):
        """
        Test create_OWL_data_property_instance method
        """
        instance = self._custom_instances_namespace[f'int_{self.custom_UUID}']
        self.target._g.add((instance, RDF.type, self._OWL_classes['PrimitiveType']))
    
        def addDataPropsToGraph():
            self.target.create_OWL_data_property_instance(instance, "hasIdentifier", self.custom_UUID)
            self.target.create_OWL_data_property_instance(instance, "isStatic", True)

        self.target.initializationPhase = False  
        addDataPropsToGraph()
        self.assertDataPropertyNotInGraph(self.target.get_graph(), self.custom_UUID)
        self.assertDataPropertyNotInGraph(self.target.get_graph(), True, 'isStatic')
        
        self.target.initializationPhase = True
        addDataPropsToGraph()
        self.assertDataPropertyInGraph(instance, self.target.get_graph(), self.custom_UUID)
        self.assertDataPropertyInGraph(instance, self.target.get_graph(), True, 'isStatic')

    @patch.object(OWLConstructor, 'create_deterministic_node_id_from_ctx')
    def test_get_instance_from_code_identifier(self, mocked_method):
        """
        Test get_instance_from_code_identifier method
        """
        mocked_method.return_value = self.custom_UUID
        self.createGraphToTestGetInstanceMethods()

        # There are 2 instances with "hasCodeIdentifier" String
        string_instance = self.target.get_instance_from_code_identifier("String", class_name="Datatype")
        self.assertIsNone(string_instance, "Unexpected output.")

        list_string_instance = self.target.get_instance_from_code_identifier("List%3CString%3E", class_name="Datatype")
        self.assertEqual(list_string_instance, self.datatype_instance_3, "Unexpected output.")

        list_integer_instance = self.target.get_instance_from_code_identifier("List%3CInteger%3E", class_name="Datatype")
        self.assertIsNone(list_integer_instance, "Unexpected output.")

        self.target.initializationPhase = False
        list_integer_instance = self.target.get_instance_from_code_identifier("List%3CInteger%3E", class_name="Datatype")
        self.assertEqual(self._custom_instances_namespace[f'List%3CInteger%3E_{self.custom_UUID}'], list_integer_instance, "Incorrect instance.")
    
    def test_get_instances_from_code_identifier(self):
        """
        Test get_instances_from_code_identifier method
        """
        self.createGraphToTestGetInstanceMethods()

        string_instances = self.target.get_instances_from_code_identifier("String", class_name="Datatype")
        # Check if expected instances are in the outputted array
        self.assertTrue(self.datatype_instance_1 in string_instances, str(self.datatype_instance_1) + " was not found in array")
        self.assertTrue(self.datatype_instance_2 in string_instances, str(self.datatype_instance_2) + " was not found in array")
        self.assertFalse(self.datatype_instance_3 in string_instances, str(self.datatype_instance_3) + " was found in array")

        # Check if expected amount of elements is in the outputted array
        self.assertEqual(len(string_instances), 2, "Amount of instances is unexpected")

    def test_get_attribute_instance_from_instance(self):
        """
        Test get_attribute_instance_from_instance method
        """
        self.createClassAndMethodNodes()
        self.target._g.add((self.class_instance, self._OWL_data_properties['hasIdentifier'], Literal(self.mock_id + 'c')))
        self.target._g.add((self.class_instance, self._OWL_object_properties['declaresMethod'], self.method_instance))
        self.target._g.add((self.class_instance, self._OWL_object_properties['hasSuperClass'], self.parent_class_instance))

        self.target.initializationPhase = True
        self.assertIsNone(self.target.get_attribute_instance_from_instance(self.class_instance, 'hasIdentifier'))
        self.target.initializationPhase = False
        self.assertEqual(self.target.get_attribute_instance_from_instance(self.class_instance, 'hasIdentifier'), Literal(self.mock_id + 'c')) # This is data property
        self.assertEqual(self.target.get_attribute_instance_from_instance(self.class_instance, 'declaresMethod'), self.method_instance) # This is simple object property
        self.assertIsNone(self.target.get_attribute_instance_from_instance(self.class_instance, 'hasSuperClass')) # This is complex object property
        self.assertIsNone(self.target.get_attribute_instance_from_instance(self.class_instance, 'isStatic')) # This prop does not exist is graph
        self.assertIsNone(self.target.get_attribute_instance_from_instance(self.class_instance, 'nonExistent')) # This prop does not exist at all
    
    def test_get_resource_from_instance(self):
        """
        Test get_resource_from_instance method
        """
        self.createClassAndMethodNodes(False)
        
        self.assertEqual(self.target.get_resource_from_instance(self.class_instance), [])
        self.assertEqual(self.target.get_resource_from_instance(self.class_instance, True), self._OWL_classes['ClassType'])

        self.target.initializationPhase = False
        self.assertEqual(self.target.get_resource_from_instance(self.class_instance), self._OWL_classes['ClassType'])
        self.assertEqual(self.target.get_resource_from_instance(self.method_instance), self._OWL_classes['Method'])
        self.assertIsNone(self.target.get_resource_from_instance('nonExistent'))
    
    def test_create_external_OWL_class_instance_if_instance_does_not_exists(self):
        """
        Test _create_external_OWL_class_instance_if_instance_does_not_exists method
        """
        self.create_external_OWL_class_instance_helper(True)
    
    def test_create_external_OWL_class_instance_if_instance_does_not_exists_from_filename_line_column(self):
        """
        Test _create_external_OWL_class_instance_if_instance_does_not_exists_from_filename_line_column method
        """
        self.create_external_OWL_class_instance_helper(False)

    def test_get_instance_from_id(self):
        """
        Test get_instance_from_id method
        """
        expectedInstance = self._custom_instances_namespace['instance_name_id']
        instance = self.target.get_instance_from_id('instance_name', 'id')
        self.assertEqual(instance, expectedInstance)
    
    #
    # There are many more test cases that can be added here. 
    # These are related to the language server which we did not implement yet.
    #

    ### BEGIN HELPER METHODS ###

    def createClassAndMethodNodes(self, parent_instance = True):
        self.target._g.add((self.class_instance, RDF.type, self._OWL_classes['ClassType']))
        self.target._g.add((self.method_instance, RDF.type, self._OWL_classes['Method']))
        if parent_instance:
            self.target._g.add((self.parent_class_instance, RDF.type, self._OWL_classes['ClassType']))

    def createGraphToTestGetInstanceMethods(self):
        self.target._g.add((self.datatype_instance_1, RDF.type, self._OWL_classes['Datatype']))
        self.target._g.add((self.duplicated_datatype_instance_1, RDF.type, self._OWL_classes['Datatype']))
        self.target._g.add((self.datatype_instance_2, RDF.type, self._OWL_classes['Datatype']))
        self.target._g.add((self.datatype_instance_3, RDF.type, self._OWL_classes['Datatype']))

        self.target._g.add((self.datatype_instance_1, self._OWL_data_properties["hasCodeIdentifier"], Literal("String")))
        self.target._g.add((self.duplicated_datatype_instance_1, self._OWL_data_properties["hasCodeIdentifier"], Literal("String")))
        self.target._g.add((self.datatype_instance_2, self._OWL_data_properties["hasCodeIdentifier"], Literal("String")))
        self.target._g.add((self.datatype_instance_3, self._OWL_data_properties["hasCodeIdentifier"], Literal("List%3CString%3E")))

    @patch.object(OWLConstructor, 'get_instance_from_id')
    @patch('hashlib.sha256')
    def create_external_OWL_class_instance_helper(self, has_id: bool, mock_sha256, mocked_instance):
        mock_hexdigest = MagicMock(return_value="123456789") # base16 (4886718345)
        mock_sha256.return_value = MagicMock(hexdigest=mock_hexdigest)

        instance_name = 'externalClass'
        instance_id = self.mock_id
        expected_instance = self._custom_instances_namespace[f'{instance_name}_{instance_id}']
        mocked_instance.return_value = expected_instance

        if has_id:
            self.assertIsNone(self.target._create_external_OWL_class_instance_if_instance_does_not_exists_from_filename_line_column(instance_name, 'ClassType', 'test', 1, 1))
            self.target.initializationPhase = False
            instance = self.target._create_external_OWL_class_instance_if_instance_does_not_exists_from_filename_line_column(instance_name, 'ClassType', 'test', 1, 1)
        else:
            self.assertIsNone(self.target._create_external_OWL_class_instance_if_instance_does_not_exists_from_filename_line_column(instance_name, 'ClassType', 'test', 1, 1))
            self.target.initializationPhase = False
            instance = self.target._create_external_OWL_class_instance_if_instance_does_not_exists_from_filename_line_column(instance_name, 'ClassType', 'test', 1, 1)

        self.assertEqual(instance, expected_instance)
        self.assertClassTypeOfInstance(instance, self.target.get_graph(), self._OWL_classes['ClassType'])
        self.assertDataPropertyInGraph(instance, self.target.get_graph(), instance_name, 'hasCodeIdentifier')
        self.assertDataPropertyInGraph(instance, self.target.get_graph(), instance_id, 'hasIdentifier')
        self.assertDataPropertyInGraph(instance, self.target.get_graph(), True, 'isExternalImport')

    def graph_serialize(self, graph: Graph, format: str = "turtle", encoding: str = "utf-8",):
        return graph.serialize(None, format=format, encoding=encoding).decode(encoding)
    
    def queryGraphForDataProperty(self, graph: Graph, propertyValue, propertyName: str = 'hasIdentifier'):
        if isinstance(propertyValue, str):
            propertyValue = '"' + propertyValue + '"'
        query = f'''
            SELECT ?instance
            WHERE {{
                ?instance SEON_code:{propertyName}|ns1:{propertyName} {propertyValue} .
            }}
        '''
        return graph.query(query)
    
    def queryGraphForObjectProperty(self, graph: Graph, fromInsance: str, toInstance: str, objectProperty):
        query = f'''
            SELECT ?instance
            WHERE {{
                ?instance SEON_code:{objectProperty} <{toInstance}> .
                FILTER (
                    CONTAINS(STR(?instance), "{fromInsance}")
                )
            }}
        '''
        return graph.query(query)
    
    def queryGraphForClassType(self, graph: Graph, instance: str):
        query = f"""
            SELECT ?resource
            WHERE {{
                <{instance}> rdf:type ?resource .
            }}
        """
        qres = graph.query(query)

        result = list(set([x['resource'] for x in qres]))
        if len(result) >= 1:
            return result[0]
        return None
    
    ### CUSTOM ASSERTIONS ###
    def assertClassTypeOfInstance(self, instance: str, graph: Graph, classType):
        self.assertEqual(self.queryGraphForClassType(graph, instance), classType, 'Class type of the instance is not as expected.')

    def assertObjectPropertyNotInGraph(self, graph: Graph, fromInsance: str, toInstance: str, objectProperty):
        self.assertFalse(self.queryGraphForObjectProperty(graph, fromInsance, toInstance, objectProperty), 
                        'Object property ' + objectProperty + ' was found in the graph, whilst should not be there.')

    def assertObjectPropertyInGraph(self, graph: Graph, fromInsance: str, toInstance: str, objectProperty):
        self.assertTrue(self.queryGraphForObjectProperty(graph, fromInsance, toInstance, objectProperty),
                        'No object property ' + objectProperty + ' was found in the graph')

    def assertDataPropertyNotInGraph(self, graph: Graph, propValue, propertyName: str = 'hasIdentifier'):
        self.assertFalse(self.queryGraphForDataProperty(graph, propValue, propertyName), 'Property ' + propertyName + ' with value ' + str(propValue) + 
                         ' was found in the graph whilst none was expected')

    def assertDataPropertyInGraph(self, expectedInstance: str, graph: Graph, propValue, propertyName: str = 'hasIdentifier'):
        queryResult = self.queryGraphForDataProperty(graph, propValue, propertyName)
        self.assertTrue(queryResult, 'No property ' + propertyName + ' with value ' + str(propValue) + ' was found in the graph.')

        #Get the first value of the query result, should be the only one given the uniqueness of the IDs
        for x in queryResult:
            instance = x['instance']
            break
        self.assertEqual(expectedInstance, instance, 'Expected instance is different than the instance added to the graph.')

    def assertGraphs(self, expectedGraph, graph):
        self.assertEqual(self.graph_serialize(expectedGraph), self.graph_serialize(graph)) 
