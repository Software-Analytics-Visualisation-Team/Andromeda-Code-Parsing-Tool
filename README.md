# Code-to-SPIF-Tool
## Setup (after a new galaxy install)
1. Open the command line
2. Navigate to the galaxy directory
3. Create a `galaxy/tools/moonshot/` directory:
   ```bash
   mkdir tools/moonshot
   ```
4. Clone this repository:
   ```bash
   git clone https://github.com/Moonshot-SEP/Code-to-SPIF-Tool.git tools/moonshot/Code-to-SPIF-Tool
   ```
5. Change the galaxy tool-configuration at `config/tool_conf.xml.sample` by adding:
  ```xml
  <section name="Moonshot" id="moonshot">
    <tool file="moonshot/Code-to-SPIF-Tool/zip_to_spif.xml" />
  </section>
  ```
   before
   ```xml
  <!--
  <section id="interactivetools" name="Interactive tools">
    <tool file="interactive/interactivetool_askomics.xml" />
    <tool file="interactive/interactivetool_bam_iobio.xml" />
    <tool file="interactive/interactivetool_cellxgene_0.16.2.xml" />
    <tool file="interactive/interactivetool_cellxgene_1.1.1.xml" />
    <tool file="interactive/interactivetool_ethercalc.xml" />
    <tool file="interactive/interactivetool_guacamole_desktop.xml" />
    <tool file="interactive/interactivetool_hicbrowser.xml" />
    <tool file="interactive/interactivetool_jupyter_notebook_1.0.0.xml" />
    <tool file="interactive/interactivetool_jupyter_notebook.xml" />
    <tool file="interactive/interactivetool_neo4j.xml" />
    <tool file="interactive/interactivetool_openrefine.xml" />
    <tool file="interactive/interactivetool_phinch.xml" />
    <tool file="interactive/interactivetool_rstudio.xml" />
  </section>
  -->
   ```
## How to use the tool
1. Open the command line
2. Navigate to the galaxy directory
3. Run galaxy:
   ```bash
   sh run.sh
   ```
