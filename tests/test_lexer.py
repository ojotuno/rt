import pytest

from rt.errors import RecipeSyntaxError
from rt.lexer import Token, strip_comment, tokenize


def values(text):
    return [t.value for t in tokenize(text)]


@pytest.mark.parametrize("text, expected", [
    ("add a b", ["add", "a", "b"]),
    ("  add   a  ", ["add", "a"]),
    ("add\ta\t\tb", ["add", "a", "b"]),          # tabs separate (used to be glued)
    ('print "hello world"', ["print", "hello world"]),
    ('print "a" "b"', ["print", "a", "b"]),
    ('pre"fix suf"fix', ["prefix suffix"]),
    (r'print "say \"hi\" \\ ok"', ["print", 'say "hi" \\ ok']),
    ("", []),
])
def test_tokenize(text, expected):
    assert values(text) == expected


def test_quoted_flag_and_empty_string():
    assert tokenize('a "" "b"') == [Token("a"), Token("", True), Token("b", True)]


def test_unterminated_quote():
    with pytest.raises(RecipeSyntaxError, match="unterminated"):
        tokenize('print "oops')


@pytest.mark.parametrize("text, expected", [
    ("add a # comment", "add a "),
    ("# whole line", ""),
    ('print "issue #1"', 'print "issue #1"'),     # inside quotes
    ("print issue#1", "print issue#1"),           # not at word start
    (r'print "\"#" # c', r'print "\"#" '),
])
def test_strip_comment(text, expected):
    assert strip_comment(text) == expected
