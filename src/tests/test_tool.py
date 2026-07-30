import os
import tempfile
from ..tools import ReadFile
from ..tools import WriteFile

# Read Tool Tests
def test_tool_has_required_attributes():
    """Verify tool classes have name, description, input_schema."""
    tool = ReadFile()
    assert tool.name == "read_file"
    assert tool.description is not None
    assert tool.input_schema is not None


def test_read_file_adds_line_numbers():
    """Verify ReadFile prefixes each line with line numbers."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt' , delete=False) as tmp_file:
        tmp_file.write("line one\nline two\nline three")
        tmp_file_path = tmp_file.name

    try:
        tool = ReadFile()
        result = tool.execute(tmp_file_path)
        assert "1 | line one" in result
        assert "2 | line two" in result
        assert "3 | line three" in result
    finally:
        os.unlink(tmp_file_path)  # Clean up the temporary file

# Write Tool Tests
def test_write_file_creates_file():
    """Verify WriteFile creates a file with content."""
    with tempfile.TemporaryDirectory() as tmpdir:

        file_path = os.path.join(tmpdir, "test.txt")

        tool = WriteFile()
        result = tool.execute(file_path, "Hello, World!")

        assert os.path.exists(file_path)
        assert "Successfully wrote" in result

        with open(file_path, 'r', encoding='utf-8') as f:
            assert f.read() == "Hello, World!"