4. Open [galaxy]([https://duckduckgo.com](http://127.0.0.1:8080/) "Your galaxy instance") in your browser
4. Navigate to the Convert code to SPIF tool under the Moonshot header in the Tools column.
5. Upload a zip file:
   - Click on the "..."-button (Browse or Upload Datasets)
   - Click on the "Upload"-button
   - Click on the "Choose local file"-button
   - Select the zip file you want to convert
   - Click on the "Start"-button
   - Wait until the file-row becomes green
   - Click on the "Cancel"-button
6. Select the zip file:
   - Click on the "..."-button (Browse or Upload Datasets)
   - Click on the zip file that you just uploaded
   - Click on the "Ok"-button
7. Pick a language:
   - Click on the dropdown menu (Java by default)
   - Click on the language you want the tool to convert files of from the zip file
8. Click on "Run Tool"-button

## How to run unit tests
Run the command: 
```
python -m unittest discover -s tests
```
Add `-v` flag at the end for more detailed testing <br/>
Depending on how your python environment is set up the command can also be:
```
python3 -m unittest discover -s tests
```

## Java implementation progress:

Note: Strikethrough means that they don't have to be implemented directly as they just serve as parrent classes for other classes that must be implemented or are already all defined in java.owl.

### Classes (Nodes):
- ~~[ ] Thing~~
- ~~[ ] AccessModifier~~ (Defined in java.owl)
- [x] AnnotationType
- ~~[ ] Artifact~~
- [x] ClassType
- ~~[ ] CodeEntity~~
- ~~[ ] ComplexType~~
- [x] Constructor
- ~~[ ] Datatype~~
- [x] EnumerationType
- [x] ExceptionType
- [x] Field
- [x] File
- [x] InterfaceType
- [x] Method
- ~~[ ] Namespace~~ (It has JavaPackage which extends NameSpace)
- ~~[ ] Nothing~~
- [x] Parameter
- [x] PrimitiveTypes
- ~~[ ] SeonThing~~
- [x] Variable
- [x] JavaPackage


## Object properties (Edges):
- [x] accessesField
- [x] catchesException
- [x] constructorIsInvokedBy
- [x] containsCodeEntity
- [x] declaresConstructor
- [x] declaresField
- [x] declaresMethod
- ~~[ ] dependsOn~~
- [x] expectsDatatype
- [x] hasAccessModifier
- ~~[ ] hasChild~~
- [x] hasDatatype 
- [x] hasNamespaceMember
- [x] hasParameter
- ~~[ ] hasParent~~
- [x] hasReturnType
- [x] hasSubClass
- [x] hasSubInterface
- ~~[ ] hasSubtype~~
- [x] hasSuperClass
- [x] hasSuperInterface
- ~~[ ] hasSuperType~~
- [x] implementsInterface
- [x] instantiatesClass
- [x] invokesConstructor
- [x] invokesMethod
- [x] isAccessedBy
- [x] isCaughtBy
- [x] isDatatypeOf
- [x] isDeclaredConstructorOf
- [x] isDeclaredFieldOf
- [x] isDeclaredMethodOf
- [x] isExpectedDatatype
- [x] isImplementedBy
- [x] isInstantiatedBy
- [x] isNamespaceMemberOf
- [x] isParameterOf
- [x] isReturnTypeOf
- [x] isThrownBy
- [x] methodIsInvokedBy
- [x] throwsException
- [x] usesComplexType


### Data properties (Properties):
- [x] hasCodeIdentifier
- [ ] hasDoc
- [x] hasIdentifier
- [x] hasLength
- [x] hasPosition
- [x] isAbstract
- [x] isConstant
- [x] isStatic 
- [x] startsAt
- [ ] hasJavaDoc


# Custom properties added (not from SEON)
- isStaticComplexType (on ComplexType)
- isExternalImport (on ComplexType, on ExceptionType and on Datatype)

# Custom edges added (not from SEON)
- isNestedNamespaceIn (namespeace -> namespace)
- hasNestedNamespaceMember (namespeace -> namespace)
- isNestedComplexTypeIn (complexType -> complexType)
- hasNestedComplexTypeMember (complexType -> complexType)

## C++ Implementation progress:

### Classes (Nodes):
- ~~[ ] Thing~~
- ~~[ ] AccessModifier~~
- ~~[] AnnotationType~~
- ~~[ ] Artifact~~
- [x] ClassType
- ~~[ ] CodeEntity~~
- ~~[ ] ComplexType~~
- [x] Constructor
- ~~[ ] Datatype~~
- [x] EnumerationType
- [x] ExceptionType
- [x] Field
- [x] File
- [x] InterfaceType
- [x] Method
- [x] Namespace
- ~~[ ] Nothing~~
- [x] Parameter
- [x] PrimitiveTypes
- ~~[ ] SeonThing~~
- [x] Variable
- ~~[ ] JavaPackage~~


## Object properties (Edges):
- [x] accessesField (Language Server)
- [x] catchesException (Language Server)
- [x] constructorIsInvokedBy (Language Server)
- [x] containsCodeEntity
- [x] declaresConstructor
- [x] declaresField
- [x] declaresMethod
- ~~[ ] dependsOn~~
- [x] expectsDatatype (partially Language Server)
- [x] hasAccessModifier 
- ~~[ ] hasChild~~
- [x] hasDatatype (partially Language Server)
- [x] hasNamespaceMember (does not take into consideration nested complexTypes and nested namespaceTypes, for this separate edges were added)
- [x] hasParameter
- ~~[ ] hasParent~~
- [x] hasReturnType (partially Language Server)
- [x] hasSubClass (Language Server)
- ~~[ ] hasSubInterface~~ (not applicable to CPP)
- ~~[ ] hasSubtype~~
- [x] hasSuperClass (Language Server)
- ~~[ ] hasSuperInterface~~ (not applicable to CPP)
- ~~[ ] hasSuperType~~
- [ ] implementsInterface (Language Server, header files are considered to be interfaces)
- [x] instantiatesClass (Language Server)
- [x] invokesConstructor (Language Server)
- [x] invokesMethod (Language Server)
- [x] isAccessedBy (Language Server)
- [x] isCaughtBy (Language Server)
- [x] isDatatypeOf (partially Language Server)
- [x] isDeclaredConstructorOf
- [x] isDeclaredFieldOf
- [x] isDeclaredMethodOf
- [x] isExpectedDatatype (partially Language Server)
- [ ] isImplementedBy  (Language Server, header files are considered to be interfaces)
- [x] isInstantiatedBy (Language Server)
- [x] isNamespaceMemberOf (does not take into consideration nested complexTypes and nested namespaceTypes, for this separate edges were added)
- [x] isParameterOf
- [x] isReturnTypeOf (partially Language Server)
- [x] isThrownBy (Language Server)
- [x] methodIsInvokedBy (Language Server)
- [x] throwsException (Language Server)
- [x] usesComplexType


### Data properties (Properties):
- [x] hasCodeIdentifier
- ~~[ ]~~ hasDoc (ANTRL does not check comments)
- ~~[ ] hasIdentifier~~ (Do not need as it serves as a superclass for hasCodeIdentifier and every node has the property hasCodeIdentifier)
- [x] hasLength
- [x] hasPosition
- [x] isAbstract
- [x] isConstant
- [x] isStatic 
- [x] startsAt
- ~~[ ]~~ hasJavaDoc (this is CPP)

# Custom edges added (not from SEON)
- isNestedNamespaceIn (namespeace -> namespace)
- hasNestedNamespaceMember (namespeace -> namespace)
- isNestedComplexTypeIn (complexType -> complexType)
- hasNestedComplexTypeMember (complexType -> complexType)

# Custom properties added (not from SEON)
- isStaticVariable (on Variable)

# Design choices and assumptions:

In cpp, in order to to implement data from cpp file A.cpp into B.cpp, you have to create the A.h file, and include it into B.cpp to use the functionality of the "interface" of A.h implemented in A.cpp. Thus, edges like "invokesMethod", "invokesConstrucot", "accessesField", etc. that start in B.cpp can only reffer to nodes from the A.h file, due to lsp limitations. 
To fix this, we have added the implementsInterface edge and pair from the node of the A.cpp file to the node fo the A.h file and vice versa to add a sensible connection from the specification of nodes to their implementation.
Also, due to lsp and antlr limitations, there is no context for #include clauses to see what .cpp file implements what .h file, 
so we can check either only the first lines before a context is encountered, or check all the lines for #include statements using lsp, for which we have found no way of computing.
Thus, we assume the #inlcude statement is at the start of the file, before any contex of antlr can be found.
