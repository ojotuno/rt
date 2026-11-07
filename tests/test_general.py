import os


def test_print_concatenates_values(rt, recipe, monkeypatch):
    monkeypatch.setenv("RT_NAME", "world")
    result = rt(recipe("""
        print "hello " $(RT_NAME) "!"
        print "called with " argc " arguments: " args[1]
        print plain words
        print
    """), "x")
    assert result.code == 0
    assert result.lines == ["hello world!", "called with 2 arguments: x", "plainwords", ""]


def test_args0_is_the_recipe(rt, recipe):
    path = recipe("print args[0]")
    assert rt(path).lines == [str(path)]


def test_args_out_of_range_fails_with_line(rt, recipe):
    result = rt(recipe("print ok\nprint args[5]\nprint never\n"))
    assert result.code == 1
    assert result.lines == ["ok"]
    assert "recipe:2: args[5] out of range (argc = 1)" in result.err
    assert "Finished with 1 error(s)" in result.err


def test_missing_env_var_fails(rt, recipe, monkeypatch):
    monkeypatch.delenv("RT_NOPE", raising=False)
    result = rt(recipe("print $(RT_NOPE)"))
    assert result.code == 1
    assert "environment variable not found: RT_NOPE" in result.err


def test_exit_stops_successfully(rt, recipe, tmp_path):
    result = rt(recipe("""
        print "before"
        exit
        print "after"
        pack never.tar.gz
    """))
    assert result.code == 0
    assert result.lines == ["before"]
    assert "[rt] Exit" in result.out and "Done!" in result.out
    assert not (tmp_path / "never.tar.gz").exists()


def test_exit_inside_if(rt, recipe):
    result = rt(recipe("if argc == 1\nexit\nend\nprint after\n"))
    assert result.lines == []
    result = rt(recipe("if argc == 1\nexit\nend\nprint after\n"), "arg")
    assert result.lines == ["after"]


def test_rt_calls_recipe_with_args(rt, recipe):
    recipe('print "child " args[1] " " argc', name="child")
    result = rt(recipe("rt child hello\nprint parent\n"))
    assert result.code == 0
    assert result.lines == ["child hello 2", "parent"]
    assert result.out.count("Done!") == 1  # summary only for the top-level call


def test_rt_child_exit_only_stops_child(rt, recipe):
    recipe("print c1\nexit\nprint c2\n", name="child")
    result = rt(recipe("rt child\nprint parent\n"))
    assert result.lines == ["c1", "parent"]


def test_rt_child_failure_stops_parent(rt, recipe):
    recipe("> exit 3", name="child")
    result = rt(recipe("rt child\nprint never\n"))
    assert result.code == 1
    assert "never" not in result.lines
    assert "rt call failed with exit code 1" in result.err


def test_rt_child_root_dir_does_not_leak(rt, recipe, tmp_path):
    (tmp_path / "sub").mkdir()
    recipe("root_dir sub", name="child")
    result = rt(recipe("rt child\n> pwd\n"))
    assert result.lines[-1] == str(tmp_path)


def test_rt_missing_file(rt, recipe):
    result = rt(recipe("rt nothere"))
    assert result.code == 1
    assert "file not found: nothere" in result.err


def test_rt_recursion_limit(rt, recipe):
    path = recipe("rt recipe")
    result = rt(path)
    assert result.code == 1
    assert "too many nested rt calls" in result.err


def test_cwd_is_restored_after_recipe(rt, recipe, tmp_path):
    (tmp_path / "sub").mkdir()
    rt(recipe("root_dir sub"))
    assert os.getcwd() == str(tmp_path)
