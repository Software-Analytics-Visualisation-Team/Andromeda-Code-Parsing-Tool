from typing import Union
from antlr4.tree.Tree import ParseTreeListener
from owl_constructor import OWLConstructor
from asbstract_syntax_tree import AST
from antlr4 import ParseTreeWalker

class TwoPhaseParseTreeWalker(ParseTreeWalker):
    """Custom ParseTreeWalker that walks the ParseTree in two phases:
    1. Initialization phase: Walks the ParseTree to create classes and data properties.
    2. Regular phase: Walks the ParseTree to create object properties.
    """

    def initializationWalk(self, listener: Union[ParseTreeListener, OWLConstructor], t: AST):
        """Walks the ParseTree in the initialization phase to create classes, data properties and simple object properties."""
        print("Parsing phase 1: Classes (Nodes) and data properties (Properties) and simple Object properties (Edges) for file", t.file_path)
        listener.initializationPhase = True
        listener.currentFilePath = t.file_path
        return super().walk(listener, t.tree)
    
    def regularWalk(self, listener: Union[ParseTreeListener, OWLConstructor], t: AST):
        """Walks the ParseTree in the regular phase to create complex object properties."""
        print("Parsing phase 2: complex Object properties (Edges) for file", t.file_path)
        listener.initializationPhase = False
        listener.currentFilePath = t.file_path
        return super().walk(listener, t.tree)
