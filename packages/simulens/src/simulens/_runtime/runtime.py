import glfw

from .._rendering import Renderer
from ..scene import Scene


class Runtime:
    def __init__(
        self,
        *,
        title: str,
        size: tuple[int, int],
    ) -> None:
        if not glfw.init():
            raise RuntimeError("Failed to initialize GLFW")

        self._window = None
        self._renderer: Renderer | None = None
        self._closed = False
        self._visible = False

        try:
            glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
            glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
            glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
            glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, glfw.TRUE)
            glfw.window_hint(glfw.RESIZABLE, glfw.TRUE)
            glfw.window_hint(glfw.VISIBLE, glfw.FALSE)

            width, height = size
            window = glfw.create_window(width, height, title, None, None)

            if window is None:
                raise RuntimeError("Failed to create a GLFW window")

            self._window = window
            glfw.make_context_current(window)
            glfw.swap_interval(1)

            self._renderer = Renderer()
            framebuffer_size = glfw.get_framebuffer_size(window)
            self._renderer.resize(*framebuffer_size)
            glfw.set_framebuffer_size_callback(window, self._on_framebuffer_resize)
        except Exception:
            self.close()
            raise

    @property
    def is_running(self) -> bool:
        window = self._require_window()
        return not glfw.window_should_close(window)

    def process_events(self) -> None:
        glfw.poll_events()

    def render(self, scene: Scene) -> None:
        window = self._require_window()
        renderer = self._require_renderer()

        if not renderer.render(scene):
            return

        glfw.swap_buffers(window)

        if not self._visible:
            glfw.show_window(window)
            self._visible = True

    def close(self) -> None:
        if self._closed:
            return

        self._closed = True

        try:
            if self._renderer is not None:
                self._renderer.close()
        finally:
            if self._window is not None:
                glfw.destroy_window(self._window)

            glfw.terminate()

    def _on_framebuffer_resize(self, _window: object, width: int, height: int) -> None:
        renderer = self._renderer

        if renderer is not None:
            renderer.resize(width, height)

    def _require_window(self):
        if self._window is None:
            raise RuntimeError("Runtime window is not available")

        return self._window

    def _require_renderer(self) -> Renderer:
        if self._renderer is None:
            raise RuntimeError("Runtime renderer is not available")

        return self._renderer
