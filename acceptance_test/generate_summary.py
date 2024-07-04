import sys
from rdflib import Graph

import urllib.parse


# Helper functions
def namespace_to_name(uri):
    """Extracts the name of the namespace from the given URI."""
    return urllib.parse.unquote(str((uri.split("#")[-1]).split("_")[0]))


def namespace_to_id(uri):
    """Extracts the ID of the namespace from the given URI."""
    return str((uri.split("#")[-1]).split("_", 1)[-1])

def create_query_to_get_nodes_of_type(node_type: str):
    """Creates a SPARQL query to get all the nodes of the given type."""

    # The query
    return f"""
        SELECT ?hasCodeIdentifier ?hasIdentifier
        WHERE {{
            ?resource rdf:type <{node_type}> .
            ?resource SEON_code:hasCodeIdentifier ?hasCodeIdentifier .   
            ?resource SEON_code:hasIdentifier ?hasIdentifier .
        }}
    """

# Node creation functions
def create_primitive_nodes(g: Graph):
    """Creates nodes for all the PrimitiveType instances in the graph."""

    primitive_nodes_query = """
        SELECT DISTINCT ?hasCodeIdentifier ?hasIdentifier
        WHERE {
            ?resource rdf:type <http://se-on.org/ontologies/domain-specific/2012/02/code.owl#PrimitiveType> .
            ?resource SEON_code:hasIdentifier ?hasIdentifier .
            ?resource SEON_code:hasCodeIdentifier ?hasCodeIdentifier .
            {?resource SEON_code:isReturnTypeOf ?something} UNION {?resource SEON_code:isDatatypeOf ?something} UNION {?resource SEON_code:isExpectedDatatype ?something}.
        }
    """
    primitive_nodes_query_result = g.query(primitive_nodes_query)

    # Print the result
    print("#" * 50 + "\n" + "PrimitiveType:" + "\n" + "#" * 50)
    for row in primitive_nodes_query_result:
        print(row[0])
    print("\n")
    

# Find all the Namespaces and Packages 
def create_container_instances(g: Graph):
    """Creates nodes for all the JavaPackages and Namespaces in the graph."""


    query1 = create_query_to_get_nodes_of_type("http://se-on.org/ontologies/system-specific/2012/02/java.owl#JavaPackage")
    query2 = create_query_to_get_nodes_of_type("http://se-on.org/ontologies/domain-specific/2012/02/code.owl#Namespace")
    container_instances_query1_result = g.query(query1)
    container_instances_query2_result = g.query(query2)
    # Print the result
    print("#" * 50 + "\n" + "JavaPackages and Namespaces:" + "\n" + "#" * 50)
    for row in container_instances_query1_result:
        print(row[0])
    for row in container_instances_query2_result:
        print(row[0])
    print("\n")

def create_class_nodes(g: Graph):
    """Creates nodes for all the ClassType instances in the graph."""

    query = create_query_to_get_nodes_of_type("http://se-on.org/ontologies/domain-specific/2012/02/code.owl#ClassType")
    class_nodes_query_result = g.query(query)
    # Print the result
    print("#" * 50 + "\n" + "ClassType:" + "\n" + "#" * 50)
    for row in class_nodes_query_result:
        print(row[1])
    print("\n")

def create_annotation_nodes(g: Graph):
    """Creates nodes for all the AnnotationType instances in the graph."""

    annotation_nodes_query = create_query_to_get_nodes_of_type("http://se-on.org/ontologies/domain-specific/2012/02/code.owl#AnnotationType")
    annotation_nodes_query_result = g.query(annotation_nodes_query)
    # Print the result
    print("#" * 50 + "\n" + "AnnotationType:" + "\n" + "#" * 50)
    for row in annotation_nodes_query_result:
        print(row[1])
    print("\n")


def create_enumeration_nodes(g: Graph):
    """Creates nodes for all the EnumerationType instances in the graph."""

    enumeration_nodes_query = create_query_to_get_nodes_of_type("http://se-on.org/ontologies/domain-specific/2012/02/code.owl#EnumerationType")
    enumeration_nodes_query_result = g.query(enumeration_nodes_query)
    # Print the result
    print("#" * 50 + "\n" + "EnumerationType:" + "\n" + "#" * 50)
    for row in enumeration_nodes_query_result:
        print(row[1])
    print("\n")

def create_interface_nodes(g: Graph):
    """Creates nodes for all the InterfaceType instances in the graph."""

    interface_nodes_query = create_query_to_get_nodes_of_type("http://se-on.org/ontologies/domain-specific/2012/02/code.owl#InterfaceType")
    interface_nodes_query_result = g.query(interface_nodes_query)
    # Print the result
    print("#" * 50 + "\n" + "InterfaceType:" + "\n" + "#" * 50)
    for row in interface_nodes_query_result:
        print(row[1])
    print("\n")


def create_exception_nodes(g: Graph):
    """Creates nodes for all the ExceptionType instances in the graph."""

    exception_nodes_query = create_query_to_get_nodes_of_type("http://se-on.org/ontologies/domain-specific/2012/02/code.owl#ExceptionType")
    exception_nodes_query_result = g.query(exception_nodes_query)
    # Print the result
    print("#" * 50 + "\n" + "ExceptionType:" + "\n" + "#" * 50)
    for row in exception_nodes_query_result:
        print(row[1])
    print("\n")

