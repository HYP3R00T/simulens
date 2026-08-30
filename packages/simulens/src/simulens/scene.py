from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field

ColorChannel = Annotated[float, Field(ge=0.0, le=1.0)]
Color = tuple[ColorChannel, ColorChannel, ColorChannel, ColorChannel]


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
    ) -> None:
        self._config = SceneConfig(background_color=background_color)

    @property
    def background_color(self) -> Color:
        return self._config.background_color
