from owl_constructor import OWLConstructor

class JavaListenerBase(OWLConstructor):

    """ Base class for Java listeners. 
    
    Contains shared functionality. 
    
    """

    accessModifierInstances, constructorDictionary = {}, {}
    currentPackageName = None 
    modifiersForNextThingToBeEncountered = []
    fieldsDictionary = {}
    
    def __init__(self, lsp):
        super().__init__(lsp)

        # Set up language specific stuff.
        self.set_OWL_language_specifics("SEON_java", "http://se-on.org/ontologies/system-specific/2012/02/java.owl#", ["JavaPackage"], [], ["hasJavaDoc"])

        # Define a node for each primitive type:
        primitiveTypes = ["byte", "char", "short", "int", "long", "float", "double", "boolean"]
        for primitive in primitiveTypes:
            instance = self.create_OWL_class_instance(None, "PrimitiveType", primitive)
            self.create_OWL_data_property_instance(instance, "hasCodeIdentifier", primitive)

        # Define a node for each access modifier:
        for access_modifier in ["default", "private", "protected", "public"]:
            instance = self.create_OWL_class_instance(None, "AccessModifier", access_modifier)
            self.create_OWL_data_property_instance(instance, "hasCodeIdentifier", access_modifier)
            self.accessModifierInstances[access_modifier] = instance

    """ Things related to keeping track of current complex type instance """

    class ComplexTypeState():
        """ Class that represents the state of a complex type."""

        def __init__(self, instance, modifiers):
            """ Set the instance and modifiers of the complex type state."""

            self.instance = instance
            self.modifiers = modifiers
            self.currentMethodInstance = None

    def requireComplexTypeNestings(func):
        """ Decorator that makes function return None if complexTypeNestings is empty."""

        def wrapper(self, *args, **kwargs):
            """ Wrapper function for the decorator."""

            if not self.complexTypeNestings:
                print("Error: tried to get complexType while complexTypeNestings is empty.")
                return None
            return func(self, *args, **kwargs)
        return wrapper

    # List of ComplexTypeState to keep track of nested type declarations.
    complexTypeNestings = []

    @requireComplexTypeNestings
    def getCurrentMethodInstance(self):
        """ Get the current method instance."""

        return self.complexTypeNestings[-1].currentMethodInstance

    @requireComplexTypeNestings
    def getCurrentComplexTypeInstance(self):
        """ Get the current complex type instance."""

        return self.complexTypeNestings[-1].instance
    
    @requireComplexTypeNestings
    def getCurrentComplexTypeModifiers(self):
        """ Get the current complex type modifiers."""

        return self.complexTypeNestings[-1].modifiers
    
    def setCurrentComplexTypeInstance(self, instance):
        """ Set the current complex type instance."""

        self.complexTypeNestings.append(self.ComplexTypeState(instance, self.modifiersForNextThingToBeEncountered))
        self.modifiersForNextThingToBeEncountered = []

    @requireComplexTypeNestings
    def setCurrentMethodInstance(self, instance):
        """ Set the current method instance."""

        self.complexTypeNestings[-1].currentMethodInstance = instance

    """ OWLConstructor Overrides """

    def get_graph(self):
        """ Get the graph.
        
        Before returning the graph, we add edges between packages that are nested in each other.
        These edges are "hasNestedNamespaceMember" and "isNestedNamespaceIn".
        
        """

        def create_package_pairs(package_list):
            """ Helper function to create pairs of packages that are nested in each other."""

            package_list_split = [package.split(".") for package in package_list]
            pairs = []
            while len(package_list_split) > 0:
                # Get package with most elements
                max_len_package = max(package_list_split, key=len)
                if len(max_len_package) == 1:
                    break
                # Remove this package from the list
                package_list_split.remove(max_len_package)
                # Get the parent package
                parent_package = max_len_package[:-1]
                while len(parent_package) > 0:
                    # Check if package with one element less is in the list.
                    found = False
                    for package in package_list_split:
                        if parent_package == package:
                            found = True
                            break           
                    if found: 
                        break
                    else:
                        parent_package = parent_package[:-1]
                if len(parent_package) > 0:
                    pairs.append((".".join(parent_package), ".".join(max_len_package)))
            return pairs

        # While parsing there is no guarantee that we will encounter package 'a.b.c' before or after 'a.b'.
        # Nor is there a guarantee that there will be a package 'a.b' if there is a package 'a.b.c' and 'a'.
        # Thus we must create edges between packages that are nested in each other after having parsed all packages.
        package_instances = self.get_instances_from_code_identifier(None, class_name = "JavaPackage")
        package_instance_name_pairs = {str(self.get_attribute_instance_from_instance(instance, "hasCodeIdentifier")): instance for instance in package_instances}
        package_pairs = create_package_pairs(package_instance_name_pairs.keys())
        for parent_package, child_package in package_pairs:
            self.create_OWL_object_property_instance(package_instance_name_pairs[parent_package], package_instance_name_pairs[child_package], "hasNestedNamespaceMember")
            self.create_OWL_object_property_instance(package_instance_name_pairs[child_package], package_instance_name_pairs[parent_package], "isNestedNamespaceIn")
        return super().get_graph()

    """ Methods for shared functionality """

    def sharedVariableEnterConfig(self, ctx, instance):
        """ Create properties and edges that are common to all local variables, fields, and parameters."""

        self.create_OWL_data_property_instance(instance, "isConstant", "final" in self.modifiersForNextThingToBeEncountered)
        self.create_OWL_data_property_instance(instance, "isStatic", "static" in self.modifiersForNextThingToBeEncountered)

        # Add "hasLength" and "startsAt" properties.
        variableText = ctx.getText()
        variableLength = len(variableText)
        self.create_OWL_data_property_instance(instance, "hasLength", variableLength)
        startsAt = ctx.start.line
        self.create_OWL_data_property_instance(instance, "startsAt", startsAt)
        
        # Add "hasDatatype" and "isDatatypeOf" edges.
        datatype_ctx = ctx.typeType()
        dt_name = datatype_ctx.getText()
        if datatype_ctx.primitiveType():
            datatype_instance = self.get_instance_from_code_identifier(dt_name, class_name="Datatype")
        else:
            datatype_instance = self.get_instance_from_lsp_definition(datatype_ctx, dt_name, class_name="Datatype")
        if datatype_instance:
            self.create_OWL_object_property_instance(instance, datatype_instance, "hasDatatype")
            self.create_OWL_object_property_instance(datatype_instance, instance, "isDatatypeOf")

        self.modifiersForNextThingToBeEncountered = []

    def sharedConstructorAndMethodEnterConfig(self, ctx, block_context, instance):
        """ Create properties and edges that are common to all methods and constructors."""

        # Add "hasLength" and "startsAt" properties.
        constructorOrMethodText = ctx.getText()
        constructorOrMethodLength = len(constructorOrMethodText)
        self.create_OWL_data_property_instance(instance, "hasLength", constructorOrMethodLength)
        startsAt = ctx.start.line
        self.create_OWL_data_property_instance(instance, "startsAt", startsAt)
        current_complex_type_instance = self.getCurrentComplexTypeInstance()

        # Add "hasAccessModifier" edges
        for modifier in self.modifiersForNextThingToBeEncountered:
            if modifier in self.accessModifierInstances.keys():
                self.create_OWL_object_property_instance(instance, self.accessModifierInstances[modifier], "hasAccessModifier")

        def parseExpression(expression_context):
            """ Parse an expression and create the necessary edges."""

            # expression_context is of type ExpressionContext
            method_call_context = expression_context.methodCall()
            if method_call_context and method_call_context.identifier():
                # method_call_context is of type MethodCallContext
                invoked_method_name = method_call_context.identifier().getText()
                # Add "invokesMethod", "methodIsInvokedBy" edges.
                invoked_method_instance = self.get_instance_from_lsp_definition(method_call_context, invoked_method_name)
                if invoked_method_instance:
                    self.create_OWL_object_property_instance(instance, invoked_method_instance, "invokesMethod")
                    self.create_OWL_object_property_instance(invoked_method_instance, instance, "methodIsInvokedBy")
                    # Add "usesComplexType" edge.
                    used_complex_type = self.get_attribute_instance_from_instance(invoked_method_instance, "isDeclaredMethodOf")
                    if used_complex_type and current_complex_type_instance and (used_complex_type != current_complex_type_instance):
                        self.create_OWL_object_property_instance(current_complex_type_instance, used_complex_type, "usesComplexType")

            creator_context = expression_context.creator()
            if creator_context and creator_context.createdName():
                # creator_context is of type CreatorContext
                created_name_ctx = creator_context.createdName()
                created_instance_name = created_name_ctx.getText()
                # Only keep the name of the class if it is nested inside another class.
                if "." in created_instance_name:
                    first, created_instance_name = created_instance_name.rsplit(".", 1)
                    # Move the start column to the start of the class name such that the language server can find the class.
                    created_name_ctx.start.column += len(first)
                # Add "instantiatesClass", "isInstantiatedBy" edges.
                created_class_instance = self.get_instance_from_lsp_definition(created_name_ctx, created_instance_name, class_name="ClassType")
                if created_class_instance:
                    # Check if the instance is a class or a constructor.
                    used_complex_type = self.get_attribute_instance_from_instance(created_class_instance, "isDeclaredConstructorOf")
                    if used_complex_type:
                        created_class_instance = used_complex_type

                    self.create_OWL_object_property_instance(instance, created_class_instance, "instantiatesClass")
                    self.create_OWL_object_property_instance(created_class_instance, instance, "isInstantiatedBy")
                    # Add "usesComplexType" edge.
                    if (created_class_instance != current_complex_type_instance):
                        self.create_OWL_object_property_instance(current_complex_type_instance, created_class_instance, "usesComplexType")
                # "invokesConstructor" and "constructorIsInvokedBy" edges.
                id = self.create_deterministic_node_id_from_ctx(expression_context)
                if id in self.constructorDictionary:
                    constructor_instance = self.constructorDictionary[id]
                    self.create_OWL_object_property_instance(instance, constructor_instance, "invokesConstructor")
                    self.create_OWL_object_property_instance(constructor_instance, instance, "constructorIsInvokedBy")

        def parseStatements(statements):
            """ Parse statements and create the necessary edges."""

            for statement in statements:
                # Statement is of type BlockStatementContext  
                statement_context = statement.statement()
                if statement_context:
                    # statement_context is of type StatementContext
                    expression_contexts = statement_context.expression()
                    for expression_context in expression_contexts:
                        parseExpression(expression_context)
                    
                    # Add "catchesException" and "isCaughtBy" edges.
                    catchClauseContexts = statement_context.catchClause()
                    if catchClauseContexts:
                        for catchClauseContext in catchClauseContexts:
                            catch_type_ctx = catchClauseContext.catchType()
                            exception_name = catch_type_ctx.getText()
                            exception_instance = self.get_instance_from_lsp_definition(catch_type_ctx, exception_name, class_name="ExceptionType")
                            if exception_instance:
                                self.create_OWL_object_property_instance(instance, exception_instance, "catchesException")
                                self.create_OWL_object_property_instance(exception_instance, instance, "isCaughtBy")
                else:
                    # statement_context is of type LocalVariableDeclarationContext
                    local_variable_declaration_context = statement.localVariableDeclaration()
                    if local_variable_declaration_context:
                        expression_contexts = local_variable_declaration_context.expression()
                        # Check if there are any expressions in the local variable declaration.
                        if expression_contexts:
                            for expression_context in expression_contexts:
                                parseExpression(expression_context)
                        else:
                            variable_declarators = local_variable_declaration_context.variableDeclarators()
                            if variable_declarators:
                                variable_declarator_contexts = variable_declarators.variableDeclarator()
                                for variable_declarator_context in variable_declarator_contexts:
                                    initializer = variable_declarator_context.variableInitializer()
                                    if initializer:
                                        expression_context = initializer.expression()
                                        if expression_context:
                                            parseExpression(expression_context)
        
        # Parse all statements in this block.
        parseStatements(block_context.blockStatement())

        current_file_name = self.filename_from_ctx(ctx)
        # "accessesField" and "isAccessedBy" edges.
        for field_instance, referenced_locations in self.fieldsDictionary.items():
            # Check if the referenced location is in this expression context.
            for location in referenced_locations:
                if current_file_name == location[0]:
                    if ((location[1] > ctx.start.line and location[1] < ctx.stop.line) or
                        (location[1] == ctx.start.line and location[1] == ctx.stop.line and location[2] >= ctx.start.column and location[2] <= ctx.stop.column) or
                        (location[1] == ctx.start.line and location[1] < ctx.stop.line and location[2] >= ctx.start.column) or
                        (location[1] > ctx.start.line and location[1] == ctx.stop.line and location[2] <= ctx.stop.column)):
                        self.create_OWL_object_property_instance(instance, field_instance, "accessesField")
                        self.create_OWL_object_property_instance(field_instance, instance, "isAccessedBy")
                        # Add "usesComplexType" edge.
                        used_complex_type = self.get_attribute_instance_from_instance(field_instance, "isDeclaredFieldOf")
                        if used_complex_type and (current_complex_type_instance != used_complex_type):
                            self.create_OWL_object_property_instance(current_complex_type_instance, used_complex_type, "usesComplexType")
                        self.fieldsDictionary[field_instance].remove(location)
                        break

        # Empty modifiersForNextThingToBeEncountered
        self.modifiersForNextThingToBeEncountered = []

    def sharedComplexTypeEnterConfig(self, ctx, instance):
        """ Create properties and edges that are common to all complex types."""

        # Add 'isNestedComplexTypeIn' and 'hasNestedComplexTypeMember' edges.
        if len(self.complexTypeNestings) > 0:
            complex_type_instance = self.getCurrentComplexTypeInstance()
            if complex_type_instance:
                self.create_OWL_object_property_instance(instance, complex_type_instance, "isNestedComplexTypeIn")
                self.create_OWL_object_property_instance(complex_type_instance, instance, "hasNestedComplexTypeMember")

        self.setCurrentComplexTypeInstance(instance)

        # Add "hasAccessModifier" edges
        for modifier in self.getCurrentComplexTypeModifiers():
            if modifier in self.accessModifierInstances.keys():
                self.create_OWL_object_property_instance(instance, self.accessModifierInstances[modifier], "hasAccessModifier")

        # Add "hasNamespaceMember" and "isNamespaceMemberOf" edges.
        if self.currentPackageName:
            current_package = self.get_instance_from_code_identifier(self.currentPackageName, class_name = "JavaPackage")
            if current_package:
                self.create_OWL_object_property_instance(current_package, instance, "hasNamespaceMember")
                self.create_OWL_object_property_instance(instance, current_package, "isNamespaceMemberOf")

        # Add "hasLength" and "startsAt" properties.
        complexTypeText = ctx.getText()
        complexTypeLength = len(complexTypeText)
        self.create_OWL_data_property_instance(instance, "hasLength", complexTypeLength)
        startsAt = ctx.start.line
        self.create_OWL_data_property_instance(instance, "startsAt", startsAt)
        self.create_OWL_data_property_instance(instance, "isStaticComplexType", "static" in self.getCurrentComplexTypeModifiers())

        self.modifiersForNextThingToBeEncountered = []

    @requireComplexTypeNestings
    def sharedComplexTypeExitConfig(self):
        """ Remove the current complex type instance when exiting a complex type."""

        self.complexTypeNestings.pop()
        self.modifiersForNextThingToBeEncountered = []

