from pydantic import BaseModel, ConfigDict

from ..geometry import Color, Point2D
from ..scene import Node


class TriangleConfig(BaseModel):
    model_config = ConfigDict(
        strict=True,
        frozen=True,
        extra="forbid",
    )

    vertices: tuple[Point2D, Point2D, Point2D]
    color: Color = (0.2, 0.7, 1.0, 1.0)


class Triangle(Node):
    def __init__(
        self,
        *,
        vertices: tuple[Point2D, Point2D, Point2D],
        color: Color = (0.2, 0.7, 1.0, 1.0),
    ) -> None:
        self._config = TriangleConfig(
            vertices=vertices,
            color=color,
        )

    @property
    def vertices(self) -> tuple[Point2D, Point2D, Point2D]:
        return self._config.vertices

    @property
    def color(self) -> Color:
        return self._config.color
