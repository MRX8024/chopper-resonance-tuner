"""MeasurementMode related tests are here."""
# Standard Library Imports
import sys
from enum import IntEnum

# Third-Party Imports
import pytest

# Local Imports
from chopper_tune import MeasurementMode


@pytest.mark.parametrize(
    "mode",
    [
        MeasurementMode.Resonances,
        MeasurementMode.Vibrations,
    ],
)
def test_it_is_an_int_enum(mode):
    """MeasurementMode is an IntEnum."""
    assert isinstance(mode, IntEnum)


@pytest.mark.parametrize(
    "mode,expected_value",
    [
        [MeasurementMode.Resonances, 0],
        [MeasurementMode.Vibrations, 1],
    ],
)
def test_enum_values(mode, expected_value):
    """Test enum values."""
    assert mode == expected_value


@pytest.mark.parametrize(
    "mode,expected_value",
    [
        [MeasurementMode.Resonances, "Resonances"],
        [MeasurementMode.Vibrations, "Vibrations"],
    ],
)
def test_enum_names(mode, expected_value):
    """Test enum names."""
    assert str(mode) == expected_value


def test_to_mode_mode_is_skipped():
    """MeasurementMode.to_mode() mode is skipped."""
    with pytest.raises(TypeError) as cm:
        _ = MeasurementMode.to_mode()

    py_error_message = {
        8: "to_mode() missing 1 required positional argument: 'mode'",
        9: "to_mode() missing 1 required positional argument: 'mode'",
    }.get(
        sys.version_info.minor,
        "MeasurementMode.to_mode() missing 1 required positional argument: 'mode'"
    )
    assert str(cm.value) == py_error_message


def test_to_mode_mode_is_none():
    """MeasurementMode.to_mode() mode is None."""
    with pytest.raises(TypeError) as cm:
        _ = MeasurementMode.to_mode(None)
    assert str(cm.value) == (
        "mode should be a MeasurementMode enum value or one "
        "of ['Resonances', 'Vibrations', 0, 1], not NoneType: 'None'"
    )


def test_to_mode_mode_is_not_a_str():
    """MeasurementMode.to_mode() mode is not an int or str."""
    with pytest.raises(TypeError) as cm:
        _ = MeasurementMode.to_mode(12334.123)

    assert str(cm.value) == (
        "mode should be a MeasurementMode enum value or one of "
        "['Resonances', 'Vibrations', 0, 1], not float: '12334.123'"
    )


def test_to_mode_mode_is_not_a_valid_str():
    """MeasurementMode.to_mode() mode is not a valid str."""
    with pytest.raises(ValueError) as cm:
        _ = MeasurementMode.to_mode("not a valid value")

    assert str(cm.value) == (
        "mode should be a MeasurementMode enum value or one of "
        "['Resonances', 'Vibrations', 0, 1], not 'not a valid value'"
    )


@pytest.mark.parametrize(
    "mode_name,mode",
    [
        # Resonances
        ["Resonances", MeasurementMode.Resonances],
        ["resonances", MeasurementMode.Resonances],
        ["RESONANCES", MeasurementMode.Resonances],
        ["ReSoNaNcEs", MeasurementMode.Resonances],
        ["rEsOnAnCeS", MeasurementMode.Resonances],
        [0, MeasurementMode.Resonances],
        # Vibrations
        ["Vibrations", MeasurementMode.Vibrations],
        ["vibrations", MeasurementMode.Vibrations],
        ["VIBRATIONS", MeasurementMode.Vibrations],
        ["ViBrAtIoNs", MeasurementMode.Vibrations],
        ["vIbRaTiOnS", MeasurementMode.Vibrations],
        [1, MeasurementMode.Vibrations],
    ],
)
def test_to_mode_is_working_properly(mode_name, mode):
    """MeasurementMode can parse schedule mode names."""
    assert MeasurementMode.to_mode(mode_name) == mode
