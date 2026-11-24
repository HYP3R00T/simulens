# MVP target

Status: proposed implementation target; not part of the public documentation.

## Goal

The first Simulens milestone should prove the complete authoring loop:

1. create a scene with reusable visual nodes;
2. arrange and animate those nodes;
3. animate a controllable camera;
4. import voiceover audio into a lightweight editor;
5. align named cues against its waveform;
6. preview, seek, and export the same deterministic result.

The MVP should be useful for polished 2D explanatory animation. Its spatial and
rendering contracts must permit basic 3D to be added without replacing the
scene graph, transform, camera, timeline, or editor models.

"No future refactoring" is not realistic. The design objective is that future
work extends stable boundaries instead of replacing them.

## Explicit scope

### Included

- Python scene authoring;
- hierarchical nodes with local transforms;
- groups and reusable custom nodes;
- essential 2D vector shapes and text;
- layout containers;
- orthographic camera movement and zoom;
- property animation, easing, sequencing, and parallel playback;
- fixed waits and named timeline cues;
- audio import, waveform, playback, scrubbing, and offset;
- a minimal timeline editor;
- interactive preview and headless image/video export;
- deterministic frame evaluation and automated visual tests.

### Deferred

- 3D geometry rendering beyond foundation-level contracts;
- physics solvers;
- circuits and optics;
- a complete visual scene editor;
- keyframe curve editing;
- photorealistic rendering;
- production-grade asset management;
- plugin discovery and a public compatibility promise.

Physics and 3D remain product requirements. They are deferred implementation,
not deferred architectural considerations.

## Naming and ownership

### `Scene`

`Scene` is the authored presentation unit. It owns:

- one root `View`;
- a default camera and optional additional cameras;
- one deterministic timeline;
- references to audio tracks and cue metadata;
- bindings to zero or more simulation worlds.

`Scene` is not itself a node.

### `View`

`View` is the root node of the visible scene tree. It represents the root
coordinate space and child hierarchy.

Use `View`, rather than `Canvas` or `World`, because:

- a canvas is an output surface or render target;
- a world is reserved for simulation state;
- the same view can be rendered through multiple cameras to multiple targets.

`scene.add(node)` is a convenience that delegates to `scene.view.add(node)`.

### `Node`

`Node` is the universal parent for entities placed in the scene tree. It works
for 2D and 3D because it owns dimension-capable spatial state rather than
dimension-specific geometry.

Minimum responsibilities:

- stable identity and optional user key;
- one parent and ordered children;
- 3D-capable local transform and computed world transform;
- visibility, opacity, and local ordering;
- attachment, detachment, and disposal lifecycle;
- change version and dirty propagation;
- traversal and reparenting operations;
- inspection metadata and bounds capability.

`Node` does not own OpenGL resources, shape geometry, fill/stroke rules, physics,
or timeline implementation.

## Scene hierarchy

```text
Scene
├── Timeline
├── Cameras
├── Audio tracks
├── Cue metadata
└── View (root Node)
    ├── Group
    │   └── other Nodes
    ├── Layout
    │   └── other Nodes
    ├── Shape2D
    ├── Text
    └── Camera
```

Tree rules:

- a node has at most one parent;
- adding an attached node reparents it;
- cycles are rejected before mutation;
- removing a node detaches it without disposing it;
- detached nodes remain valid;
- parent transforms never rewrite child-local geometry;
- insertion order is stable and breaks equal z-index ties;
- subtree opacity and effects apply through explicit compositing.

## Geometry hierarchy

Use inheritance for shared representation and durable behavior, not for every
mathematical classification.

```text
Node
├── Group
├── Layout
├── Shape2D
│   └── Path2D
│       ├── Polygon
│       ├── Rectangle
│       │   └── Square               optional convenience type
│       ├── Ellipse
│       │   └── Circle               optional convenience type
│       └── Line
├── Text
├── Image
├── Camera
│   ├── OrthographicCamera
│   └── PerspectiveCamera            post-MVP
└── Mesh3D                           post-MVP
```

Do not create a deep taxonomy such as `Quadrilateral -> Rectangle -> Square`
unless `Quadrilateral` introduces behavior used by multiple implementations.
Mathematical classification alone is not a software abstraction.

Prefer parameterized geometry and named constructors:

```python
Polygon(points=[...])
Polygon.regular(sides=5, radius=1)
Triangle.equilateral(side=2)  # convenience constructor or type
Triangle.right(a=3, b=4)  # convenience constructor or type
```

Specialized types are justified when they preserve a meaningful invariant or
provide unique operations. For example, a `Square` must prevent independent
width and height changes from silently breaking its square invariant.

### MVP geometry

- `Path2D` with move, line, quadratic/cubic curve, and close commands;
- `Line` or polyline;
- `Polygon`, including regular polygon construction;
- `Rectangle`, including optional corner radius;
- `Ellipse` and `Circle`;
- fill, stroke, opacity, and anti-aliasing;
- local bounds and hit testing;
- `Text` with dependable measurement and alignment.

Triangle, square, and other named shapes can be introduced as lightweight
constructors once the underlying path and property rules are stable.

## Layout

Canvas Commons demonstrates that layout materially improves animation
authoring. Simulens should adopt the capability without making every shape a
layout object.

`Layout` is a container node that arranges children implementing a bounds
contract. Initial modes:

- row;
- column;
- stack/overlay;
- grid after row and column are stable.

Initial properties:

- width and height: fixed, content-sized, or percentage of parent;
- minimum and maximum size;
- padding, gap, and margin or child spacing;
- main-axis justification;
- cross-axis alignment;
- child grow, shrink, and basis;
- optional clipping;
- animated layout changes.

