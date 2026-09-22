"""Typed validation helpers shared by landmark scorers."""

import math
from collections.abc import Collection, Sequence
from typing import cast

type JsonObject = dict[str, object]
type Point3 = tuple[float, float, float]
type Matrix3 = tuple[Point3, Point3, Point3]


class ContractError(ValueError):
    """Raised when a submitted answer or scorer input violates its contract."""


def require(condition: bool) -> None:
    """Raise a stable exception when a contract condition is not met."""
    if not condition:
        raise ContractError


def object_value(value: object, *, keys: Collection[str] | None = None) -> JsonObject:
    """Return a string-keyed object, optionally requiring its exact keys."""
    if not isinstance(value, dict) or not all(isinstance(key, str) for key in value):
        raise ContractError
    result = cast(JsonObject, value)
    if keys is not None:
        require(set(result) == set(keys))
    return result


def finite_number(value: object) -> float:
    """Return a finite JSON number, rejecting booleans."""
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        raise ContractError
    number = float(value)
    require(math.isfinite(number))
    return number


def finite_point3(value: object) -> Point3:
    """Return a finite three-coordinate JSON array."""
    if not isinstance(value, list) or len(value) != 3:
        raise ContractError
    return (
        finite_number(value[0]),
        finite_number(value[1]),
        finite_number(value[2]),
    )


def finite_matrix3(value: object) -> Matrix3:
    """Return a finite 3-by-3 JSON matrix."""
    if not isinstance(value, list) or len(value) != 3:
        raise ContractError
    return (
        finite_point3(value[0]),
        finite_point3(value[1]),
        finite_point3(value[2]),
    )


def string_choice(value: object, choices: Collection[str]) -> str:
    """Return a string when it belongs to the declared finite choice set."""
    if not isinstance(value, str) or value not in choices:
        raise ContractError
    return value


def physical_distance_mm(
    first: Sequence[float],
    second: Sequence[float],
    linear_voxel_to_mm: Sequence[Sequence[float]],
) -> float:
    """Measure the physical distance between two voxel-space points."""
    delta = [first[index] - second[index] for index in range(3)]
    transformed = [
        sum(linear_voxel_to_mm[row][column] * delta[column] for column in range(3))
        for row in range(3)
    ]
    return math.sqrt(sum(component * component for component in transformed))
