from rdflib import Namespace
from rdflib import Graph, RDF, Literal
import urllib.parse
from context_interpreter import ContextInterpreter
from language_server_communicator import LanguageServerCommunicator

class OWLConstructor(ContextInterpreter, LanguageServerCommunicator):

    """ Class for constructing an OWL representation of a code base. 
    
    This class contains methods for creating nodes, object properties, and data properties in an OWL representation of a code base.
    Custom Definitions are used along side definitions from SEON to define the classes, object properties, and data properties.
    
    """

    initializationPhase = True
    currentFilePath = None
    currentFileInstance = None
    fileInstances = []

    _custom_definitions_namespace = Namespace("http://definitions.moonshot.sep/_#")
    _custom_instances_namespace = Namespace("http://instances.moonshot.sep/_#")
    _SEON_general = Namespace("http://www.w3.org/2002/07/owl")
    _SEON_main = Namespace("http://se-on.org/ontologies/general/2012/2/main.owl#")
    _SEON_code = Namespace("http://se-on.org/ontologies/domain-specific/2012/02/code.owl#")
        
    # Define classes
    _OWL_classes = {
        "Thing": _SEON_general.Thing,
        "AccessModifier": _SEON_code.AccessModifier,
        "AnnotationType": _SEON_code.AnnotationType,
        "Artifact": _SEON_main.Artifact,
        "ClassType": _SEON_code.ClassType,
        "CodeEntity": _SEON_code.CodeEntity,
        "ComplexType": _SEON_code.ComplexType,
        "Constructor": _SEON_code.Constructor,
        "Datatype": _SEON_code.Datatype,
        "EnumerationType": _SEON_code.EnumerationType,
        "ExceptionType": _SEON_code.ExceptionType,
        "Field": _SEON_code.Field,
        "File": _SEON_main.File,
        "InterfaceType": _SEON_code.InterfaceType,
        "Method": _SEON_code.Method,
        "Namespace": _SEON_code.Namespace,
        "Nothing": _SEON_general.Nothing,
        "Parameter": _SEON_code.Parameter,
        "PrimitiveType": _SEON_code.PrimitiveType,
        "SeonThing": _SEON_main.SeonThing,
        "Variable": _SEON_code.Variable,
    }
    # Define object properties
    _OWL_object_properties = {
        "simple": { # These edges can be created during the initialization phase.
            "containsCodeEntity": _SEON_code.containsCodeEntity,
            "declaresField": _SEON_code.declaresField,
            "declaresMethod": _SEON_code.declaresMethod,
            "declaresConstructor": _SEON_code.declaresConstructor,
            "hasAccessModifier": _SEON_code.hasAccessModifier,
            "hasNamespaceMember": _SEON_code.hasNamespaceMember,
            "hasParameter": _SEON_code.hasParameter,
            "isDeclaredConstructorOf": _SEON_code.isDeclaredConstructorOf,
            "isDeclaredFieldOf": _SEON_code.isDeclaredFieldOf,
            "isDeclaredMethodOf": _SEON_code.isDeclaredMethodOf,
            "isNamespaceMemberOf": _SEON_code.isNamespaceMemberOf,
            "isParameterOf": _SEON_code.isParameterOf,
        },
        "complex": { # These edges must be created after the initialization phase.
            "accessesField": _SEON_code.accessesField,
            "catchesException": _SEON_code.catchesException,
            "constructorIsInvokedBy": _SEON_code.constructorIsInvokedBy,
            "dependsOn": _SEON_main.dependsOn,
            "expectsDatatype": _SEON_code.expectsDatatype,
            "hasChild": _SEON_main.hasChild,
            "hasDatatype": _SEON_code.hasDatatype,
            "hasParent": _SEON_main.hasParent,
            "hasReturnType": _SEON_code.hasReturnType,
            "hasSubClass": _SEON_code.hasSubClass,
            "hasSubInterface": _SEON_code.hasSubInterface,
            "hasSubtype": _SEON_code.hasSubtype,
            "hasSuperClass": _SEON_code.hasSuperClass,
            "hasSuperInterface": _SEON_code.hasSuperInterface,
            "hasSuperType": _SEON_code.hasSuperType,
            "implementsInterface": _SEON_code.implementsInterface,
            "instantiatesClass": _SEON_code.instantiatesClass,
            "invokesConstructor": _SEON_code.invokesConstructor,
            "invokesMethod": _SEON_code.invokesMethod,
            "isAccessedBy": _SEON_code.isAccessedBy,
            "isCaughtBy": _SEON_code.isCaughtBy,
            "isDatatypeOf": _SEON_code.isDatatypeOf,
            "isExpectedDatatype": _SEON_code.isExpectedDatatype,
            "isImplementedBy": _SEON_code.isImplementedBy,
            "isInstantiatedBy": _SEON_code.isInstantiatedBy,
            "isReturnTypeOf": _SEON_code.isReturnTypeOf,
            "isThrownBy": _SEON_code.isThrownBy,
            "methodIsInvokedBy": _SEON_code.methodIsInvokedBy,
            "throwsException": _SEON_code.throwsException,
            "usesComplexType": _SEON_code.usesComplexType,

            # Custom object properties
            "isNestedNamespaceIn": _SEON_code.isNestedNamespaceIn,
            "hasNestedNamespaceMember": _SEON_code.hasNestedNamespaceMember,
            "isNestedComplexTypeIn": _SEON_code.isNestedComplexTypeIn,
            "hasNestedComplexTypeMember": _SEON_code.hasNestedComplexTypeMember,
        },
    }
    # Define data properties
    _OWL_data_properties = {
        "hasCodeIdentifier": _SEON_code.hasCodeIdentifier,
        "hasDoc": _SEON_code.hasDoc,
        "hasIdentifier": _SEON_code.hasIdentifier,
        "hasLength": _SEON_code.hasLength,
        "hasPosition": _SEON_code.hasPosition,
        "isAbstract": _SEON_code.isAbstract,
        "isConstant": _SEON_code.isConstant,
        "isStatic": _SEON_code.isStatic,
        "startsAt": _SEON_code.startsAt,

        # Custom data properties
        "isStaticComplexType": _custom_definitions_namespace.isStaticComplexType,
        "isStaticVariable": _custom_definitions_namespace.isStaticVariable,
        "isExternalImport": _custom_definitions_namespace.isExternalImport,
    }

    def __init__(self, lsp):
        super().__init__(lsp)
        # Setting up RDF stuff.
        g = Graph()
        g.bind("ns1", self._custom_definitions_namespace)
        g.bind("SEON_general", self._SEON_general)
        g.bind("SEON_main", self._SEON_main)
        g.bind("SEON_code", self._SEON_code)
        self._g = g
        self._code_graph = Graph().parse("http://se-on.org/ontologies/domain-specific/2012/02/code.owl")        
        
        # Get all class names that are subclasses of CodeEntity
        self.codeEntityClassNames = [x.split("#")[-1] for x in self._get_sub_classes_recursively(self._OWL_classes["CodeEntity"])]

    """ Handle node, object property, and data property creation """

    def create_node_for_current_file(self, ctx):
        """ Create a node for the current file."""
        self.currentFileInstance = self.create_OWL_class_instance(ctx, "File", self.currentFilePath)
        self.fileInstances.append(self.currentFileInstance)

    def set_OWL_language_specifics(self, namespaceName: str, namespaceString: str, classes: list, object_properties: list, data_properties: list):
        """ Add additional language specific classes, object properties, and data properties to the OWL representation."""
        
        if not self.initializationPhase:
            return
        
        # Bind new namespace
        new_namespace = Namespace(namespaceString)
        self._g.bind(namespaceName, new_namespace)

        # Add all new classes, object properties, and data properties to the OWL representation
        for class_name in classes:
            self._OWL_classes[class_name] = new_namespace[class_name]
        for object_property in object_properties:
            self._OWL_object_properties["complex"][object_property] = new_namespace[object_property]
        for data_property in data_properties:
            self._OWL_data_properties[data_property] = new_namespace[data_property]

    def create_OWL_class_instance(self, ctx, class_name: str, instance_name: str):
        """ Create an instance of a class in the OWL representation."""
        
        id = self.create_deterministic_node_id_from_ctx(ctx)
        instance_name = self._clean_instance_name(instance_name)
        instance = self.get_instance_from_id(instance_name, id)  

        # Only create new nodes in the initialization phase
        if self.initializationPhase:
            self._g.add((instance, RDF.type, self._OWL_classes[class_name]))
            self.create_OWL_data_property_instance(instance, "hasIdentifier", id)
            if (not class_name == "PrimitiveType") and class_name in self.codeEntityClassNames:
                self.create_OWL_object_property_instance(self.currentFileInstance, instance, "containsCodeEntity")

        return instance

    def create_OWL_object_property_instance(self, from_instance, to_instance, property_name: str):        
        """ Create an instance of an object property in the OWL representation."""
        
        # In the initialization phase, only create simple object properties
        if self.initializationPhase:
            if not property_name in self._OWL_object_properties["simple"]:
                return None
            edge_type = self._OWL_object_properties["simple"][property_name]
        # In the post-initialization phase, create complex object properties
        else:
            if not property_name in self._OWL_object_properties["complex"]:
                return None
            edge_type = self._OWL_object_properties["complex"][property_name]

        self._g.add((from_instance, edge_type, to_instance)) 

    def create_OWL_data_property_instance(self, instance, property_name: str, property_value):
        """ Create an instance of a data property in the OWL representation."""
        
        if not self.initializationPhase:
            return
        
        self._g.add((instance, self._OWL_data_properties[property_name], Literal(property_value)))

    def _get_sub_classes_recursively(self, class_uri):
        """ Get all subclasses of a class recursively"""
        
        # Construct query
        sub_class_query = f'''
            SELECT ?subClass
            WHERE {{
                {f"?subClass rdfs:subClassOf <{class_uri}> . "}
            }}
        '''
        rows = self._code_graph.query(sub_class_query)
        nested_sub_classes = []
        for row in rows:
            sub_class = row['subClass']
            # Recursively get all sub classes
            nested_sub_classes += self._get_sub_classes_recursively(sub_class)
        
        # If no new sub classes are found, return the current classes
        return [class_uri] + nested_sub_classes

    """ Get instances from other attriutes """

    def get_instances_from_code_identifier(self, instance_name, class_name = None, isDeclaredMethodOf = None, isDeclaredFieldOf = None, hasDatatype = None):
        """ Get instances from the code identifier of the instance.
        
        Some additional parameters can be passed to filter the instances.
        
        """

        instance_name = self._clean_instance_name(instance_name)
        # Checks all sub types.
        # e.g. if class_name is "Datatype", it should check for instances of type "PrimitiveType", "ComplexType", etc.
        sub_types = self._get_sub_classes_recursively(self._OWL_classes[class_name])
        sub_types_values = ' '.join(f"<{uri}>" for uri in list(sub_types))

        query = f'''
            SELECT ?description
            WHERE {{
                ?description rdf:type ?type .
                {f'?description SEON_code:hasCodeIdentifier "{instance_name}" .' if instance_name else ""}
                {f'?description SEON_code:isDeclaredMethodOf <{isDeclaredMethodOf}> .' if isDeclaredMethodOf else ""}
                {f'?description SEON_code:isDeclaredFieldOf <{isDeclaredFieldOf}> .' if isDeclaredFieldOf else ""}
                {f'?description SEON_code:hasDatatype <{hasDatatype}> .' if hasDatatype else ""}
                VALUES ?type {{ {sub_types_values} }}
            }}
        '''

        qres = self._g.query(query)
        return list(set([x['description'] for x in qres])) # Remove duplicates 

    def _clean_instance_name(self, instance_name):
        """ Clean the instance name by removing brackets and encoding the class name."""
        
        if not instance_name:
            return None
        # Remove brackets, which indicate if an array of that class is created
        if "[" in instance_name:
            instance_name = instance_name.split("[")[0]

        # Encode class name in order to keep the type parameter which is used
        if "<" in instance_name or "|" in instance_name:
            instance_name = urllib.parse.quote_plus(instance_name)
        return instance_name
    
    def get_instance_from_code_identifier(self, instance_name, class_name = None, isDeclaredMethodOf = None, isDeclaredFieldOf = None, hasDatatype = None):
        """ Get an instance from the code identifier of the instance.
        
        Some additional parameters can be passed to filter the instances.

        """
        
        instance_name = self._clean_instance_name(instance_name)
        descriptions = self.get_instances_from_code_identifier(instance_name, class_name, isDeclaredMethodOf, isDeclaredFieldOf, hasDatatype)
        if len(descriptions) == 0 and not self.initializationPhase:
            node_id = self.create_deterministic_node_id_from_ctx(None)
            node = self._create_external_OWL_class_instance_if_instance_does_not_exists(instance_name, class_name, node_id)
            return node

        elif len(descriptions) == 1:
            for row in descriptions:
                return row

    def get_instance_from_id(self, instance_name, id: str):
        """ Get an instance from the code identifier of the instance and the id."""

        instance_name = self._clean_instance_name(instance_name)
        return self._custom_instances_namespace[f"{instance_name}_{id}"]

    """ Get attributes from instances """

    def get_attribute_instance_from_instance(self, instance, attribute_name):
        """ Get an attribute instance from an instance."""

        if self.initializationPhase:
            return None
        # Only allow getting attributes that have been created during the initialization phase.
        if attribute_name not in self._OWL_data_properties and attribute_name not in self._OWL_object_properties["simple"]:
            return None

        query = f"""
            SELECT ?{attribute_name}
            WHERE {{
                <{instance}> SEON_code:{attribute_name} ?{attribute_name} .
            }}
        """
        qres = self._g.query(query)
        # Remove duplicates
        attributes = list(set([x[attribute_name] for x in qres])) 
        
        return attributes[-1] if attributes else None

    def get_resource_from_instance(self, instance, override_first_tree_walk = False):
        """ Get the resource from an instance."""
        
        if self.initializationPhase and not override_first_tree_walk:
            return []
        # construct query
        query = f"""
            SELECT ?resource
            WHERE {{
                <{instance}> rdf:type ?resource .
            }}
        """
        qres = self._g.query(query)
        # Remove duplicates
        result = list(set([x['resource'] for x in qres]))
        if len(result) >= 1:
            return result[0]
        return None

    def get_graph(self):
        """ Get the graph."""
        
        return self._g
    
    """ Handle nodes that are imported in the code base """

    def _create_external_OWL_class_instance_if_instance_does_not_exists(self, instance_name, class_name, id):
        """ Create an instance of a class in the OWL representation if the instance does not exist.
        
        This instance will be marked as an external import.

        """
        
        if self.initializationPhase:
            return None

        instance = self.get_instance_from_id(instance_name, id)
        self._g.add((instance, RDF.type, self._OWL_classes[class_name]))
        # TODO: Change to use create_OWL_data_property_instance
        self._g.add((instance, self._OWL_data_properties["hasCodeIdentifier"], Literal(instance_name)))
        self._g.add((instance, self._OWL_data_properties["hasIdentifier"], Literal(id)))
        self._g.add((instance, self._OWL_data_properties["isExternalImport"], Literal(True)))
        return instance

    def _create_external_OWL_class_instance_if_instance_does_not_exists_from_filename_line_column(self, instance_name: str, class_name: str, filename: str, line: int, column: int):
        """ Create an instance of a class in the OWL representation if the instance does not exist.

        This instance will be marked as an external import.

        """

        
        if self.initializationPhase:
            return None

        node_id = self.create_deterministic_node_id_from_filename_line_column(filename, line, column)
        return self._create_external_OWL_class_instance_if_instance_does_not_exists(instance_name, class_name, node_id)
    
    """ Language server interactions """

    def get_instance_from_lsp_definition(self, callOrAccessCtx, instance_name, class_name = None, override_first_tree_walk = False):
        """ Get an instance by means of using the language server.
        
        This method is used to get the instance of the thing being accessed.
        It returns the instance of its declaration.
        
        """
        
        if self.initializationPhase and not override_first_tree_walk:
            return None

        instance_name = self._clean_instance_name(instance_name)

        # Call language server with request: "Where is the thing defined?"
        result = self.request_definition_from_ctx(callOrAccessCtx)

        # Get def line and def column from response
        if len(result) != 1:
            return None
        def_line, def_column, def_file_name = result[0]

        # Ignore things defined outside of codebase.
        if def_file_name.startswith("file://"):
            def_file_name = def_file_name[7:]
        else:
            if not self.initializationPhase and class_name:
                return self._create_external_OWL_class_instance_if_instance_does_not_exists_from_filename_line_column(instance_name, class_name, def_file_name, def_line, def_column)
            return None

        # Create unique identifier from this
        id = self.create_deterministic_node_id_from_filename_line_column(def_file_name, def_line, def_column)
        # Get the instance with this ID.
        query = f'''
            SELECT ?description
            WHERE {{
                ?description SEON_code:hasIdentifier "{id}" .
                ?description SEON_code:hasCodeIdentifier "{instance_name}" .

            }}
        '''
        qres = self._g.query(query)
        descriptions = list(set([x['description'] for x in qres]))
        
        if len(descriptions) == 1:
            for row in descriptions:
                return row

    ''' Other usage of the language server'''
    
    def get_locations_where_field_method_constructor_instance_is_referenced(self, ctx):
        """ Get locations where a field, method, or constructor instance is referenced.
        
        This method is used to get the locations where a field, method, or constructor instance is referenced.

        """

        if self.initializationPhase:
            return []

        # Call language server with
        result = self.request_references_from_ctx(ctx)

        ret = []
        
        # Format the output of the lsp call
        for (def_line, def_column, def_file_name) in result:
            if def_file_name.startswith("file://"):
                def_file_name = def_file_name[7:]
            else:
                continue
            ret.append((def_file_name, def_line, def_column))
        return ret

    def get_instances_where_field_method_constructor_instance_is_refferenced(self, ctx):
        """ Get instances where a field, method, or constructor instance is referenced."""

        locations = self.get_locations_where_field_method_constructor_instance_is_referenced(ctx)

        ret = []
        # Loop through the locations and create the instances
        for def_file_name, def_line, def_column in locations:
            id = self.create_deterministic_node_id_from_filename_line_column(def_file_name, def_line, def_column)
            ret.append(id)

        return ret

    def get_instances_where_file_is_defined(self, line, col, file_name, instance):
        """ Uses the language server to obtain what files are referenced by the current file """

        if self.initializationPhase:
            return []

        # Call language server with
        result = self.request_definition_from_file_line_column(file_name, line, col)

        files = []
        # Create the list of file instances
        for (_, _, def_file_name) in result:
            if def_file_name.startswith("file://"):
                def_file_name = def_file_name[7:]
            else:
                continue
            for file_instance in self.fileInstances:
                if def_file_name in file_instance:
                    if file_instance not in files and file_instance != instance:
                        files.append(file_instance)
        
        return files