import moderngl

from ..scene import Scene


class Renderer:
    def __init__(self) -> None:
        self._context = moderngl.create_context(require=330)
        self._framebuffer_size = (0, 0)
        self._closed = False

    def resize(self, width: int, height: int) -> None:
        self._framebuffer_size = (width, height)

        if width > 0 and height > 0:
            self._context.viewport = (0, 0, width, height)

    def render(self, scene: Scene) -> bool:
        width, height = self._framebuffer_size

        if width <= 0 or height <= 0:
            return False

        self._context.screen.use()
        self._context.clear(*scene.background_color)
        return True

    def close(self) -> None:
        if self._closed:
            return

        self._closed = True
        self._context.release()