def create_method_nodes(g: Graph):
    """Creates nodes for all the Method instances in the graph."""

    method_nodes_query = create_query_to_get_nodes_of_type("http://se-on.org/ontologies/domain-specific/2012/02/code.owl#Method")
    method_nodes_query_result = g.query(method_nodes_query)
    # Print the result
    print("#" * 50 + "\n" + "Method:" + "\n" + "#" * 50)
    for row in method_nodes_query_result:
        print(row[1])
    print("\n")

def create_constructor_nodes(g: Graph):
    """Creates nodes for all the Constructor instances in the graph."""

    constructor_nodes_query = create_query_to_get_nodes_of_type("http://se-on.org/ontologies/domain-specific/2012/02/code.owl#Constructor")
    constructor_nodes_query_result = g.query(constructor_nodes_query)
    # Print the result
    print("#" * 50 + "\n" + "Constructor:" + "\n" + "#" * 50)
    for row in constructor_nodes_query_result:
        print(row[1])
    print("\n")

def create_variable_nodes(g: Graph):
    """Creates nodes for all the Variable instances in the graph. """

    variable_nodes_query = create_query_to_get_nodes_of_type("http://se-on.org/ontologies/domain-specific/2012/02/code.owl#Variable")
    variable_nodes_query_result = g.query(variable_nodes_query)
    # Print the result
    print("#" * 50 + "\n" + "Variable:" + "\n" + "#" * 50)
    for row in variable_nodes_query_result:
        print(row[1])
    print("\n")

def create_parameter_nodes(g: Graph):
    """ Creates nodes for all the Parameter instances in the graph. """

    parameter_nodes_query =create_query_to_get_nodes_of_type("http://se-on.org/ontologies/domain-specific/2012/02/code.owl#Parameter")
    parameter_nodes_query_result = g.query(parameter_nodes_query)
    # Print the result
    print("#" * 50 + "\n" + "Parameter:" + "\n" + "#" * 50)
    for row in parameter_nodes_query_result:
        print(row[1])
    print("\n")

def create_field_nodes(g: Graph):
    """ Creates nodes for all the Field instances in the graph. """

    field_nodes_query = create_query_to_get_nodes_of_type("http://se-on.org/ontologies/domain-specific/2012/02/code.owl#Field")
    field_nodes_query_result = g.query(field_nodes_query)
    # Print the result
    print("#" * 50 + "\n" + "Field:" + "\n" + "#" * 50)
    for row in field_nodes_query_result:
        print(row[1])
    print("\n")


def create_relationships(g: Graph, relationship_type: str):
    """Creates relationships of the given type in the graph."""

    relationships_query = f"""
        SELECT ?method ?relationship
        WHERE {{
            ?method SEON_code:{relationship_type} ?relationship .
        }}
    """
    relationships_query_result = g.query(relationships_query)
    # Print the result
    print("#" * 50)
    print(relationship_type + " Relationship:")
    print("#" * 50)
    for row in relationships_query_result:
        print(row[0], " ", relationship_type, " ", row[1])
        print("\n")

    print("\n")
    

def __main__():

    # Get the input and output file paths from the command line arguments.
    input_file_path, output_file_path = sys.argv[1], sys.argv[2]

    # Parse the input file as a graph.
    g = Graph().parse(input_file_path, format='xml')

    relationship_types = [
            "accessesField", "catchesException", "constructorIsInvokedBy", "containsCodeEntity",
            "declaresConstructor", "declaresField", "declaresMethod", "expectsDatatype",
            "hasAccessModifier", "hasDatatype", "hasNamespaceMember", "hasParameter",
            "hasReturnType", "hasSubClass", "hasSubInterface", "hasSuperClass",
            "hasSuperInterface", "implementsInterface", "instantiatesClass", "invokesConstructor",
            "invokesMethod", "isAccessedBy", "isCaughtBy", "isDatatypeOf", "isDeclaredConstructorOf",
            "isDeclaredFieldOf", "isDeclaredMethodOf", "isExpectedDatatype", "isImplementedBy",
            "isInstantiatedBy", "isNamespaceMemberOf", "isParameterOf", "isReturnTypeOf",
            "isThrownBy", "methodIsInvokedBy", "throwsException", "usesComplexType"
        ]
    datatype_properties = [
        "hasCodeIdentifier","hasIdentifier","hasLength","hasPosition",
        "isAbstract","isConstant","isStatic","startsAt"
    ]
    # Output the constructed json to a file.
    with open(output_file_path, "w") as f:
        # Query for all nodes already defined
        sys.stdout = f  # Redirect stdout to the output file
        create_primitive_nodes(g)
        create_annotation_nodes(g)
        create_container_instances(g)
        create_class_nodes(g)
        create_enumeration_nodes(g)
        create_interface_nodes(g)
        create_exception_nodes(g)
        create_method_nodes(g)
        create_constructor_nodes(g)
        create_variable_nodes(g)
        create_parameter_nodes(g)
        create_field_nodes(g)

        for relationship_type in relationship_types:
            create_relationships(g, relationship_type)
        
        for datatype_property in datatype_properties:
            create_relationships(g, datatype_property)
        sys.stdout = sys.__stdout__  # Restore stdout


if __name__ == "__main__":
    __main__()