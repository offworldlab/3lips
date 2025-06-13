"""Basic test to ensure pytest runs successfully."""


def test_basic():
    """A basic test to ensure the test framework works."""
    assert True


def test_imports():
    """Test that basic imports work."""
    import math
    import os
    import sys

    assert math.pi > 3
    assert os.path.exists(".")
    assert sys.version_info.major >= 3
