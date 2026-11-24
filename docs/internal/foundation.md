# Simulens foundation

Status: working note; not part of the public documentation.

## Purpose

Simulens is a Python-first toolkit for building deterministic simulations and
turning them into interactive or rendered visual experiences. It should make
simple work easy without limiting advanced rendering, composition, or custom
simulation systems.

The public authoring experience is Python. GPU shaders and native libraries may
be used internally when they provide capabilities or performance that Python
cannot reasonably provide.

## Product boundaries

Simulens is:

- a reusable scene, animation, simulation, and rendering toolkit;
- suitable for interactive viewing and reproducible offline rendering;
- designed for mathematical, scientific, and explanatory visuals;
- dimension-aware at its foundation, with first-class 2D and 3D views;
- extensible through custom nodes, data sources, render passes, and effects;
- independent of any single windowing, export, or editor experience.

Simulens is not:

- a Manim fork or compatibility clone;
- a general-purpose game engine;
- a full video editor or 3D content-creation suite;
- a universal or authoritative solver for every scientific domain;
- a replacement for Blender, CAD, SPICE, or specialist research software;
- an editor-first system whose core depends on a GUI.

## Desired capabilities

### Foundation

- hierarchical scene graph with stable node identity;
- composable 3D transforms with ergonomic 2D projections and operations;
- cameras, layers, visibility, opacity, and ordering;
- deterministic clock, timeline, and frame evaluation;
- clear ownership and lifecycle of CPU and GPU resources;
- headless operation as well as an interactive window.

### Animation and simulation

- keyframes, interpolation, easing, and reusable animations;
- procedural per-frame updates without coupling them to rendering;
- fixed-step simulation with render interpolation where appropriate;
- pause, seek, replay, and exact frame rendering;
- named timeline cues that can be positioned against an audio waveform;
- cue-relative waits and animation durations without hard-coded timestamps;
- adapters for user-defined simulation state rather than a mandatory solver.

### Rendering and composition

- backend-independent render descriptions with an OpenGL backend first;
- render-to-texture and explicit render passes;
- hard, soft, animated, inverted, and nested masks;
- multiple cameras composited into one output;
- effects such as blur, bloom, and color processing;
- vector paths, text, images, meshes, particles, and scientific fields;
- orthographic and perspective cameras with depth-aware rendering;
- mathematical axes, plots, curves, surfaces, fields, and annotations;
- still-image, image-sequence, and video output.

### Simulation domains

- domain-specific worlds separated from the visual scene graph;
- mechanics systems for bodies, forces, contacts, constraints, and integrators;
- uniform and body-to-body gravity as distinct force models;
- material/contact properties such as friction and restitution;
- circuit graphs with component models and pluggable analysis solvers;
- geometric optics with rays, interfaces, mirrors, and lenses;
- explicit bindings that turn simulation state into visual node properties;
- checkpoints and deterministic replay for seeking and offline rendering.

### Audio and authoring

- project-level voiceover tracks and scene-level audio clips;
- waveform display, trimming, offset, gain, mute, and synchronized scrubbing;
- draggable named cues stored as project metadata rather than source constants;
- ripple and preserve-time editing modes for downstream cues;
- identical cue behavior in preview, headless rendering, and final export.

### Extensibility

- public protocols for custom nodes and renderable data;
- registered renderers instead of central `isinstance` dispatch;
- custom shader and render-pass support behind managed resource APIs;
- optional adapters for external tools, including Manim-derived geometry;
- a small, versioned public API with implementation details kept internal.

## Architectural rules

1. **State is not rendering.** Scene and simulation state must be usable without
   an OpenGL context.
2. **Simulation is not presentation.** Domain state and solvers must not depend
   on visual nodes; bindings adapt their outputs for display.
3. **Evaluation is deterministic.** A scene evaluated at the same time with the
   same inputs must produce the same render description.
4. **The renderer consumes data.** It must not contain product logic for every
   concrete node type.
5. **Composition is fundamental.** Cameras, masks, layers, and effects are render
   graph operations, not special-case drawing tricks.
6. **Capabilities are explicit.** Unsupported backend or hardware features fail
   clearly or use a documented fallback.
7. **Resources have owners.** Creation, caching, invalidation, and destruction of
   GPU resources must be predictable.
8. **Convenience builds on primitives.** High-level animation APIs compile into a
   small set of timeline and scene operations.
9. **Internal APIs may evolve.** Only intentionally public modules receive
   compatibility guarantees.

## Core model

The intended flow is:

```text
Python authoring API
        ↓
scene graph + simulation state
        ↓ evaluate(time)
immutable render description
        ↓
render graph and resource manager
        ↓
OpenGL backend
        ↓
window, image, or video sink
```

This boundary allows future rendering backends, headless tests, serialization,
and tooling without replacing the user-facing scene model.

## Reliability requirements

- unit tests for scene evaluation, transforms, timelines, and validation;
- deterministic tests that evaluate selected scenes at exact timestamps;
- golden-image tests with defined tolerance for rendering behavior;
- headless rendering in continuous integration;
- tests for context loss and resource cleanup;
- performance benchmarks for representative scene sizes;
- reference scenes covering text, paths, masks, cameras, effects, and simulation;
- timeline tests covering cues before, within, and after animations;
- audio synchronization tests at different frame and sample rates;
- analytical and invariant-based tests for each simulation domain;
- rendering tests for depth, camera projection, transparency, and 2D/3D mixing;
- documented capability and compatibility matrix.

Visual correctness, deterministic behavior, and resource safety are release
requirements rather than later optimization work.

## Initial implementation sequence

1. Define node identity, hierarchy, 3D transforms, and change tracking.
2. Define the clock, deterministic scene evaluation, and animation tracks.
3. Define named timeline cues and their editor-independent metadata model.
4. Replace concrete-type renderer dispatch with render descriptions and a
   renderer registry.
5. Add resource ownership, headless rendering, and image-based tests.
6. Introduce render targets and a minimal render graph.
7. Implement masks and multi-camera composition as the first proof of the render
   graph design.
8. Grow the shape, text, audio, effect, simulation, and export libraries
   incrementally.

## Deliberately deferred decisions

- final 3D scene and material model;
- specialist physics models beyond the validated initial domain subsets;
- scene serialization format;
- plugin discovery and packaging mechanism;
- GUI or visual editor architecture;
- additional rendering backends;
- direct Manim compatibility.

These should not be embedded into the first implementation, but the boundaries
above should allow them without replacing the core scene and timeline models.
