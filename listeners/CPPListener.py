from antlr_generated_code.cpp.CPP14ParserListener import CPP14ParserListener
from listeners.base.CPPListenerBase import CPPListenerBase

class CPPListener(CPP14ParserListener, CPPListenerBase):
   
    """ This class is responsible for listening to the events triggered by ANTLR when parsing C++ source code.

    Each method in this class is called when the corresponding event is triggered by ANTLR.
    The methods in this class are responsible for creating the nodes and edges in the OWL ontology.
    Some helper methods are defined in the CPPListenerBase class.

    """

    """ Enter methods (Listener overrides) """

    def enterTranslationUnit(self, ctx):
        """ Create a node of type "File" for the current file. """

        self.create_node_for_current_file(ctx)
        self.modifierNestings = ["public"]
        # Only .cpp files can implement interfaces
        if ".cpp_" in self.currentFileInstance:
            for line in range (0, ctx.start.line + 1):
                refferenced_files = self.get_instances_where_file_is_defined(line, 0, self.filename_from_ctx(ctx), self.currentFileInstance)
                for refferenced_file in refferenced_files:
                    # only .h/hpp files can be interfaces
                    if ".h_" in refferenced_file or ".hpp_" in refferenced_file:
                        # Add 'implementsInterface' and 'isImplementedBy' edge to the needed files.
                        self.create_OWL_object_property_instance(self.currentFileInstance, refferenced_file, "implementsInterface")
                        self.create_OWL_object_property_instance(refferenced_file, self.currentFileInstance, "isImplementedBy")

    def enterNamespaceDefinition(self, ctx):
        """ Create a node of type "Namespace" for each namespace in the source code. """

        # 1) Figure out the name (handles anonymous or inline namespaces)
        ident = ctx.Identifier()
        if ident:
            namespace_name = ident.getText()
        else:
            # First time we see an anonymous namespace, initialize the counter
            if not hasattr(self, "_anon_ns_counter"):
                self._anon_ns_counter = 0

            namespace_name = f"_anonymous_{self._anon_ns_counter}"
            self._anon_ns_counter += 1

        # 2) Create the OWL instance & add the identifier property
        instance = self.create_OWL_class_instance(ctx, "Namespace", namespace_name)
        if not instance:
            return

        self.create_OWL_data_property_instance(instance,
                                            "hasCodeIdentifier",
                                            namespace_name)

        # 3) If we’re already inside another namespace, link them
        if self.namespaceNestings:
            parent_ns = self.getCurrentNamespaceInstance()
            self.create_OWL_object_property_instance(instance,
                                                    parent_ns,
                                                    "isNestedNamespaceIn")
            self.create_OWL_object_property_instance(parent_ns,
                                                    instance,
                                                    "hasNestedNamespaceMember")

        # 4) Update our “current namespace” stack & default modifier
        self.setCurrentNamespaceInstance(instance)
        self.setCurrentModifierInstance("public")

    def enterEnumSpecifier(self, ctx):
        """ Create a node of type "EnumerationType" for each enum in the source code."""
        head = ctx.enumHead()
        ident = head.Identifier()      # may be None for anonymous enums
        if ident is None:
            return                   # or assign a synthetic name if you prefer
        enum_name = ident.getText()
        # enum_name = ctx.enumHead().Identifier().getText()
        instance = self.create_OWL_class_instance(ctx.enumHead(), "EnumerationType", enum_name)
        if instance:
            self.create_OWL_data_property_instance(instance, "hasCodeIdentifier", enum_name)
            
            self.sharedClassEnumEnterConfig("EnumerationType", enum_name, ctx.enumHead(), instance)
            # Set the default access modifier of the nodes inside the enum
            self.setCurrentModifierInstance("public")
            # Set the isAbstract property
            self.create_OWL_data_property_instance(instance, "isAbstract", False)

    def enterClassSpecifier(self, ctx):
        """ Create a node of type "ClassType" for each class in the source code."""

        classType = "ClassType"
        superclass = None
        superclassContext = None
        instance_exc = None
        instance = None
        class_name = ctx.classHead().classHeadName()

        if class_name:
            class_name = class_name.getText()

            # Check if the class is an exception type
            if hasattr(ctx.classHead(), 'baseClause'):
                superclassContext = ctx.classHead().baseClause()
                if superclassContext:
                    superclassContext = superclassContext.baseSpecifierList().baseSpecifier()[0].baseTypeSpecifier()
                    superclass = superclassContext.getText()
                    if superclass  == "std::exception":
                        classType = "ExceptionType"
                    else:
                        # Use language server to get the instance of the superclass
                        instance_exc = self.get_instance_from_lsp_definition(superclassContext, superclass, override_first_tree_walk=True)
                        if instance_exc:
                            instace_resource = self.get_resource_from_instance(instance_exc, override_first_tree_walk=True)
                            if instace_resource and "ExceptionType" in instace_resource:
                                classType = "ExceptionType"
        
            instance = self.create_OWL_class_instance(ctx.classHead().classHeadName(), classType, class_name)
        if instance:
            self.create_OWL_data_property_instance(instance, "hasCodeIdentifier", class_name)

            self.sharedClassEnumEnterConfig(classType, class_name, ctx.classHead(), instance)
            # Add 'hasSubClass' and 'hasSuperClass' edge to the needed classes.
            if instance_exc:
                self.create_OWL_object_property_instance(instance, instance_exc, "hasSuperClass")
                self.create_OWL_object_property_instance(instance_exc, instance, "hasSubClass")
            # Set the default access modifier of the nodes inside the class
            self.setCurrentModifierInstance("private")

    def enterFunctionDefinition(self, ctx):
        """ Create a node of type "Method" for each method/constructor in the source code. """

        instance = None

        # ----- Common helper to find the last real typeSpecifier() -----
        def _extract_return_type_spec(ctx):
            seq = ctx.declSpecifierSeq().declSpecifier()
            # walk from right to left until we find one with a typeSpecifier()
            for spec in reversed(seq):
                ts = spec.typeSpecifier()
                if ts:
                    # drill down to the trailing/simple specifier
                    tts = ts.trailingTypeSpecifier()
                    if tts:
                        return tts.simpleTypeSpecifier()
            return None

        # ----- Method (has a declSpecifierSeq) -----
        if ctx.declSpecifierSeq():
            # extract the method name
            method_ctx = ctx.declarator()
            if method_ctx:
                method_ctx = method_ctx.pointerDeclarator() if hasattr(method_ctx, "pointerDeclarator") and callable(method_ctx.pointerDeclarator) else None
            if method_ctx:
                method_ctx = method_ctx.noPointerDeclarator() if hasattr(method_ctx, "noPointerDeclarator") and callable(method_ctx.noPointerDeclarator) else None
            if method_ctx:
                method_ctx = method_ctx.noPointerDeclarator() if hasattr(method_ctx, "noPointerDeclarator") and callable(method_ctx.noPointerDeclarator) else None
            if not method_ctx:
                return
            method_name = method_ctx.getText()
            instance = self.create_OWL_class_instance(method_ctx, "Method", method_name)
            if not instance:
                return

            # method_ctx = (ctx.declarator()
            #                 .pointerDeclarator()
            #                 .noPointerDeclarator()
            #                 .noPointerDeclarator())
            # if not method_ctx:
            #     return

            method_name = method_ctx.getText()
            instance = self.create_OWL_class_instance(method_ctx, "Method", method_name)
            if not instance:
                return

            # identifier
            self.create_OWL_data_property_instance(instance, "hasCodeIdentifier", method_name)

            # abstract/static flags
            specs = ctx.declSpecifierSeq().getText().split()
            self.create_OWL_data_property_instance(instance, "isAbstract", "virtual" in specs)
            if "virtual" in specs:
                self.setCurrentComplexTypeAbstract(True)

            self.create_OWL_data_property_instance(instance, "isStatic", "static" in specs)

            # link to its enclosing class/struct
            class_inst = self.getCurrentComplexTypeInstance()
            if class_inst:
                self.create_OWL_object_property_instance(instance, class_inst, "isDeclaredMethodOf")
                self.create_OWL_object_property_instance(class_inst, instance, "declaresMethod")

            # return‐type (skip constructors, pure‐virtuals, etc.)
            ret_spec = _extract_return_type_spec(ctx)
            if ret_spec and ret_spec.getText() != "void":
                # primitive vs. complex
                if ret_spec.theTypeName() is None:
                    # primitive
                    rt = ret_spec.getText()
                    rt_inst = self.get_instance_from_code_identifier(rt, class_name="Datatype")
                else:
                    # user‐defined type
                    className = ret_spec.theTypeName().className()
                    rt_inst = self.get_instance_from_lsp_definition(className, className.getText())

                if rt_inst:
                    self.create_OWL_object_property_instance(instance, rt_inst, "hasReturnType")
                    self.create_OWL_object_property_instance(rt_inst, instance, "isReturnTypeOf")

        # ----- Constructor (no declSpecifierSeq) -----
        else:
            ctor_ctx = (ctx.declarator()
                        .pointerDeclarator()
                        .noPointerDeclarator()
                        .noPointerDeclarator())
            if not ctor_ctx:
                return

            ctor_name = ctor_ctx.getText()
            instance = self.create_OWL_class_instance(ctor_ctx, "Constructor", ctor_name)
            if instance:
                self.create_OWL_data_property_instance(instance, "hasCodeIdentifier", ctor_name)

                class_inst = self.getCurrentComplexTypeInstance()
                if class_inst:
                    self.create_OWL_object_property_instance(instance, class_inst, "isDeclaredConstructorOf")
                    self.create_OWL_object_property_instance(class_inst, instance, "declaresConstructor")

                # track constructor→method references
                refs = self.get_instances_where_field_method_constructor_instance_is_refferenced(ctor_ctx)
                for r in refs or ():
                    self.constructorDictionary[r] = instance

        # ----- common post‐processing -----
        if instance:
            self.setCurrentMethodInstance(instance)
            self.sharedConstructorAndMethodEnterConfig(ctx, instance)
            self.setCurrentModifierInstance("private")

    def enterMemberDeclarator(self, ctx):
        """ Create a node of type "Field" for each field in the source code.
            Create a node of type "Method" for each pure virtual method in the source code.
            This function can find fields and pure virtual methods.
        """

        # The pure virtual method is counted, so we have to exclude it
        instance = None
        declarator_ctx = ctx.parentCtx.parentCtx.declSpecifierSeq()
        if declarator_ctx:
            declarator_specifier = declarator_ctx.getText()
            if "virtual" not in declarator_specifier and ")" not in ctx.declarator().getText():
                field_name = ctx.declarator().getText()
                instance = self.create_OWL_class_instance(ctx.declarator(), "Field", field_name)
                if instance:
                    self.create_OWL_data_property_instance(instance, "hasCodeIdentifier", field_name)
                    
                    # Add "isDeclaredFieldOf" and inverse "declaresField" edges
                    class_instance = self.getCurrentComplexTypeInstance()
                    if class_instance:
                        self.create_OWL_object_property_instance(instance, class_instance, "isDeclaredFieldOf")
                        self.create_OWL_object_property_instance(class_instance, instance, "declaresField")

                    self.sharedFieldParameterVariableEnterConfig(declarator_ctx.getText(), instance, ctx.parentCtx.parentCtx)
            else: #pure virtual method
                method_ctx = ctx.declarator().pointerDeclarator().noPointerDeclarator().noPointerDeclarator()
                if method_ctx:
                    method_name = method_ctx.getText()
                    instance = self.create_OWL_class_instance(method_ctx, "Method", method_name)
                    self.create_OWL_data_property_instance(instance, "hasCodeIdentifier", method_name)

                    # Add "IsDeclaredMethodOf" and inverse "DeclaresMethod" edges
                    class_instance = self.getCurrentComplexTypeInstance()
                    if class_instance:
                        self.create_OWL_object_property_instance(instance, class_instance, "isDeclaredMethodOf")
                        self.create_OWL_object_property_instance(class_instance, instance, "declaresMethod")

                    self.create_OWL_data_property_instance(instance, "isAbstract", True)
                    self.setCurrentComplexTypeAbstract(True)
                    self.sharedConstructorAndMethodEnterConfig(ctx.parentCtx.parentCtx, instance)
        else: #pure virtual constructor in case of .h files
            c_name = ctx.declarator().pointerDeclarator().noPointerDeclarator().noPointerDeclarator().getText()
            instance = self.create_OWL_class_instance(ctx.declarator().pointerDeclarator().noPointerDeclarator().noPointerDeclarator(), "Constructor", c_name)
            if instance:
                self.create_OWL_data_property_instance(instance, "hasCodeIdentifier", c_name)
                # Add "isDeclaredConstructorOf" and "declaresConstructor" edges
                class_instance = self.getCurrentComplexTypeInstance()
                if class_instance:
                    self.create_OWL_object_property_instance(instance, class_instance, "isDeclaredConstructorOf")
                    self.create_OWL_object_property_instance(class_instance, instance, "declaresConstructor")
        # Add "hasAccessModifier" edge
        if instance: 
            modifier = self.getCurrentModifierInstance()
            if modifier is None:
                modifier = self.get_instance_from_code_identifier("public", class_name = "AccessModifier")
            self.create_OWL_object_property_instance(instance, self.accessModifierInstances[modifier], "hasAccessModifier")

    def enterParameterDeclaration(self, ctx):
        """ Create a node of type "Parameter" for each parameter in the source code."""

        if not ctx.declSpecifierSeq() or not ctx.declSpecifierSeq().declSpecifier():
            return

        parameter_ctx = ctx.declarator()
        if parameter_ctx:
            parameter_name = parameter_ctx.getText()
            instance = self.create_OWL_class_instance(ctx.declarator(), "Parameter", parameter_name)
            if instance:
                self.create_OWL_data_property_instance(instance, "hasCodeIdentifier", parameter_name)
                position = None
                parent_list = getattr(ctx.parentCtx, "parameterDeclaration", None)
                if parent_list and callable(parent_list):
                    param_list = parent_list()
                    if isinstance(param_list, list):
                        try:
                            position = param_list.index(ctx)
                        except ValueError:
                            position = None
                if position is None:
                    # If the position is not found, we can use the index of the parameter in the parent context
                    position = 0
                # Adds "hasPosition" data property to the parameter
                # position = ctx.parentCtx.parameterDeclaration().index(ctx)
                self.create_OWL_data_property_instance(instance, "hasPosition", position)
                self.sharedFieldParameterVariableEnterConfig(ctx.declSpecifierSeq().getText(), instance, ctx)

                # Add "hasParameter" and "isParameterOf" edge from the parent method to the parameter
                method_instance = self.getCurrentMethodInstance()
                if method_instance:
                    self.create_OWL_object_property_instance(method_instance, instance, "hasParameter")
                    self.create_OWL_object_property_instance(instance, method_instance, "isParameterOf")
                    
                    # Add "expectsDatatype" and "isExpectedDatatype" edge from the parent method to the paramet
                    type_ctx = ctx.declSpecifierSeq().declSpecifier()[-1].typeSpecifier().trailingTypeSpecifier()
                    if type_ctx:
                        type_ctx = type_ctx.simpleTypeSpecifier()
                    if type_ctx:
                        if type_ctx.theTypeName() is None: #primitiveType
                            parameter_datatype = type_ctx.getText()
                            parameter_datatype_instance = self.get_instance_from_code_identifier(parameter_datatype, class_name="Datatype")
                            if parameter_datatype_instance:
                                self.create_OWL_object_property_instance(method_instance, parameter_datatype_instance, "expectsDatatype")
                                self.create_OWL_object_property_instance(parameter_datatype_instance, method_instance, "isExpectedDatatype")
                        else: #ComplexType
                            type_ctx = type_ctx.theTypeName().className()
                            parameter_datatype_instance = self.get_instance_from_lsp_definition(type_ctx, type_ctx.getText())
                            if parameter_datatype_instance:
                                self.create_OWL_object_property_instance(method_instance, parameter_datatype_instance, "expectsDatatype")
                                self.create_OWL_object_property_instance(parameter_datatype_instance, method_instance, "isExpectedDatatype")

    def enterInitDeclarator(self, ctx):
        """ Create a node of type "Variable" for each variable in the source code."""

        if not ctx.parentCtx.parentCtx.declSpecifierSeq() or not ctx.parentCtx.parentCtx.declSpecifierSeq().declSpecifier():
            return

        declarator_specifier = ctx.parentCtx.parentCtx.declSpecifierSeq()
        if declarator_specifier is not None:
            variable_name = ctx.declarator().getText()
            instance = self.create_OWL_class_instance(ctx.declarator(), "Variable", variable_name)
            if instance:
                self.create_OWL_data_property_instance(instance, "hasCodeIdentifier", variable_name)

                # Add isStaticVariable property
                self.sharedFieldParameterVariableEnterConfig(declarator_specifier.getText(), instance, ctx)
                self.create_OWL_data_property_instance(instance, "isStaticVariable", "static" in declarator_specifier.getText())

                # — safe extraction of the final simpleTypeSpecifier —
                type_ctx = None
                seq = ctx.parentCtx.parentCtx.declSpecifierSeq().declSpecifier()
                for spec in reversed(seq):
                    ts = spec.typeSpecifier()
                    if not ts:
                        continue
                    tail = ts.trailingTypeSpecifier()
                    if not tail:
                        continue
                    simple = tail.simpleTypeSpecifier()
                    if simple:
                        type_ctx = simple
                        break

                # Add the "hasDatatype" and "isDatatypeOf" edges for the variable
                if type_ctx:
                    if type_ctx.theTypeName() is None:  # primitiveType
                        datatype = type_ctx.getText()
                        datatype_instance = self.get_instance_from_code_identifier(datatype, class_name="Datatype")
                        if datatype_instance:
                            self.create_OWL_object_property_instance(instance, datatype_instance, "hasDatatype")
                            self.create_OWL_object_property_instance(datatype_instance, instance, "isDatatypeOf")
                    else:  # ComplexType
                        cname_ctx = type_ctx.theTypeName().className()
                        if cname_ctx:
                            datatype_instance = self.get_instance_from_lsp_definition(cname_ctx, cname_ctx.getText())
                            if datatype_instance:
                                self.create_OWL_object_property_instance(instance, datatype_instance, "hasDatatype")
                                self.create_OWL_object_property_instance(datatype_instance, instance, "isDatatypeOf")

    def enterAccessSpecifier(self, ctx):
        """ Keep track of the access modifiers """

        if len(self.modifierNestings) > 0:
            self.modifierNestings.pop()
        self.setCurrentModifierInstance(ctx.getText())

    def enterTryBlock(self, ctx):
        """ Add "catchesException" and "isCaughtBy" edges. """

        exc_ctx = None
        handler_seq = ctx.handlerSeq() if hasattr(ctx, "handlerSeq") else None
        if handler_seq and hasattr(handler_seq, "handler"):
            handlers = handler_seq.handler()
            if handlers and len(handlers) > 0:
                last_handler = handlers[-1]
                exc_decl = last_handler.exceptionDeclaration() if hasattr(last_handler, "exceptionDeclaration") else None
                if exc_decl and hasattr(exc_decl, "typeSpecifierSeq"):
                    type_spec_seq = exc_decl.typeSpecifierSeq()
                    if type_spec_seq and hasattr(type_spec_seq, "typeSpecifier"):
                        type_specifiers = type_spec_seq.typeSpecifier()
                        if type_specifiers and len(type_specifiers) > 0:
                            exc_ctx = type_specifiers[-1]
        if exc_ctx:
            exc_name = exc_ctx.getText()
            # Use language server to get the instance of the exception
            exc_instance = self.get_instance_from_lsp_definition(exc_ctx, exc_name)
            if exc_instance:
                method_instance = self.getCurrentMethodInstance()
                # Check if method_instance is not None
                if method_instance:
                    self.create_OWL_object_property_instance(method_instance, exc_instance, "catchesException") 
                    self.create_OWL_object_property_instance(exc_instance, method_instance, "isCaughtBy")
        
    def enterThrowExpression(self, ctx):
        """ Add "throwsException" and "isThrownBy" edges. """

        exc_ctx = (ctx.assignmentExpression().conditionalExpression().logicalOrExpression()
            .logicalAndExpression()[-1].inclusiveOrExpression()[-1].exclusiveOrExpression()[-1]
            .andExpression()[-1].equalityExpression()[-1].relationalExpression()[-1].shiftExpression()[-1]
            .additiveExpression()[-1].multiplicativeExpression()[-1].pointerMemberExpression()[-1]
            .castExpression()[-1].unaryExpression()
        )
        exc_instance = None
        exc_name = None
        if hasattr(exc_ctx, "newExpression_") and exc_ctx.newExpression_():
            ne = exc_ctx.newExpression_()
            if hasattr(ne, "newTypeId") and ne.newTypeId():
                exc_ctx = ne.newTypeId().typeSpecifierSeq().typeSpecifier()[-1]
                exc_name = exc_ctx.getText()
                exc_instance = self.get_instance_from_lsp_definition(exc_ctx, exc_name)
        if hasattr(exc_ctx, "postfixExpression") and exc_ctx.postfixExpression():
            pe = exc_ctx.postfixExpression()
            if hasattr(pe, "postfixExpression") and pe.postfixExpression():
                pe2 = pe.postfixExpression()
                if hasattr(pe2, "postfixExpression") and pe2.postfixExpression():
                    exc_ctx = pe2.postfixExpression()
        if exc_instance:
            if len(self.methodNestings) > 0:
                method_instance = self.getCurrentMethodInstance()
                self.create_OWL_object_property_instance(method_instance, exc_instance, "throwsException")
                self.create_OWL_object_property_instance(exc_instance, method_instance, "isThrownBy")
            
    def enterPostfixExpression(self, ctx):
        """ Add the "accessesField" and "isAccessedBy" edges for each field access in the source code 
            Add the "invokesMethod" and "methodIsInvokedBy" edges for each method access in the source code
            Add the "usesComplexType" edge for each complex type access in another complex type in the source code
        """
        
        if ctx.postfixExpression():
            accessed_name = ctx.idExpression()
            if accessed_name:
                accessed_name = accessed_name.getText()
                refferenced_instance = self.get_instance_from_lsp_definition(ctx.idExpression(), accessed_name)
                if refferenced_instance:
                    reffered_node_type = self.get_resource_from_instance(refferenced_instance)
                    if reffered_node_type:
                        method_instance = self.getCurrentMethodInstance()
                        if method_instance:
                            if "Method" in reffered_node_type: #method
                                self.create_OWL_object_property_instance(method_instance, refferenced_instance, "invokesMethod")
                                self.create_OWL_object_property_instance(refferenced_instance, method_instance, "methodIsInvokedBy")
                            if "Field" in reffered_node_type: #field
                                self.create_OWL_object_property_instance(method_instance, refferenced_instance, "accessesField")
                                self.create_OWL_object_property_instance(refferenced_instance, method_instance, "isAccessedBy")
                        complexType_instance = self.getCurrentComplexTypeInstance() 
                        if complexType_instance: # connects to the property of the object, needs to connect to object
                            complexType_owner = self.get_attribute_instance_from_instance(refferenced_instance, "isDeclaredFieldOf")
                            if not complexType_owner:
                                complexType_owner = self.get_attribute_instance_from_instance(refferenced_instance, "isDeclaredMethodOf")
                            if complexType_owner:
                                self.create_OWL_object_property_instance(complexType_instance, complexType_owner, "usesComplexType")
                
    def enterNewExpression_(self, ctx): 
        """ Add "instantiatesClass" and "isInstantiatedBy" edges for each object instantiation in the source code
            Add "invokesConstructor" and "constructorIsInvokedBy" edges for each object instantiation in the source code
        """

        # ────────────────────────────────────────────────────────────────
        # 1.  Drill down cautiously until we find a className() context
        # ────────────────────────────────────────────────────────────────
        nti  = ctx.newTypeId()
        if not nti:
            return                                    # e.g.  “new (buf) T”

        tseq = nti.typeSpecifierSeq()
        if not tseq or not tseq.typeSpecifier():
            return

        target_cls_ctx = None
        for ts in tseq.typeSpecifier():               # walk left → right
            tail = ts.trailingTypeSpecifier()
            if not tail:
                continue
            simp = tail.simpleTypeSpecifier()
            if not simp:
                continue
            tname = simp.theTypeName()
            if not tname:
                continue
            cname = tname.className()
            if cname:
                target_cls_ctx = cname                # found it!
                break

        if target_cls_ctx is None:                    #   built‑ins: new int
            return

        class_name = target_cls_ctx.getText()

        # ────────────────────────────────────────────────────────────────
        # 2.  Ordinary “instantiatesClass / isInstantiatedBy” link
        # ────────────────────────────────────────────────────────────────
        referenced_instance = self.get_instance_from_lsp_definition(
            target_cls_ctx, class_name
        )
        if referenced_instance:
            node_type = self.get_resource_from_instance(referenced_instance)
            if node_type and "ClassType" in node_type:
                method_inst = self.getCurrentMethodInstance()
                if method_inst:
                    self.create_OWL_object_property_instance(
                        method_inst, referenced_instance, "instantiatesClass"
                    )
                    self.create_OWL_object_property_instance(
                        referenced_instance, method_inst, "isInstantiatedBy"
                    )

        # ────────────────────────────────────────────────────────────────
        # 3.  Constructor call mapping  (optional)
        # ────────────────────────────────────────────────────────────────
        first_ts = tseq.typeSpecifier()[0]            # safe: we know the list exists
        ctor_id  = self.create_deterministic_node_id_from_ctx(first_ts)
        if ctor_id in self.constructorDictionary:
            ctor_inst   = self.constructorDictionary[ctor_id]
            method_inst = self.getCurrentMethodInstance()
            if method_inst:
                self.create_OWL_object_property_instance(
                    method_inst, ctor_inst, "invokesConstructor"
                )
                self.create_OWL_object_property_instance(
                    ctor_inst, method_inst, "constructorIsInvokedBy"
                )

    """ Exit methods (Listener overrides) """

    def exitNamespaceDefinition(self, ctx):
        """ Remove the current nestings when exiting a namespace. """

        if len(self.namespaceNestings) > 0:
            self.namespaceNestings.pop()
        if len(self.modifierNestings) > 0:
            self.modifierNestings.pop()

    def exitEnumSpecifier(self, ctx):
        """ Remove the current nestings when exiting an enum """

        if len(self.modifierNestings) > 0:
            self.modifierNestings.pop()
        if len(self.complexTypeNestings) > 0:
            self.complexTypeNestings.pop()
    
    def exitClassSpecifier(self, ctx):
        """ Remove the current nestings when exiting a class.
            Set isAbstract property of the class."""

        class_ctx = ctx.classHead().classHeadName()
        if class_ctx:
            class_name = class_ctx.getText()
            id = self.create_deterministic_node_id_from_ctx(class_ctx)
            instance = self.get_instance_from_id(class_name, id)
            isAbstract = self.getCurrentComplexTypeAbstract()
            if len(self.complexTypeNestings) > 0:
                self.complexTypeNestings.pop()
            if len(self.modifierNestings) > 0:
                self.modifierNestings.pop()
            if isAbstract:
                if len(self.complexTypeNestings) > 0:
                    self.setCurrentComplexTypeAbstract(True)
            
            self.create_OWL_data_property_instance(instance, "isAbstract", isAbstract)

    def exitFunctionDefinition(self, ctx):
        """ Remove the current nestings when exiting a function. """

        if len(self.modifierNestings) > 0:
            self.modifierNestings.pop()
        if len(self.methodNestings) > 0:
            self.methodNestings.pop()