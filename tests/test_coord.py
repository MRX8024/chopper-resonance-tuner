"""Tests for the Position class."""

# Third-Party Imports
import pytest

from chopper_tune import Coord


def test_coord_init_empty():
    """Coord can not be initialized without any arguments."""
    with pytest.raises(TypeError) as cm:
        _ = Coord()
    assert str(cm.value) == (
        "Coord.__new__() missing 1 required positional argument: 't'"
    )

def test_coord_init_with_tuple():
    """Coord can be initialized with a tuple."""
    coord = Coord((1, 2, 3))
    assert len(coord) == 3


def test_coord_init_with_list():
    """Coord can be initialized with a list."""
    coord = Coord([1, 2, 3])
    assert len(coord) == 3


def test_coord_item_get():
    """Coord items can be get."""
    coord = Coord((1, 2, 3))
    assert coord[0] == 1
    assert coord[1] == 2
    assert coord[2] == 3


def test_coord_item_property_get():
    """Coord items can be retrieved from the x, y, z properties."""
    coord = Coord((1, 2, 3))
    assert coord.x == 1
    assert coord.x == coord[0]
    assert coord.y == 2
    assert coord.y == coord[1]
    assert coord.z == 3
    assert coord.z == coord[2]


def test_coord_item_property_set():
    """Coord items can be assigned through properties."""
    coord = Coord((12, 34, 144))
    test_value = 14
    assert coord.x != test_value
    coord.x = test_value
    assert coord.x == test_value

    test_value = 231
    assert coord.y != test_value
    coord.y = test_value
    assert coord.y == test_value

    test_value = 23112
    assert coord.z != test_value
    coord.z = test_value
    assert coord.z == test_value


def test_coord_item_property_set_2():
    """Coord items can be assigned through properties."""
    coord = Coord((12, 34, 144))
    test_value = 14
    expected_value = coord.x + test_value
    assert coord.x != expected_value
    coord.x += test_value
    assert coord.x == expected_value


def test_coord_item_property_set_3():
    """Coord items can be assigned through properties."""
    coord = Coord((12, 34, 144))
    test_value = 14
    expected_value = coord.x * test_value
    assert coord.x != expected_value
    coord.x *= test_value
    assert coord.x == expected_value


def test_coord_added_a_float():
    """Coord float can be added."""
    coord1 = Coord((12, 34, 144))
    result = coord1 + 12
    assert isinstance(result, Coord)
    assert result.x == 24
    assert result.y == 46
    assert result.z == 156


def test_coord_subtract_a_float():
    """Coord a float can be subtracted."""
    coord1 = Coord((12, 34, 144))
    result = coord1 - 12
    assert isinstance(result, Coord)
    assert result.x == 0
    assert result.y == 22
    assert result.z == 132


def test_coord_multiply_by_float():
    """Coord can be multiplied with a float."""
    coord1 = Coord((12, 34, 144))
    result = coord1 * 12
    assert isinstance(result, Coord)
    assert result.x == 144
    assert result.y == 408
    assert result.z == 1728


def test_coord_divided_by_float():
    """Coord can be divided by a float."""
    coord1 = Coord((12, 48, 144))
    result = coord1 / 12
    assert isinstance(result, Coord)
    assert result.x == 1
    assert result.y == 4
    assert result.z == 12


def test_coord_chain_calculation():
    """Coord with some chaing calculations."""
    coord1 = Coord((12, 34, 144))
    coord2 = Coord((0, 0, 0))
    coord2 += (coord1 * 12)
    assert isinstance(coord2, Coord)
    assert coord2.x == 144
    assert coord2.y == 408
    assert coord2.z == 1728


@pytest.mark.parametrize(
    "test_value", (
        Coord((-1, -1, 0)),
        (-1, -1, 0),
        [-1, -1, 0]
    )
)
def test_coord_added_with_another_coord(test_value):
    """Coord can be added by other Coords, lists or tuples."""
    coord1 = Coord((12, 34, 144))
    coord2 = test_value
    result = coord1 + coord2
    assert isinstance(result, Coord)
    assert result.x == 11
    assert result.y == 33
    assert result.z == 144


@pytest.mark.parametrize(
    "test_value", (
        Coord((-1, -1, 0)),
        (-1, -1, 0),
        [-1, -1, 0]
    )
)
def test_coord_iadded_with_another_coord(test_value):
    """Coord can be added by other Coords, lists or tuples."""
    coord1 = Coord((12, 34, 144))
    coord2 = test_value
    coord1 += coord2
    assert isinstance(coord1, Coord)
    assert coord1.x == 11
    assert coord1.y == 33
    assert coord1.z == 144


@pytest.mark.parametrize(
    "test_value", (
        Coord((-1, -1, 0)),
        (-1, -1, 0),
        [-1, -1, 0]
    )
)
def test_coord_multiply_with_another_coord(test_value):
    """Coord can be multiplied by other Coords, lists or tuples."""
    coord1 = Coord((12, 34, 144))
    coord2 = test_value
    result = coord1 * coord2
    assert isinstance(result, Coord)
    assert result.x == -12
    assert result.y == -34
    assert result.z == 0


@pytest.mark.parametrize(
    "test_value", (
        Coord((-1, -1, 0)),
        (-1, -1, 0),
        [-1, -1, 0]
    )
)
def test_coord_i_multiply_with_another_coord(test_value):
    """Coord can be i_multiplied by other Coords, lists or tuples."""
    coord1 = Coord((12, 34, 144))
    assert coord1.x == 12
    assert coord1.y == 34
    assert coord1.z == 144
    coord2 = test_value
    coord1 *= coord2
    assert coord1.x == -12
    assert coord1.y == -34
    assert coord1.z == 0


@pytest.mark.parametrize(
    "test_value", (
        Coord((-2, -1, 1)),
        (-2, -1, 1),
        [-2, -1, 1]
    )
)
def test_coord_divide_with_another_coord(test_value):
    """Coord can be divided by other Coords, lists or tuples."""
    coord1 = Coord((12, 34, 144))
    coord2 = test_value
    result = coord1 / coord2
    assert isinstance(result, Coord)
    assert result.x == -6
    assert result.y == -34
    assert result.z == 144


def test_coord_itruediv_with_float():
    """Coord can be divided by other flots."""
    coord1 = Coord((12, 34, 144))
    coord1 /= 2
    assert isinstance(coord1, Coord)
    assert coord1.x == 6
    assert coord1.y == 17
    assert coord1.z == 72


@pytest.mark.parametrize(
    "test_value, expected_result", (
        (Coord((1, 0, 0)), 1),
        (Coord((1, 1, 0)), 2**0.5),
        (Coord((3, 4, 0)), 5),
    )
)
def test_length(test_value, expected_result):
    """length() calculates the vector length."""
    assert test_value.length() == pytest.approx(expected_result)


@pytest.mark.parametrize(
    "test_value", (
        Coord((1, 10, 0)),
        Coord((1, 1, 0)),
        Coord((3, 4, 0)),
    )
)
def test_unitize(test_value):
    """length() calculates the vector length."""
    assert test_value.length() != pytest.approx(1.0)
    result = test_value.unitize()
    assert isinstance(result, Coord)
    assert test_value == result
    assert test_value.length() == pytest.approx(1.0)
