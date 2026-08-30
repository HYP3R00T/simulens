from typing import TypeVar

from pydantic import BaseModel, ConfigDict

from .camera import Camera2D
from .node import Node
from ..geometry import Color

NodeType = TypeVar("NodeType", bound=Node)


class SceneConfig(BaseModel):
    model_config = ConfigDict(
        strict=True,
        frozen=True,
        extra="forbid",
    )

    background_color: Color = (0.0, 0.0, 0.0, 1.0)


class Scene:
    def __init__(
        self,
        *,
        background_color: Color = (0.0, 0.0, 0.0, 1.0),
        camera: Camera2D | None = None,
    ) -> None:
        self._config = SceneConfig(background_color=background_color)
        self._camera = camera or Camera2D()
        self._nodes: list[Node] = []

    def add(self, node: NodeType) -> NodeType:
        self._nodes.append(node)
        return node

    @property
    def background_color(self) -> Color:
        return self._config.background_color

    @property
    def camera(self) -> Camera2D:
        return self._camera

    @property
    def nodes(self) -> tuple[Node, ...]:
        return tuple(self._nodes)
