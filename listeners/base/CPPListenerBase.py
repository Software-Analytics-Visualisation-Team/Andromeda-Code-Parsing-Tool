from owl_constructor import OWLConstructor

class CPPListenerBase(OWLConstructor):

    """ Base class for C++ listeners. 
    
    Contains shared functionality. 
    
    """

    accessModifierInstances, constructorDictionary = {}, {}

    def __init__(self, lsp):
        super().__init__(lsp)

        # Set up language specific stuff.
        primitiveTypes = ["int", "short", "long", "long long", "unsigned int", "unsigned short", "unsigned long",
                          "unsigned long long", "char", "wchar_t", "char16_t", "char32_t", "float", "double",
                          "long double", "bool", "void"]

        for primitive in primitiveTypes:
            # replacing every space with an underscore so it can be serialized
            primitive = primitive.replace(" ", "_")
            instance = self.create_OWL_class_instance(None, "PrimitiveType", primitive)
            self.create_OWL_data_property_instance(instance, "hasCodeIdentifier", primitive)

        # Define a node for each access modifier:
        for access_modifier in ["private", "protected", "public"]:
            instance = self.create_OWL_class_instance(None, "AccessModifier", access_modifier)
            self.create_OWL_data_property_instance(instance, "hasCodeIdentifier", access_modifier)
            self.accessModifierInstances[access_modifier] = instance

    """ Things related to keeping track of current complex type and namespaces instance """

    class ComplexTypeState():
        """ Class that represents the state of a complex type. """

        def __init__(self, instance, isAbstract):
            """ Constructor for ComplexTypeState. """

            self.instance = instance
            self.isAbstract = isAbstract

    class NamespaceState():
        """ Class that represents the state of a namespace. """

        def __init__(self, instance):
            """ Constructor for NamespaceState. """

            self.instance = instance

    class MethodState():
        """ Class that represents the state of a method. """

        def __init__(self, instance):
            """ Constructor for MethodState. """

            self.instance = instance

    # List of ComplexTypeState and namespace to keep track of nested type declarations.
    complexTypeNestings = []
    namespaceNestings = []
    methodNestings = []
    modifierNestings = ["public"]

    def getCurrentComplexTypeInstance(self):
        """ Get the current complex type instance. """

        if len(self.complexTypeNestings) > 0:
            return self.complexTypeNestings[-1].instance
        return None

    def getCurrentComplexTypeAbstract(self):
        """ Get the current complex type abstract property. """

        if len(self.complexTypeNestings) > 0:
            return self.complexTypeNestings[-1].isAbstract
        return None

    def getCurrentNamespaceInstance(self):
        """ Get the current namespace instance. """

        if len(self.namespaceNestings) > 0:
            return self.namespaceNestings[-1].instance
        return None

    def getCurrentModifierInstance(self):
        """ Get the current modifier instance. """	

        if len(self.modifierNestings) > 0:
            return self.modifierNestings[-1]
        return None

    def getCurrentMethodInstance(self):
        """ Get the current method instance."""

        if len(self.methodNestings) > 0:
            return self.methodNestings[-1].instance
        return None

    def setCurrentComplexTypeAbstract(self, abstract):
        """ Set the current complex type abstract property."""

        if len(self.complexTypeNestings) > 0:
            self.complexTypeNestings[-1].isAbstract = abstract
    
    def setCurrentComplexTypeInstance(self, instance):
        """ Set the current complex type instance."""

        self.complexTypeNestings.append(self.ComplexTypeState(instance, False))

    def setCurrentNamespaceInstance(self, instance):
        """ Set the current namespace instance.	"""

        self.namespaceNestings.append(self.NamespaceState(instance))

    def setCurrentModifierInstance(self, modifier):
        """ Set the current modifier instance."""

        self.modifierNestings.append(modifier)

    def setCurrentMethodInstance(self, instance):
        """ Set the current method instance."""

        self.methodNestings.append(self.MethodState(instance))
        
    """ Methods for shared functionality """

    def sharedClassEnumEnterConfig(self, node_class, node_name, ctx, instance):
        """ A method used to check possible definitions of classes and enums """

        # Add 'isNamespaceMemeberOf' and 'hasNamespaceMember' edge to the needed namespaces.
        if len(self.namespaceNestings) > 0 and len(self.complexTypeNestings) == 0:
            namespace_instance = self.getCurrentNamespaceInstance()
            self.create_OWL_object_property_instance(instance, namespace_instance, "isNamespaceMemberOf")
            self.create_OWL_object_property_instance(namespace_instance, instance, "hasNamespaceMember")
        # Add 'isNestedComplexTypeIn' and 'hasNestedComplexTypeMember' edge to the needed classes.
        elif len(self.complexTypeNestings) > 0:
            class_instance = self.getCurrentComplexTypeInstance()
            self.create_OWL_object_property_instance(instance, class_instance, "isNestedComplexTypeIn")
            self.create_OWL_object_property_instance(class_instance, instance, "hasNestedComplexTypeMember")

        # Add 'hasAccesModifier' edge
        modifier = self.getCurrentModifierInstance()
        if modifier is None:
            modifier = get_instance_from_code_identifier("public", class_name = "AccessModifier")
        self.create_OWL_object_property_instance(instance, self.accessModifierInstances[modifier], "hasAccessModifier")
        
        length = len(ctx.parentCtx.getText())
        self.create_OWL_data_property_instance(instance, "hasLength", length)

        start = ctx.start.line
        self.create_OWL_data_property_instance(instance, "startsAt", start)

        # Set the current class
        self.setCurrentComplexTypeInstance(instance)

    def sharedFieldParameterVariableEnterConfig(self, declarator_specifier, instance, ctx):
        """ A method used to check possible definitions of variables, fields and parameters 
        isConstant property with hasLenght and startsAt
        """

        self.create_OWL_data_property_instance(instance, "isConstant", "const" in declarator_specifier)

        length = len(ctx.getText())
        self.create_OWL_data_property_instance(instance, "hasLength", length)

        start = ctx.start.line
        self.create_OWL_data_property_instance(instance, "startsAt", start)

    def sharedConstructorAndMethodEnterConfig(self, ctx, instance):
        """ A method used to check possible definitions of methods and constructors """

        length = len(ctx.getText())
        self.create_OWL_data_property_instance(instance, "hasLength", length)

        start = ctx.start.line
        self.create_OWL_data_property_instance(instance, "startsAt", start)
