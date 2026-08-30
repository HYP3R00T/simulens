import slangpy as spy

from .renderer import Renderer
from ..scene import Scene


class Runtime:
    def __init__(
        self,
        *,
        title: str,
        size: tuple[int, int],
    ) -> None:
        width, height = size

        self._renderer = Renderer()

        try:
            self._window = spy.Window(
                width=width,
                height=height,
                title=title,
                resizable=True,
            )
        except Exception:
            self._renderer.close()
            raise

        try:
            self._renderer.attach(self._window)
        except Exception:
            self._window.close()
            self._renderer.close()
            raise

        self._closed = False

    @property
    def is_running(self) -> bool:
        return not self._window.should_close()

    def process_events(self) -> None:
        self._window.process_events()

    def render(self, scene: Scene) -> None:
        self._renderer.render(scene)

    def close(self) -> None:
        if self._closed:
            return

        self._closed = True

        try:
            self._renderer.close()
        finally:
            self._window.close()
