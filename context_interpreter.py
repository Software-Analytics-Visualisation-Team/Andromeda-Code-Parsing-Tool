import hashlib
from urllib.parse import quote
import uuid
from antlr_generated_code.cpp.CPP14Parser import CPP14Parser


class ContextInterpreter():

    """ This class stores some helpers for interpreting ANTLR context objects."""

    def filename_from_ctx(self, ctx):
        """ Get the filename of the input stream that the context object is associated with."""

        return ctx.start.getInputStream().fileName

    def create_deterministic_node_id_from_filename_line_column(self, filename: str, line: int, column: int):
        """ Create a deterministic node ID from a filename, line number, and column number."""

        filename = quote(filename) # URL encode filename
        hasher = hashlib.sha256()
        hasher.update(filename.encode('utf-8'))
        hash_string = hasher.hexdigest()
        filename_number = int(hash_string, 16)
        return str(f"{line}_{column}_{filename_number}")

    def create_deterministic_node_id_from_ctx(self, ctx):
        """ Create a deterministic node ID from an ANTLR context object."""
        
        if not ctx:
            return str(uuid.uuid4()).replace("-", "_").upper()
        
        # Get the position where the identifier is defined.
        # e.g. ctx.start.column should be at the start of "display()", not at the start of "void display()".
        if hasattr(ctx, "identifier") and ctx.identifier():
            ctx = ctx.identifier()
            if isinstance(ctx, list):
                ctx = ctx[0]

        start_line = ctx.start.line
        start_column = ctx.start.column
        if hasattr(ctx, "enumkey"):
            key = ctx.enumkey().getText()
            start_column = start_column + len(key) + 1
            if key == "enumclass":
                start_column = start_column + 1
        elif isinstance(ctx, CPP14Parser.NamespaceDefinitionContext):
            start_column = start_column + len("namespace ")

        filename = self.filename_from_ctx(ctx)
        return self.create_deterministic_node_id_from_filename_line_column(filename, start_line, start_column)