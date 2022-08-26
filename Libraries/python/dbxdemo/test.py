from testbook import testbook
import pytest

@testbook("notebooks.ipynb", execute=0)
def test_output(tb):
    assert tb.cell_output_text(0) == "hello world"

@testbook("notebooks.ipynb", execute=True)
def test_add(tb):
    add = tb.get("add")
    assert add(1, 2) == 3
