from antlr_generated_code.java.JavaLexer import JavaLexer
from antlr_generated_code.java.JavaParser import JavaParser
from antlr_generated_code.cpp.CPP14Lexer import CPP14Lexer
from antlr_generated_code.cpp.CPP14Parser import CPP14Parser
from listeners.JavaListener import JavaListener
from listeners.CPPListener import CPPListener

class SupportedLanguage():
    """Class representing a supported language in the tool."""

    def __init__(self, name, file_extensions, parser, lexer, listener, unitMethodName):
        """Initializes a supported language object by setting its name, 
            file extensions, parser, lexer, listener, and unitMethodName.
        """
        
        self.name = name
        self.file_extensions = file_extensions
        self.parser = parser
        self.lexer = lexer
        self.listener = listener
        self.unitMethodName = unitMethodName

    @staticmethod
    def fromFile(filename: str) -> 'SupportedLanguage':
        """Returns the supported language object for the given filename.
           Raises an exception if no supported language exists for the given file.
        """
        for language in supported_languages:
            if filename.split(".")[-1] in language.file_extensions:
                return language
        raise Exception("No supported language found for the given file(s): " + filename)
    
    @staticmethod
    def fromName(name: str) -> 'SupportedLanguage':
        """Returns the supported language object for the given name.
           Raises an exception if no supported language exists with the given name.
        """
        for language in supported_languages:
            if name.lower() == language.name.lower():
                return language
        raise Exception("No supported language found for the given name: " + name)

# List of supported languages
supported_languages = [
    SupportedLanguage("Java", ["java"], JavaParser, JavaLexer, JavaListener, "compilationUnit"),
    SupportedLanguage("Cpp", ["cpp", "h", "hpp"], CPP14Parser, CPP14Lexer, CPPListener, "translationUnit"),
    # TODO: Add more supported languages
]

