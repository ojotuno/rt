import pytest

from rt.errors import ParseErrors
from rt.parser import IfBlock, Statement, lex_line, parse


def errors(text):
    with pytest.raises(ParseErrors) as exc:
        parse(text, "r")
    return [str(e) for e in exc.value.errors]


def test_statement_fields():
    stmt = lex_line('add  "my file"  as x  # c', 7, "r")
    assert stmt.keyword == "add"
    assert [t.value for t in stmt.args] == ["my file", "as", "x"]
    assert stmt.rest == '"my file"  as x'
    assert (stmt.line, stmt.source) == (7, "r")


@pytest.mark.parametrize("line", ["> echo hi", ">echo hi", "  >   echo hi"])
def test_shell_line(line):
    stmt = lex_line(line, 1, "r")
    assert (stmt.keyword, stmt.rest) == (">", "echo hi")


def test_blank_and_comment_lines_are_skipped():
    assert parse("\n   \n# c\n\t\n") == []


def test_nested_ifs_build_a_tree():
    nodes = parse("if a == a\nprint x\nif 1 < 2\nprint y\nend\nend\nprint z\n")
    assert isinstance(nodes[0], IfBlock) and isinstance(nodes[1], Statement)
    inner = nodes[0].body[1]
    assert isinstance(inner, IfBlock)
    assert inner.body[0].args[0].value == "y"


def test_all_syntax_errors_are_reported_with_lines():
    errs = errors("print ok\nfoo bar\npack\nif a ~ b\nend\nend\nexit now\n")
    assert errs == [
        "r:2: unknown keyword: foo",
        "r:3: usage: pack FILENAME",
        "r:4: usage: if VALUE OPERATOR VALUE  (operators: == != < > <= >=)",
        "r:5: end without a matching if",
        "r:6: end without a matching if",
        "r:7: usage: exit",
    ]


def test_if_without_end():
    assert errors("print a\nif a == a\nprint b\n") == ["r:2: if without end"]


def test_end_with_arguments():
    assert errors("if a == a\nend now\n") == ["r:2: end does not accept arguments", "r:1: if without end"]


def test_unterminated_quote_has_line():
    assert errors('print ok\nprint "bad\n') == ["r:2: unterminated quoted string"]


@pytest.mark.parametrize("line, message", [
    ("add a b", "usage: add PATTERN [as NAME | in DIR]"),
    ("add a to b", "usage: add PATTERN [as NAME | in DIR]"),
    ("ignore a in b", "usage: ignore PATTERN [from DIR]"),
    ("root_dir", "usage: root_dir PATH"),
    ("root_dir a/*", "root_dir cannot contain wildcards"),
    ("target_dir a b", "usage: target_dir PATH"),
    ("target_dir a?", "target_dir cannot contain wildcards"),
    ("rt", "usage: rt [-url] RECIPE|PACKAGE [ARGS...]"),
    (">", "usage: > COMMAND"),
    ("git", "usage: git ARGS..."),
])
def test_command_arity(line, message):
    assert errors(line) == [f"r:1: {message}"]


def test_nothing_runs_when_there_are_syntax_errors(rt, recipe, tmp_path):
    path = recipe("> touch created\nbogus\n")
    result = rt(path)
    assert result.code == 1
    assert not (tmp_path / "created").exists()
    assert "syntax error: " in result.err and "unknown keyword: bogus" in result.err
