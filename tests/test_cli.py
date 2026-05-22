import pytest
import argparse
from src.cli.main import non_negative_int


def test_non_negative_int():
    try:
        assert non_negative_int("10") == 10
        assert non_negative_int("0") == 0
        
        with pytest.raises(argparse.ArgumentTypeError):
            non_negative_int("-5")
            
        with pytest.raises(argparse.ArgumentTypeError):
            non_negative_int("abc")
    except Exception as e:
        pytest.fail(f"Test failed with unexpected exception: {e}")
