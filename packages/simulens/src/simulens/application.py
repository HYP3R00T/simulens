import time

import slangpy as spy
from pydantic import BaseModel, ConfigDict, Field, PositiveInt


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

    @property
    def title(self) -> str:
        return self._config.title

    @property
    def size(self) -> tuple[int, int]:
        return self._config.size

    def run(self) -> None:
        width, height = self.size

        window = spy.Window(
            width=width,
            height=height,
            title=self.title,
            resizable=True,
        )

        try:
            while not window.should_close():
                window.process_events()

                # Temporary pacing until we introduce VSync.
                time.sleep(1 / 120)
        finally:
            window.close()
