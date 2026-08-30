from array import array
from importlib.resources import files
from typing import cast

import moderngl

from ..scene import Scene
from ..shapes import Triangle


class Renderer:
    def __init__(self) -> None:
        self._context = moderngl.create_context(require=330)

        shader_directory = files("simulens._rendering").joinpath("shaders")
        vertex_shader = shader_directory.joinpath("basic.vert.glsl").read_text()
        fragment_shader = shader_directory.joinpath("basic.frag.glsl").read_text()

        self._program = self._context.program(
            vertex_shader=vertex_shader,
            fragment_shader=fragment_shader,
        )
        self._fill_color = cast(moderngl.Uniform, self._program["fill_color"])
        self._projection = cast(moderngl.Uniform, self._program["projection"])
        self._triangle_resources: dict[
            Triangle,
            tuple[moderngl.Buffer, moderngl.VertexArray],
        ] = {}

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
        self._update_projection(scene, width, height)

        for node in scene.nodes:
            if isinstance(node, Triangle):
                self._draw_triangle(node)
                continue

            raise TypeError(f"Unsupported scene node: {type(node).__name__}")

        return True

    def _draw_triangle(self, triangle: Triangle) -> None:
        resources = self._triangle_resources.get(triangle)

        if resources is None:
            coordinates = array(
                "f",
                (coordinate for vertex in triangle.vertices for coordinate in vertex),
            )
            vertex_buffer = self._context.buffer(coordinates.tobytes())
            vertex_array = self._context.vertex_array(
                self._program,
                [(vertex_buffer, "2f", "position")],
            )
            resources = (vertex_buffer, vertex_array)
            self._triangle_resources[triangle] = resources

        _, vertex_array = resources
        self._fill_color.value = triangle.color
        vertex_array.render(mode=moderngl.TRIANGLES)

    def _update_projection(self, scene: Scene, width: int, height: int) -> None:
        camera = scene.camera
        aspect_ratio = width / height
        visible_width = camera.visible_height * aspect_ratio

        scale_x = 2.0 / visible_width
        scale_y = 2.0 / camera.visible_height
        center_x, center_y = camera.center

        projection = array(
            "f",
            [
                scale_x,
                0.0,
                0.0,
                0.0,
                scale_y,
                0.0,
                -center_x * scale_x,
                -center_y * scale_y,
                1.0,
            ],
        )
        self._projection.write(projection.tobytes())

    def close(self) -> None:
        if self._closed:
            return

        self._closed = True
        try:
            for vertex_buffer, vertex_array in self._triangle_resources.values():
                vertex_array.release()
                vertex_buffer.release()

            self._program.release()
        finally:
            self._context.release()
