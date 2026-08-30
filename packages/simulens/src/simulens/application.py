from pydantic import BaseModel, ConfigDict, Field, PositiveInt

from ._runtime import Runtime
from .scene import Scene


class ApplicationConfig(BaseModel):
    model_config = ConfigDict(
        strict=True,
        frozen=True,
        extra="forbid",
    )

    title: str = Field(
        default="Simulens",
        min_length=1,
    )

    size: tuple[PositiveInt, PositiveInt] = (800, 600)


class Application:
    def __init__(
        self,
        *,
        title: str = "Simulens",
        size: tuple[int, int] = (800, 600),
    ) -> None:
        self._config = ApplicationConfig(
            title=title,
            size=size,
        )

    def run(self, scene: Scene) -> None:
        runtime = Runtime(
            title=self._config.title,
            size=self._config.size,
        )
        try:
            while runtime.is_running:
                runtime.process_events()
                runtime.render(scene)
        finally:
            runtime.close()
