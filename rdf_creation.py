from asbstract_syntax_tree import AST
from two_phase_parse_tree_walker import TwoPhaseParseTreeWalker
from supported_language import SupportedLanguage
from monitors4codegen.multilspy import SyncLanguageServer
from monitors4codegen.multilspy.multilspy_config import MultilspyConfig
from monitors4codegen.multilspy.multilspy_logger import MultilspyLogger
from rdflib import Graph
from antlr4 import FileStream, CommonTokenStream

def asts_to_rdf(asts: list[AST], language: SupportedLanguage, root_path: str) -> Graph:    
    """Generates RDF from the provided ASTs in the provided language.

    Args:
        asts (list[AST]): List of ASTs to generate RDF from.
        language (SupportedLanguage): Language in which the the files from which the ASTs were generated were written.
        root_path (str): Root path of the files.

    Returns:
        Graph: RDF generated from the provided ASTs.
    """

    print("Initializing language server for " + language.name)
    lsp = SyncLanguageServer.create(MultilspyConfig.from_dict({"code_language": language.name.lower()}), MultilspyLogger(), root_path)
    lsp.repository_root_path = root_path
    with lsp.start_server():
        print(f"Language server for language {language.name} started")
        listener = language.listener(lsp)
        walker = TwoPhaseParseTreeWalker()

        for ast in asts:
            walker.initializationWalk(listener, ast)
        for ast in asts:
            walker.regularWalk(listener, ast)

        return listener.get_graph()


def get_rdf(root_path: str, files: list[str], language: SupportedLanguage) -> Graph:
    """Returns RDF generated from the provided [files] in [language].

    Args:
        files (list[str]): Paths of files to generate RDF from.
        language (SupportedLanguage): Language in which files were written.

    Returns:
        Graph: generated rdf representation of the provided files.
    """
    asts = [create_ast(file, language) for file in files] # Generate ASTs
    asts = [ast for ast in asts if ast is not None] # Remove None ASTs
    rdf = asts_to_rdf(asts, language, root_path)
    
    return rdf

def create_ast(file_path: str, language: SupportedLanguage) -> AST:
    """Parses the file at file_path in language as an AST.

    Args:
        file_path (str): Path provided for the file to be parsed.
        language (SupportedLanguage): Language in which the provided file was written.

    Returns:
        AST of the provided file.
    """
    try:
        input_stream = FileStream(file_path, encoding='utf-8')
        lexer = language.lexer(input_stream)
        stream = CommonTokenStream(lexer)
        parser = language.parser(stream)
        tree = getattr(parser, language.unitMethodName)()
        return AST(file_path, tree)
    except UnicodeDecodeError:
        return None
