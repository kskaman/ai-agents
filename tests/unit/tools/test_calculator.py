import pytest

from task_operator.tools.calculator import calculate


def test_calculate_basic_arithmetic():
    """A normal math expression returns the same answer Python would give."""
    assert calculate("(71 - 32) * 5 / 9") == str((71 - 32) * 5 / 9)


@pytest.mark.parametrize("expr", ["__import__('os')", "abs(-1)", "1; 2", ""])
def test_calculate_rejects_non_arithmetic(expr):
    """Anything that isn't plain arithmetic (code, function calls, empty input)
    is refused before it ever reaches eval()."""
    with pytest.raises(ValueError):
        calculate(expr)


def test_calculate_rejects_exponentiation():
    """`**` is blocked so the model can't hang the program with a huge power."""
    with pytest.raises(ValueError, match=r"\*\*"):
        calculate("9**9**9")
