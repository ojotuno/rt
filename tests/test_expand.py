import pytest

from rt.errors import RecipeError
from rt.expand import expand_shell, expand_text, expand_token
from rt.lexer import Token

ARGS = ["recipe", "one", "two"]


@pytest.fixture(autouse=True)
def env(monkeypatch):
    monkeypatch.setenv("RT_A", "aaa")
    monkeypatch.setenv("RT_B", "bbb")
    monkeypatch.delenv("RT_MISSING", raising=False)


def test_all_env_vars_are_expanded():  # used to stop after the first one
    assert expand_text("$(RT_A)/$(RT_B)/x", ARGS) == "aaa/bbb/x"


def test_missing_env_var():
    with pytest.raises(RecipeError, match="RT_MISSING"):
        expand_text("$(RT_MISSING)", ARGS)


def test_dollar_without_parentheses_is_literal():
    assert expand_text("$HOME and $", ARGS) == "$HOME and $"


def test_args_are_replaced_in_place():  # used to replace the whole token
    assert expand_text("pre-args[1]-args[2].tar", ARGS) == "pre-one-two.tar"


def test_args_out_of_range():
    with pytest.raises(RecipeError, match="out of range"):
        expand_text("args[3]", ARGS)


def test_args_needs_word_boundary():
    assert expand_text("myargs[1]", ARGS) == "myargs[1]"


def test_argc():
    assert expand_token(Token("argc"), ARGS) == "3"
    assert expand_token(Token("argc", quoted=True), ARGS) == "argc"
    assert expand_token(Token("argcount"), ARGS) == "argcount"


def test_quoted_tokens_expand_env_and_args():
    assert expand_token(Token("$(RT_A) args[1]", quoted=True), ARGS) == "aaa one"


def test_expand_shell_keeps_quotes_and_spacing():
    text = """echo "a   b" 'c' argc --argc $(RT_A) args[2]"""
    assert expand_shell(text, ARGS) == """echo "a   b" 'c' 3 --argc aaa two"""
