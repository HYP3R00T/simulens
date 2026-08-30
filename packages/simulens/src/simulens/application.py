import slangpy as spy
from pydantic import BaseModel, ConfigDict, Field, PositiveInt

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

    @property
    def title(self) -> str:
        return self._config.title

    @property
    def size(self) -> tuple[int, int]:
        return self._config.size

    def run(self, scene: Scene) -> None:
        width, height = self.size

        device = spy.Device()

        try:
            window = spy.Window(
                width=width,
                height=height,
                title=self.title,
                resizable=True,
            )

            try:
                surface = device.create_surface(window)
                surface.configure(
                    width=width,
                    height=height,
                    vsync=True,
                )

                try:
                    while not window.should_close():
                        window.process_events()

                        surface_texture = surface.acquire_next_image()

                        if surface_texture is None:
                            continue

                        command_encoder = device.create_command_encoder()

                        command_encoder.clear_texture_float(
                            surface_texture,
                            clear_value=spy.float4(*scene.background_color),
                        )

                        device.submit_command_buffer(command_encoder.finish())

                        del surface_texture
                        surface.present()
                finally:
                    device.wait()
                    surface.unconfigure()
            finally:
                window.close()
        finally:
            device.close()
