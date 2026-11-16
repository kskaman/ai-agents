from task_operator.tools.text import count_characters


def test_count_characters_includes_spaces():
    """Spaces count as characters."""
    assert count_characters("hello world") == "11"
