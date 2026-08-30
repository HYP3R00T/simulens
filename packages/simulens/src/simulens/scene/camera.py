from pydantic import BaseModel, ConfigDict, PositiveFloat

from ..geometry import Point2D


class Camera2DConfig(BaseModel):
    model_config = ConfigDict(
        strict=True,
        frozen=True,
        extra="forbid",
    )

    center: Point2D = (0.0, 0.0)
    visible_height: PositiveFloat = 2.0


class Camera2D:
    def __init__(
        self,
        *,
        center: Point2D = (0.0, 0.0),
        visible_height: float = 2.0,
    ) -> None:
        self._config = Camera2DConfig(
            center=center,
            visible_height=visible_height,
        )

    @property
    def center(self) -> Point2D:
        return self._config.center

    @property
    def visible_height(self) -> float:
        return self._config.visible_height
