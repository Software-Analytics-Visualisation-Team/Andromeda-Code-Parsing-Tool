from antlr4.tree.Tree import ParseTree

class AST():
    """Container for ParseTree and file path of the file from which the ParseTree was generated."""

    tree = None
    file_path = None
    
    def __init__(self, file_path: str, tree: ParseTree) -> 'AST':
        """ Initialize the AST object with the file path and ParseTree."""

        self.file_path = file_path
        self.tree = tree