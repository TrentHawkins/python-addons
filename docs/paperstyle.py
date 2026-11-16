import collections.abc
import re

import pygments.style
import pygments.token


bold      = " bold"
italic    = " italic"
underline = " underline"


macros = {
	"background": "#EEEEEE",
	"comments"  : "#999999",
	"functions" : "#550099",
	"keywords"  : "#000000",
	"numbers"   : "#559900",
	"strings"   : "#995500",
	"types"     : "#005599",
	"variables" : "#555555",
	"builtins"  : "#009955",
	"errors"    : "#990055",
}


class PaperStyle(pygments.style.Style):
	"""Python source-code highlighting with the reference dark palette."""

	background_color = macros["background"]

	# Empty styles inherit from their parent token.
	styles = {
		pygments.token.Token : "#000000", # Default text.
		pygments.token.Error : "#CCCCCC", # Unrecognized characters, e.g. $ outside a string.

		pygments.token.Text           : "", # Spaces and line-continuation backslashes.
		pygments.token.Text.Whitespace: "", # Newlines and separately classified whitespace.

		pygments.token.Keyword            : macros["keywords"] + bold, # if, else, return, def, class.
		pygments.token.Keyword.Constant   : macros["numbers"], # True, False, None.
		pygments.token.Keyword.Namespace  : macros["keywords"] + bold, # import and from in import statements.

		pygments.token.Name                  : macros["variables"], # value in value = 1; attr in obj.attr; ordinary call names.
		pygments.token.Name.Builtin          : macros["builtins"], # int, str, len, print.
		pygments.token.Name.Builtin.Pseudo   : macros["builtins"], # self, cls, Ellipsis, NotImplemented.
		pygments.token.Name.Class            : macros["types"], # Example in class Example:.
		pygments.token.Name.Decorator        : macros["variables"], # @classmethod, @property, @decorator.
		pygments.token.Name.Exception        : macros["errors"], # Built-in exception names, e.g. ValueError and TypeError.
		pygments.token.Name.Function         : macros["functions"], # combine in def combine(...):
		pygments.token.Name.Function.Magic   : macros["functions"], # __init__, __repr__, __add__.
		pygments.token.Name.Namespace        : macros["variables"], # math in import math; pathlib in from pathlib import Path.
		pygments.token.Name.Variable         : macros["variables"], # Parent category for special-variable names.
		pygments.token.Name.Variable.Magic   : macros["variables"], # __name__, __file__, __slots__.

		pygments.token.Literal     : macros["numbers"], # Parent category for strings and numbers.

		pygments.token.String          : macros["strings"], # Parent category for all string literal tokens.
		pygments.token.String.Affix    : macros["strings"] + bold, # String prefixes: f, r, b, t, fr, rb.
		pygments.token.String.Doc      : macros["comments"] + italic, # Docstrings, e.g. """Documentation.""".
		pygments.token.String.Double   : macros["strings"], # "hello" and ordinary double-triple-quoted strings.
		pygments.token.String.Escape   : macros["numbers"], # \n, \t, \u1234 escape sequences inside strings.
		pygments.token.String.Interpol : macros["keywords"], # { and !r} in f"{value!r}"; also %s and format placeholders.
		pygments.token.String.Single   : macros["strings"], # 'hello' and ordinary single-triple-quoted strings.

		pygments.token.Number             : macros["numbers"], # Parent category for numeric literal tokens.
		pygments.token.Number.Bin         : macros["numbers"], # 0b1010.
		pygments.token.Number.Float       : macros["numbers"], # 3.14, 1e3.
		pygments.token.Number.Hex         : macros["numbers"], # 0xFF.
		pygments.token.Number.Integer     : macros["numbers"], # 42.
		pygments.token.Number.Oct         : macros["numbers"], # 0o755.

		pygments.token.Operator     : macros["keywords"], # +, -, *, /, **, ==, =, @, and the dot in obj.attr.
		pygments.token.Operator.Word: macros["keywords"], # and, or, not, is, in.

		pygments.token.Punctuation       : macros["keywords"], # Parentheses, brackets, braces, commas, colons, semicolons.

		pygments.token.Comment            : macros["comments"] + italic, # Parent category for comment tokens.
		pygments.token.Comment.Hashbang   : macros["comments"] + italic, # #!/usr/bin/env python3 on the first line.
		pygments.token.Comment.Single     : macros["comments"] + italic, # # A Python comment.
		pygments.token.Comment.Special    : macros["comments"] + italic + bold, # TODO/FIXME tags when the codetagify filter is on.
	}
