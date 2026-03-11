"""SearchMethod related tests are here."""
# Standard Library Imports
import sys
from enum import IntEnum

# Third-Party Imports
import pytest

# Local Imports
from chopper_tune import SearchMethod


@pytest.mark.parametrize(
    "method",
    [
        SearchMethod.BruteForce,
        SearchMethod.Adaptive,
        SearchMethod.Progressive,
    ],
)
def test_it_is_an_int_enum(method):
    """SearchMethod is an IntEnum."""
    assert isinstance(method, IntEnum)


@pytest.mark.parametrize(
    "method,expected_value",
    [
        [SearchMethod.BruteForce, 0],
        [SearchMethod.Adaptive, 1],
        [SearchMethod.Progressive, 2],
    ],
)
def test_enum_values(method, expected_value):
    """Test enum values."""
    assert method == expected_value


@pytest.mark.parametrize(
    "method,expected_value",
    [
        [SearchMethod.BruteForce, "BruteForce"],
        [SearchMethod.Adaptive, "Adaptive"],
        [SearchMethod.Progressive, "Progressive"],
    ],
)
def test_enum_names(method, expected_value):
    """Test enum names."""
    assert str(method) == expected_value


def test_to_method_method_is_skipped():
    """SearchMethod.to_method() method is skipped."""
    with pytest.raises(TypeError) as cm:
        _ = SearchMethod.to_method()

    py_error_message = {
        8: "to_method() missing 1 required positional argument: 'method'",
        9: "to_method() missing 1 required positional argument: 'method'",
    }.get(
        sys.version_info.minor,
        "SearchMethod.to_method() missing 1 required positional argument: 'method'"
    )
    assert str(cm.value) == py_error_message


def test_to_method_method_is_none():
    """SearchMethod.to_method() method is None."""
    with pytest.raises(TypeError) as cm:
        _ = SearchMethod.to_method(None)
    assert str(cm.value) == (
        "method should be a SearchMethod enum value or one "
        "of ['BruteForce', 'Adaptive', 'Progressive', 0, 1, 2], not NoneType: 'None'"
    )


def test_to_method_method_is_not_a_str():
    """SearchMethod.to_method() method is not an int or str."""
    with pytest.raises(TypeError) as cm:
        _ = SearchMethod.to_method(12334.123)

    assert str(cm.value) == (
        "method should be a SearchMethod enum value or one of "
        "['BruteForce', 'Adaptive', 'Progressive', 0, 1, 2], not float: '12334.123'"
    )


def test_to_method_method_is_not_a_valid_str():
    """SearchMethod.to_method() method is not a valid str."""
    with pytest.raises(ValueError) as cm:
        _ = SearchMethod.to_method("not a valid value")

    assert str(cm.value) == (
        "method should be a SearchMethod enum value or one of "
        "['BruteForce', 'Adaptive', 'Progressive', 0, 1, 2], not 'not a valid value'"
    )


@pytest.mark.parametrize(
    "method_name,method",
    [
        # BruteForce
        ["BruteForce", SearchMethod.BruteForce],
        ["bruteforce", SearchMethod.BruteForce],
        ["BRUTEFORCE", SearchMethod.BruteForce],
        ["BrUtEfOrCe", SearchMethod.BruteForce],
        ["bRuTeFoRcE", SearchMethod.BruteForce],

        # Brute_Force
        ["Brute_Force", SearchMethod.BruteForce],
        ["brute_force", SearchMethod.BruteForce],
        ["BRUTE_FORCE", SearchMethod.BruteForce],
        ["BrUtE_FoRcE", SearchMethod.BruteForce],
        ["bRuTe_fOrCe", SearchMethod.BruteForce],
        [0, SearchMethod.BruteForce],

        # Adaptive
        ["Adaptive", SearchMethod.Adaptive],
        ["adaptive", SearchMethod.Adaptive],
        ["ADAPTIVE", SearchMethod.Adaptive],
        ["AdApTiVe", SearchMethod.Adaptive],
        ["aDaPtIvE", SearchMethod.Adaptive],
        [1, SearchMethod.Adaptive],

        # Progressive
        ["Progressive", SearchMethod.Progressive],
        ["progressive", SearchMethod.Progressive],
        ["PROGRESSIVE", SearchMethod.Progressive],
        ["PrOgReSsIvE", SearchMethod.Progressive],
        ["pRoGrEsSiVe", SearchMethod.Progressive],
        [2, SearchMethod.Progressive],
    ],
)
def test_to_method_is_working_properly(method_name, method):
    """SearchMethod can parse schedule method names."""
    assert SearchMethod.to_method(method_name) == method
