from antlr_generated_code.java.JavaParserListener import JavaParserListener
from listeners.base.JavaListenerBase import JavaListenerBase

class JavaListener(JavaParserListener, JavaListenerBase):
    
    """ This class is responsible for listening to the events triggered by ANTLR when parsing Java source code.

    Each method in this class is called when the corresponding event is triggered by ANTLR.
    The methods in this class are responsible for creating the nodes and edges in the OWL ontology.
    Some helper methods are defined in the JavaListenerBase class.

    """

    """ Enter methods (Listener overrides) """

    def enterCompilationUnit(self, ctx):
        """ Create a node of type "File". """

        self.create_node_for_current_file(ctx)

    def enterPackageDeclaration(self, ctx):
        """ Create a node of type "JavaPackage" for each package in the source code."""

        package_name = ctx.qualifiedName().getText()
        # Check if a node for the package with this name is already present. If not create one.
        instance = self.get_instance_from_code_identifier(package_name, class_name = "JavaPackage")
        if not instance:
            instance = self.create_OWL_class_instance(ctx, "JavaPackage", package_name)
            self.create_OWL_data_property_instance(instance, "hasCodeIdentifier", package_name)

        self.currentPackageName = package_name

    def enterEnumDeclaration(self, ctx):
        """ Create a node of type "EnumerationType" for each enum in the source code."""

        enum_name = ctx.identifier().getText()
        instance = self.create_OWL_class_instance(ctx, "EnumerationType", enum_name)
        self.create_OWL_data_property_instance(instance, "hasCodeIdentifier", enum_name)

        self.sharedComplexTypeEnterConfig(ctx, instance)

    def enterInterfaceDeclaration(self, ctx):
        """ Create a node of type "InterfaceType" for each interface in the source code."""

        interface_name = ctx.identifier().getText()
        # Create the node
        instance = self.create_OWL_class_instance(ctx, "InterfaceType", interface_name)
        self.create_OWL_data_property_instance(instance, "hasCodeIdentifier", interface_name)
        self.create_OWL_data_property_instance(instance, "isExternalImport", False)
        
        # Add "hasSubInterface" and "hasSuperInterface" edges.
        typeTypeContexts = ctx.typeList()
        for typeTypeContext in typeTypeContexts:
            if typeTypeContext:
                typeType = typeTypeContext.getText()
                to_instance = self.get_instance_from_lsp_definition(typeTypeContext, typeType, class_name="InterfaceType")
                if to_instance:
                    self.create_OWL_object_property_instance(instance, to_instance, "hasSuperInterface")
                    self.create_OWL_object_property_instance(to_instance, instance, "hasSubInterface")

        self.sharedComplexTypeEnterConfig(ctx, instance)
        modifiers = self.getCurrentComplexTypeModifiers()
        self.create_OWL_data_property_instance(instance, "isAbstract", modifiers != None and "abstract" in modifiers)

    def enterClassDeclaration(self, ctx):
        """ Create a node of type "ClassType" for each class in the source code."""

        code_class_name = ctx.identifier().getText()
        className = "ClassType"
        typeTypeContext = ctx.typeType()
        if typeTypeContext :
            typeType = typeTypeContext.getText()

            # Give this class type ExceptionType if it extends Exception
            if typeType == "Exception":
                className = "ExceptionType"

        instance = self.create_OWL_class_instance(ctx, className, code_class_name)
        self.create_OWL_data_property_instance(instance, "hasCodeIdentifier", code_class_name)
        self.create_OWL_data_property_instance(instance, "isExternalImport", False)

        # Add "hasSubClass", "hasSuperClass" edges.
        if typeTypeContext :
            typeType = typeTypeContext.getText()
            to_instance = self.get_instance_from_lsp_definition(typeTypeContext, typeType, class_name="ClassType")
            if to_instance:
                self.create_OWL_object_property_instance(instance, to_instance, "hasSuperClass")
                self.create_OWL_object_property_instance(to_instance, instance, "hasSubClass")

        # Add "implementsInterface" and "isImplementedBy" edges.
        typeListContexts = ctx.typeList()
        for typeListContext in typeListContexts:
            if typeListContext:
                typeType = typeListContext.getText()
                to_instance = self.get_instance_from_lsp_definition(typeListContext, typeType, class_name="InterfaceType")
                if to_instance:
                    self.create_OWL_object_property_instance(instance, to_instance, "implementsInterface")
                    self.create_OWL_object_property_instance(to_instance, instance, "isImplementedBy")

        # Perform the shared complex type enter configuration
        self.sharedComplexTypeEnterConfig(ctx, instance)
        modifiers = self.getCurrentComplexTypeModifiers()
        self.create_OWL_data_property_instance(instance, "isAbstract", modifiers != None and "abstract" in modifiers)

    def enterAnnotationTypeDeclaration(self, ctx):
        """ Create a node of type "AnnotationType" for each annotation type in the source code."""

        annotation_name = ctx.identifier().getText()
        instance = self.create_OWL_class_instance(ctx, "AnnotationType", annotation_name)
        self.create_OWL_data_property_instance(instance, "hasCodeIdentifier", annotation_name)

        # Perform the shared complex type enter configuration
        self.sharedComplexTypeEnterConfig(ctx, instance)
        modifiers = self.getCurrentComplexTypeModifiers()
        self.create_OWL_data_property_instance(instance, "isAbstract", modifiers != None and "abstract" in modifiers)

    def enterConstructorDeclaration(self, ctx):
        """ Create a node of type "Constructor" for each constructor in the source code."""

        constructor_name = ctx.identifier().getText()
        instance = self.create_OWL_class_instance(ctx, "Constructor", constructor_name)
        self.create_OWL_data_property_instance(instance, "hasCodeIdentifier", constructor_name)
        # Add "declaresConstructor", "isDeclaredConstructorOf" edges.
        current_complex_type_instance = self.getCurrentComplexTypeInstance()
        if current_complex_type_instance:
            self.create_OWL_object_property_instance(current_complex_type_instance, instance, "declaresConstructor")
            self.create_OWL_object_property_instance(instance, current_complex_type_instance, "isDeclaredConstructorOf")

        # Find the refferences of the constructor
        reffereced_instances = self.get_instances_where_field_method_constructor_instance_is_refferenced(ctx.identifier())
        if reffereced_instances:
            for reffereced_instance in reffereced_instances:
                self.constructorDictionary[reffereced_instance] = instance

        constructor_body_block_context = ctx.block()
        if constructor_body_block_context:
            self.sharedConstructorAndMethodEnterConfig(ctx, constructor_body_block_context, instance)
        
    def enterFieldDeclaration(self, ctx):
        """ Create a node of type "Field" for each field in the source code."""

        field_name_ctx = ctx.variableDeclarators().variableDeclarator(0).variableDeclaratorId()
        field_name = field_name_ctx.getText()
        instance = self.create_OWL_class_instance(ctx, "Field", field_name)
        self.create_OWL_data_property_instance(instance, "hasCodeIdentifier", field_name)
        
        # Add "hasAccessModifier" edges
        for modifier in self.modifiersForNextThingToBeEncountered:
            if modifier in self.accessModifierInstances.keys():
                self.create_OWL_object_property_instance(instance, self.accessModifierInstances[modifier], "hasAccessModifier")

        # Add "declaresField", "isDeclaredFieldOf" edges.
        current_complex_type_instance = self.getCurrentComplexTypeInstance()
        if current_complex_type_instance:
            self.create_OWL_object_property_instance(current_complex_type_instance, instance, "declaresField")
            self.create_OWL_object_property_instance(instance, current_complex_type_instance, "isDeclaredFieldOf")

        # Find the refferences of the field.
        field_name_ctx.start.column += 1
        reffereced_locations = self.get_locations_where_field_method_constructor_instance_is_referenced(field_name_ctx)
        if reffereced_locations:
            for reffereced_location in reffereced_locations:
                if not instance in self.fieldsDictionary:
                    self.fieldsDictionary[instance] = []
                self.fieldsDictionary[instance].append(reffereced_location)

        self.sharedVariableEnterConfig(ctx, instance)

    def enterLocalVariableDeclaration(self, ctx):
        """ Create a node of type "Variable" for each variable in the source code."""

        variable_name = ctx.variableDeclarators().variableDeclarator(0).variableDeclaratorId().getText()
        instance = self.create_OWL_class_instance(ctx, "Variable", variable_name)
        self.create_OWL_data_property_instance(instance, "hasCodeIdentifier", variable_name)

        self.sharedVariableEnterConfig(ctx, instance)

    def enterMethodDeclaration(self, ctx):
        """ Create a node of type "Method" for each method in the source code."""

        method_name = ctx.identifier().getText()
        instance = self.create_OWL_class_instance(ctx, "Method", method_name)
        self.setCurrentMethodInstance(instance)
        self.create_OWL_data_property_instance(instance, "hasCodeIdentifier", method_name)
        # Add "declaresMethod", "isDeclaredMethodOf" edges.
        current_complex_type_instance = self.getCurrentComplexTypeInstance()
        if current_complex_type_instance:
            self.create_OWL_object_property_instance(current_complex_type_instance, instance, "declaresMethod")
            self.create_OWL_object_property_instance(instance, current_complex_type_instance, "isDeclaredMethodOf")
        # Add "hasReturnType", "isReturnTypeOf" edges.
        return_type_name = ctx.typeTypeOrVoid().getText()
        if return_type_name != "void":
            datatype_ctx = ctx.typeTypeOrVoid().typeType()
            datatype_name = datatype_ctx.getText()
            if datatype_ctx.primitiveType():
                return_type_instance = self.get_instance_from_code_identifier(datatype_name, class_name="Datatype")
            else:
                return_type_instance = self.get_instance_from_lsp_definition(datatype_ctx, datatype_name, class_name="Datatype")

            if return_type_instance:
                self.create_OWL_object_property_instance(instance, return_type_instance, "hasReturnType")
                self.create_OWL_object_property_instance(return_type_instance, instance, "isReturnTypeOf")

        # Add "throwsException" and "isThrownBy" edges.
        throwsContexts = ctx.qualifiedNameList()
        if throwsContexts:
            for throwsContext in throwsContexts.qualifiedName():
                exception_name = throwsContext.getText()
                exception_instance = self.get_instance_from_lsp_definition(throwsContext, exception_name, class_name="ExceptionType")
                if exception_instance:
                    self.create_OWL_object_property_instance(instance, exception_instance, "throwsException")
                    self.create_OWL_object_property_instance(exception_instance, instance, "isThrownBy")
        
        # Add "isStatic" property.
        if "static" in self.modifiersForNextThingToBeEncountered:
            self.create_OWL_data_property_instance(self.getCurrentMethodInstance(), "isStatic", True)

        # Perform shared method enter configuration
        method_body_block_context = ctx.methodBody().block()
        if method_body_block_context:
            self.sharedConstructorAndMethodEnterConfig(ctx, method_body_block_context, instance)

    def enterFormalParameter(self, ctx):
        """ Create a node of type "Parameter" for each parameter in the source code."""

        parameter_name = ctx.variableDeclaratorId().getText()
        instance = self.create_OWL_class_instance(ctx, "Parameter", parameter_name)
        self.create_OWL_data_property_instance(instance, "hasCodeIdentifier", parameter_name)
        
        # Getting the index of the parameter in the method eg. 0 for the first parameter, 1 for the second parameter and so on
        parameter_position = ctx.parentCtx.formalParameter().index(ctx)
        self.create_OWL_data_property_instance(instance, "hasPosition", parameter_position)

        current_method_instance = self.getCurrentMethodInstance()
        # Create "hasParameter" edge from the current method to this parameter.
        if current_method_instance:
            self.create_OWL_object_property_instance(current_method_instance, instance, "hasParameter")
        
        # Create "isParameterOf" edge from this parameter to the current method.
        if current_method_instance:
            self.create_OWL_object_property_instance(instance, current_method_instance, "isParameterOf")
        
        # Create "expectsDatatype" and "isExpectedDatatype" edges.
        if current_method_instance:
            datatype_ctx = ctx.typeType()
            datatype_name = datatype_ctx.getText()
            if datatype_ctx.primitiveType():
                datatype_instance = self.get_instance_from_code_identifier(datatype_name, class_name="Datatype")
            else:
                datatype_instance = self.get_instance_from_lsp_definition(datatype_ctx, datatype_name, class_name="Datatype")

            if datatype_instance:
                self.create_OWL_object_property_instance(current_method_instance, datatype_instance, "expectsDatatype")
                self.create_OWL_object_property_instance(datatype_instance, current_method_instance, "isExpectedDatatype")
        
        self.modifiersForNextThingToBeEncountered = []
        self.sharedVariableEnterConfig(ctx, instance)

    def enterCatchClause(self, ctx):
        """ Adds "isCaughtBy" and "catchesException" edges. """

        # Get the name of the exception being caught
        catch_type_ctx = ctx.catchType()
        exception_name = catch_type_ctx.getText()
        
        # Get the current method or constructor instance
        current_method_or_constructor = self.getCurrentMethodInstance()
        instance = self.get_instance_from_lsp_definition(catch_type_ctx, exception_name, class_name="ExceptionType")
        if instance and current_method_or_constructor:
            # Create the 'isCaughtBy' property
            self.create_OWL_object_property_instance(instance, current_method_or_constructor, "isCaughtBy")
            # Create the 'catchesException' property
            self.create_OWL_object_property_instance(current_method_or_constructor, instance, "catchesException")

    def enterClassOrInterfaceModifier(self, ctx):
        """ Contrary to its name, this method is called for every modifier, not just class or interface modifiers."""

        self.modifiersForNextThingToBeEncountered.append(ctx.getText())

    """ Exit methods (Listener overrides) """

    def exitCompilationUnit(self, _):
        """ Reset the currentPackageName variable."""
        self.currentPackageName = None

    def exitEnumDeclaration(self, _):
        """ Reset the modifiersForNextThingToBeEncountered variable."""

        self.sharedComplexTypeExitConfig()
    
    def exitInterfaceDeclaration(self, _):
        """ Reset the modifiersForNextThingToBeEncountered variable."""

        self.sharedComplexTypeExitConfig()

    def exitClassDeclaration(self, _):
        """ Reset the modifiersForNextThingToBeEncountered variable."""

        self.sharedComplexTypeExitConfig()

    def exitAnnotationTypeDeclaration(self, _):
        """ Reset the modifiersForNextThingToBeEncountered variable."""

        self.sharedComplexTypeExitConfig()

    def exitMethodDeclaration(self, _):
        """ Reset the modifiersForNextThingToBeEncountered variable."""

        self.setCurrentMethodInstance(None)
        self.modifiersForNextThingToBeEncountered = []

    def exitConstructorDeclaration(self, _):
        """ Reset the modifiersForNextThingToBeEncountered variable."""

        self.modifiersForNextThingToBeEncountered = []
