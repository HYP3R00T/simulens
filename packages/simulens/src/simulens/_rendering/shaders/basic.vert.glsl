#version 330 core

uniform mat3 projection;

in vec2 position;

void main() {
    vec3 projected = projection * vec3(position, 1.0);
    gl_Position = vec4(projected.xy, 0.0, 1.0);
}
