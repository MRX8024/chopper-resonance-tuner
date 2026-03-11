"""Test CoordinateGenerator class."""

# Third-Party Imports
import pytest

# Local Imports
from chopper_tune import Coord, CoordGenerator


def test_init_direction_arg_is_skipped():
    """__init__() requires direction arg."""
    with pytest.raises(TypeError) as cm:
        _ = CoordGenerator(
            start_coord=Coord((1, 0, 0))
        )

    assert str(cm.value) == (
        "CoordGenerator.__init__() missing 1 required positional argument: 'direction'"
    )


def test_init_direction_is_not_a_list_tuple_or_coord_instance():
    """__init__() direction arg is not a list, tuple or Coord instance raise TypeError."""
    with pytest.raises(TypeError) as cm:
        _ = CoordGenerator(
            direction="not a list, tuple or Coord instance",
            start_coord=Coord((1, 0, 0))
        )

    assert str(cm.value) == (
        "direction should be a list, tuple or a Coord instance, not str: "
        "'not a list, tuple or Coord instance'"
    )


@pytest.mark.parametrize(
    "direction", (
        Coord((0, 0, 0)),
        (0, 0, 0),
        [0, 0, 0],
    )
)
def test_init_direction_length_is_zero(direction):
    """__init__() direction arg length is zero raise ValueError."""
    with pytest.raises(ValueError) as cm:
        _ = CoordGenerator(
            direction=direction,
            start_coord=Coord((1, 0, 0))
        )

    assert str(cm.value) == "direction length cannot be zero."


@pytest.mark.parametrize(
    "direction", (
        Coord((10, 21, 1)),
        (123, 35, 2.1),
        [0, 233.2, 12.3],
    )
)
def test_direction_is_normalized(direction):
    """Direction is normalized to length 1."""
    generator = CoordGenerator(
        direction=direction,
        start_coord=Coord((0, 0, 0)),
    )
    assert generator.direction is not None
    assert generator.direction.length() == pytest.approx(1.0)


def test_next_position_core_xy():
    """Generate coordinates for a corexy printer."""
    generator = CoordGenerator(
        direction=Coord((1, 1, 0)),
        start_coord=Coord((0, 0, 0)),
    )
    assert generator.direction is not None

    pos1 = generator.next(1.0)
    assert isinstance(pos1, Coord)
    assert pos1.x == pytest.approx((2**0.5)/2)
    assert pos1.y == pytest.approx((2**0.5)/2)
    assert pos1.z == pytest.approx(0)

    pos2 = generator.next(10.0)
    assert pos2.x == pytest.approx((2**0.5) / 2 + (10*(2**0.5) / 2))
    assert pos2.y == pytest.approx((2**0.5) / 2 + (10*(2**0.5) / 2))
    assert pos2.z == pytest.approx(0)

    pos3 = generator.next(9.0)
    assert pos3.x == pytest.approx((2**0.5) / 2 + (10*(2**0.5) / 2) + (9*(2**0.5) / 2))
    assert pos3.y == pytest.approx((2**0.5) / 2 + (10*(2**0.5) / 2) + (9*(2**0.5) / 2))
    assert pos3.z == pytest.approx(0)


def test_next_position_cartesian():
    """Generate coordinates for Cartesian printer."""
    generator = CoordGenerator(
        direction=Coord((1, 0, 0)),
        start_coord=Coord((0, 0, 0)),
    )
    assert generator.direction is not None

    pos1 = generator.next(1.0)
    assert isinstance(pos1, Coord)
    assert pos1.x == pytest.approx(1.0)
    assert pos1.y == pytest.approx(0)
    assert pos1.z == pytest.approx(0)

    pos2 = generator.next(10.0)
    assert pos2.x == pytest.approx(11.0)
    assert pos2.y == pytest.approx(0)
    assert pos2.z == pytest.approx(0)

    pos3 = generator.next(9.0)
    assert pos3.x == pytest.approx(20)
    assert pos3.y == pytest.approx(0)
    assert pos3.z == pytest.approx(0)
