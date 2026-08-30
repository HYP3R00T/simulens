import slangpy as spy

from ..scene import Scene


class Renderer:
    def __init__(self) -> None:
        self._device = spy.Device()
        self._surface: spy.Surface | None = None
        self._closed = False

    def attach(self, window: spy.Window) -> None:
        if self._surface is not None:
            raise RuntimeError("Renderer is already attached to a window")

        surface = self._device.create_surface(window)
        surface.configure(
            width=window.width,
            height=window.height,
            vsync=True,
        )

        self._surface = surface

    def render(self, scene: Scene) -> None:
        if self._surface is None:
            raise RuntimeError("Renderer is not attached to a window")

        surface_texture = self._surface.acquire_next_image()

        if surface_texture is None:
            return

        try:
            command_encoder = self._device.create_command_encoder()

            command_encoder.clear_texture_float(
                surface_texture,
                clear_value=spy.float4(*scene.background_color),
            )

            self._device.submit_command_buffer(command_encoder.finish())
        finally:
            del surface_texture

        self._surface.present()

    def close(self) -> None:
        if self._closed:
            return

        self._closed = True

        try:
            self._device.wait()
        finally:
            try:
                if self._surface is not None:
                    self._surface.unconfigure()
            finally:
                self._device.close()