Layout is initially two-dimensional and operates in its local plane. It may
contain projected or overlay representations of 3D content, but automatic 3D
layout is outside the MVP.

The layout engine should be behind a protocol. Whether it is implemented in
Simulens or adapted from an external engine must not affect node ownership or
public layout semantics.

## Camera

Camera design is part of the foundation, not an editor afterthought.

`Camera` is a node so its position and orientation can be parented, targeted,
inspected, and animated. Projection is a separate camera capability.

### MVP `OrthographicCamera`

- 3D position and orientation;
- orthographic visible height or explicit bounds;
- aspect-ratio-aware width;
- pan, zoom, rotate, and `look_at` helpers;
- animated transform and projection properties;
- world-to-screen and screen-to-world conversion;
- viewport and render-target association;
- layer/visibility filtering;
- predictable resizing policy.

A 2D scene uses an orthographic camera facing the XY plane. The camera remains
3D-capable, so tilting it or replacing it with a perspective projection later
does not require a new scene model.

### Post-MVP camera capabilities

- `PerspectiveCamera`;
- orbit, track, dolly, and follow rigs;
- multiple simultaneous camera views;
- depth-aware focus and picking;
- camera output used as a texture or masked layer.

Editor camera controls are adapters that manipulate camera properties. They
must not contain camera state unavailable to authored animations.

## Animation and timeline

The MVP needs a deterministic timeline before it needs a large animation
catalogue.

Required primitives:

- absolute project time represented without accumulated frame-delta drift;
- animatable typed properties;
- interpolation and easing;
- sequential and parallel composition;
- fixed-duration wait;
- named `wait_until` cue;
- animation fitted to a named cue;
- deterministic seek and replay;
- stable behavior at different preview and export frame rates.

Desired authoring direction:

```python
class Intro(Scene):
    def build(self) -> None:
        card = Group()
        box = card.add(Rectangle(width=4, height=2, fill=BLUE))
        title = card.add(Text("Gravity"))
        self.add(card)

        self.play(card.opacity.to(1, duration=0.4))
        self.wait_until("title-voiceover-end")
        self.play(
            self.camera.position.to((2, 1, 8)),
            self.camera.zoom.to(1.5),
        )
```

The exact property syntax needs a prototype. The semantics above are the MVP
contract.

## Minimal editor

The first editor is a synchronized authoring shell, not a complete scene
designer.

Required panels:

- render preview;
- play, pause, frame-step, and seek controls;
- bottom timeline with time ruler and playhead;
- audio track with waveform;
- named cue track;
- scene and render diagnostics.

Required actions:

- drop or select an audio file;
- move and trim the audio track;
- add, rename, move, and remove cues;
- choose ripple or preserve-time cue movement;
- scrub audio and animation together;
- jump from a cue to its source location when available;
- reload scene code while retaining audio and cue metadata;
- launch preview and export using the same evaluated scene.

Node-tree inspection, property editing, camera gizmos, and curve editors are
valuable follow-up features but not necessary to prove the voiceover workflow.

Audio and cue timestamps live in project sidecar metadata. The editor modifies
metadata, not Python source.

## Rendering and export

The MVP renderer should consume backend-neutral render descriptions rather than
checking each concrete node type itself.

Required pipeline:

```text
Scene evaluation
      ↓
ordered render descriptions
      ↓
render registry and resource manager
      ↓
OpenGL passes
      ↓
window or off-screen framebuffer
      ↓
preview, image, or video sink
```

Minimum guarantees:

- interactive and headless contexts produce equivalent frames;
- GPU resources have deterministic owners and cleanup;
- resizing and high-DPI output are handled explicitly;
- color and alpha conventions are documented;
- static geometry and text resources are cached;
- export does not depend on real-time playback speed;
- audio is muxed from timeline metadata during final video export.

Masks and arbitrary post-processing do not need to ship in the first vertical
slice, but the render-pass boundary must be capable of adding them next.

## Delivery sequence

### M0: contracts

- settle `Scene`, `View`, `Node`, transform, bounds, camera, and timeline
  semantics;
- write lifecycle, hierarchy, transform, and deterministic-time tests;
- define public versus internal modules.

### M1: visual vertical slice

- strict node tree and persistent transforms;
- orthographic camera;
- renderer registry and resource ownership;
- rectangle, circle, polygon/path, group, and text;
- window and headless still rendering;
- golden-image reference scene.

### M2: animation vertical slice

- animatable properties and timeline evaluation;
- easing, sequential/parallel composition, waits, and camera animation;
- deterministic seek and frame-sequence export;
- timeline-focused tests.

### M3: voiceover vertical slice

- minimal editor shell;
- audio import and waveform;
- synchronized playback and scrubbing;
- named cues, `wait_until`, and cue-fitted animation;
- persisted sidecar metadata;
- video export with audio.

### M4: foundation release

- layout row, column, stack, grow, shrink, gap, padding, and alignment;
- error reporting and diagnostics;
- complete example project using camera motion and voiceover cues;
- performance baselines, documentation, packaging, and CI hardening.

### Next after MVP

- render graph, masks, layers, effects, and multiple cameras;
- perspective camera, meshes, basic lighting, axes, curves, and surfaces;
- mechanics world prototype using fixed-step snapshots and scene bindings.

## MVP acceptance scenario

One reference project should demonstrate the complete result:

1. drop a voiceover into the editor;
2. create and drag named cues against visible waveform phrases;
3. render a responsive layout containing text, rectangles, circles, and a plot;
4. animate nodes and the orthographic camera;
5. hold completed animation states until voiceover cues;
6. scrub repeatedly to identical frames;
7. export a video whose audio and visual cues remain synchronized;
8. run the same project headlessly in continuous integration.

The MVP is complete when this workflow is dependable, not when the catalogue
contains every desired shape or simulation.
