import re
from pathlib import Path, PurePosixPath
from urllib.parse import urlparse, unquote


class LanguageServerCommunicator:

    """ Communicates with a language server to request references and definitions of symbols in a source code file."""

    def __init__(self, lsp):
        """ Initialize the LanguageServerCommunicator with a LanguageServerProtocol object."""
        
        self.lsp = lsp

    def _construct_language_server_input(self, ctx):
        """ Construct the input to the language server from an ANTLR context object."""

        line = ctx.start.line - 1
        column = ctx.start.column
        file_name = self.filename_from_ctx(ctx)[len(self.lsp.repository_root_path)+1:]
        return file_name, line, column

    def _process_language_server_output(self, result):
        """ Process the output from the language server to extract the line, column, and file name of the definition or reference."""

        def_line = result["range"]["start"]["line"] + 1
        def_column = result["range"]["start"]["character"]
        def_file_name = result["uri"]
        return def_line, def_column, def_file_name
    
    def _process_language_server_outputs(self, results):
        """ Process multiple outputs from the language server to extract the line, column, and file name of the definitions or references."""

        if not results:
            return []
        return [self._process_language_server_output(result) for result in results]
        
    def _safe_request(self, fn, *args):
        try:
            return fn(*args)
        except BaseException as e:
            code = getattr(e, "code", None)
            text = f"{type(e).__name__}: {e!r} {e}"
            if code == -32603 or "-32603" in text or "Internal error" in text:
                return []
            raise
            
    def request_references_from_ctx(self, ctx):
        """ Request references of the symbol at the given context from the language server."""

        params = self._construct_language_server_input(ctx)
        result = self._safe_request(self.lsp.request_references, *params)
        return self._process_language_server_outputs(result)

    def request_definition_from_ctx(self, ctx):
        """ Request the definition of the symbol at the given context from the language server."""

        params = self._construct_language_server_input(ctx)
        result = self._safe_request(self.lsp.request_definition, *params)
        return self._process_language_server_outputs(result)

    def request_references_from_file_line_column(self, file_name, line, column):
        """ Request references of the symbol at the given file, line, and column from the language server."""

        result = self._safe_request(self.lsp.request_references, file_name, line, column)
        return self._process_language_server_outputs(result)

    def request_definition_from_file_line_column(self, file_name, line, column):
        """ Request the definition of the symbol at the given file, line, and column from the language server."""

        result = self._safe_request(self.lsp.request_definition, file_name, line, column)
        return self._process_language_server_outputs(result)