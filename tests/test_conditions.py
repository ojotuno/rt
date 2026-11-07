import pytest

from rt.conditions import compare
from rt.errors import RecipeError


@pytest.mark.parametrize("left, op, right, expected", [
    ("a", "==", "a", True), ("a", "==", "b", False),
    ("a", "!=", "b", True), ("a", "!=", "a", False),
    ("10", ">", "3", True),        # was compared as text before ("10" < "3")
    ("3", ">", "10", False),
    ("3", "<", "10", True), ("10", "<", "3", False),
    ("5", "<=", "5", True), ("6", "<=", "5", False),
    ("5", ">=", "5", True), ("4", ">=", "5", False),
    ("1.5", "<", "2", True), ("-1", "<", "0", True),
    ("10", "==", "10.0", True), ("010", "==", "10", True),
    ("", "!=", "x", True), ("", "==", "", True),
])
def test_compare(left, op, right, expected):
    assert compare(left, op, right) is expected


@pytest.mark.parametrize("op", ["<", ">", "<=", ">="])
def test_order_needs_numbers(op):
    with pytest.raises(RecipeError, match="needs numbers"):
        compare("abc", op, "1")


def test_if_runs_block_only_when_true(rt, recipe):
    result = rt(recipe("""
        if args[1] == yes
        print "yes-block"
        end
        if args[1] != yes
        print "no-block"
        end
        print "after"
    """), "yes")
    assert result.lines == ["yes-block", "after"]


def test_skipped_block_is_not_evaluated(rt, recipe):
    # args[9] would fail if the inner if/print were evaluated
    result = rt(recipe("""
        if 1 > 2
        if args[9] == x
        print args[9]
        end
        print args[9]
        end
        print "ok"
    """))
    assert result.code == 0
    assert result.lines == ["ok"]


def test_nested_false_inner_keeps_running_outer(rt, recipe):
    # The old interpreter lost track of the nesting here and skipped the rest.
    result = rt(recipe("""
        if no == yes
        if 1 < 2
        print "FAIL"
        end
        end
        print "reached"
    """))
    assert result.code == 0
    assert result.lines == ["reached"]


def test_bad_comparison_reports_line(rt, recipe):
    result = rt(recipe("print a\nif abc < 3\nend\n"))
    assert result.code == 1
    assert "recipe:2: operator < needs numbers" in result.err
