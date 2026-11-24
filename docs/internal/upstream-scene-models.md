# Upstream scene-model study

Status: internal research note; not part of the public documentation.

## Scope

This study focuses on the author-facing object model: how visual entities are
created, attached, nested, controlled, animated, rendered, and extended. It does
not attempt to inventory every shape or effect.

Source snapshots inspected:

- [Manim Community](https://github.com/ManimCommunity/manim/tree/864704ac0ca70e6769e9fe7a4a57477e43c44d3a),
  version 0.21.0, commit `864704a` from 2026-09-04.
- [Canvas Commons](https://github.com/canvas-commons/canvas-commons/tree/b8793686125f2e8044292bd282712a6eed28404b),
  packages version 0.3.1, commit `b879368` from 2026-08-19.

## Summary

Manim Community has the better minimal Python authoring experience. Canvas
Commons has the stronger scene-tree, property, ownership, and inspection model.
Simulens should combine those strengths rather than reproduce either system.

The recommended direction is:

- a real, single-parent scene tree rooted at a `View`;
- a small Python `Node` base with identity, hierarchy, transform, visibility,
  opacity, ordering, and lifecycle;
- shallow semantic inheritance such as `Square -> Rectangle -> Shape2D -> Node`;
- capabilities and renderer registrations for behavior that does not represent
  an "is-a" relationship;
- animatable properties backed by explicit state/version tracking;
- a deterministic timeline that evaluates independently from rendering;
- scene traversal compiled into backend-neutral render commands;
- OpenGL-specific objects kept out of the public node hierarchy.

## Manim Community

### End-user model

A user subclasses `Scene`, implements `construct`, creates mutable `Mobject`
instances, and uses `add`, `remove`, and `play`:

```python
class Example(Scene):
    def construct(self):
        square = Square(fill_opacity=1)
        self.add(square)
        self.play(square.animate.shift(RIGHT).set_fill(BLUE))
```

`Scene` owns an ordered list of top-level mobjects. Addition order determines
background-to-foreground order unless z-index sorting changes it. Some
animations introduce their mobject automatically, so an explicit `add` is not
always required.

This API is concise, readable, and successful because users manipulate visible
objects directly. Rendering concepts rarely appear in ordinary scene code.

### Type hierarchy

The main 2D vector path is approximately:

```text
Mobject
└── VMobject
    └── Polygram
        └── Polygon
            └── Rectangle
                └── Square
```

Other branches include point-cloud, image, text, graph, and 3D mobjects. `Group`
extends `Mobject`, while `VGroup` extends `VMobject` and accepts only compatible
vector mobjects.

The base `Mobject` owns points, submobjects, updaters, style-related state, and a
large collection of geometry, layout, transform, traversal, animation, and
convenience methods. Concrete shapes construct or transform their point arrays.
For example, `Square` delegates to `Rectangle`, and `Rectangle` delegates to a
polygon before stretching its generated geometry to the requested dimensions.

### Containment semantics

`Mobject.add(child)` stores the child in `submobjects`. A child cannot be the
same object as its parent and duplicates within one parent's list are removed.
The hierarchy is recursively traversable through `get_family()`.

This is a containment collection rather than a strict scene graph:

- a mobject does not maintain a canonical parent link;
- single-parent ownership is not enforced;
- group transforms generally mutate descendant geometry instead of preserving
  a persistent local transform relative to a parent;
- the scene performs list restructuring when roots or descendants are added and
  removed;
- Cairo and OpenGL currently have documented differences in child insertion
  and deduplication behavior.

The model works well for mathematical transformations, but it makes reparenting,
editor inspection, inherited transforms, and render-layer composition harder to
define precisely.

### State and animation

Mobjects are mutable. Methods such as `shift`, `scale`, `rotate`, and `set_fill`
change the object and return it for fluent chaining.

`mobject.animate.method(...)` records method calls in an animation builder. At
playback, Manim creates starting copies and interpolates mobject families from
an animation progress value. Dedicated animation classes handle creation,
transformation, fading, indication, composition, and other behaviors.

Mobjects can also hold updater callbacks. They receive the object and optionally
frame delta time and run recursively through submobjects. This is flexible, but
delta-time mutation and animation-time copying complicate deterministic seeking
and can make ownership of state changes difficult to reason about.

### Rendering consequences

The scene coordinates animation and rendering. Cairo and OpenGL have separate
renderers, object paths, and compatibility machinery. The OpenGL renderer walks
scene mobjects, obtains shader wrappers from each object, and draws them with
camera uniforms. Cairo captures flattened mobject families and can cache static
content into a background image.

The backend split leaks into the model: renderer checks appear in scene
management, and plugins must account for incompatible base classes. Simulens
should avoid backend-specific node classes and metaclass-based conversion.

### What Simulens should learn from Manim

Adopt:

- direct Python objects and a small amount of scene ceremony;
- fluent mutation for immediate changes;
- `scene.add`, `scene.remove`, and `scene.play` vocabulary;
- useful semantic shape inheritance;
- reusable animation objects and composition helpers;
- rich geometry and positioning conveniences built above stable primitives.

Avoid:

- a base class that accumulates unrelated geometry and renderer behavior;
- geometry mutation as the only representation of transforms;
- ambiguous multi-parent containment;
- animation implemented primarily by deep-copying mutable object families;
- separate public object hierarchies for each rendering backend;
- scene logic branching repeatedly on the active renderer.

## Canvas Commons

### End-user model

A scene is defined with `makeScene2D` and a generator receiving its root view:

```typescript
export default makeScene2D(function* (view) {
  const rect = new Rect({width: 300, height: 200, fill: 'blue'});
  view.add(rect);
  yield* rect.position.x(300, 1);
});
```

The same nodes may be constructed with its custom JSX runtime:

```tsx
view.add(
  <Layout layout direction={'row'}>
    <Rect width={300} height={200} />
    <Circle size={200} />
  </Layout>,
);
```

JSX creates real node instances immediately. There is no virtual DOM or
reconciliation. The imperative constructor form and JSX form produce the same
tree.

### Type hierarchy

The main visual inheritance chain is:

```text
Node
└── Layout
    └── Shape
        └── Curve
            ├── Rect
            ├── Circle
            ├── Line
            └── Polygon
```

`View2D` extends `Rect` and is the root of every `Scene2D`. Media nodes reuse
shape behavior where useful: for example, `Img` and `Video` extend `Rect`.
`Camera` extends `Node` because it participates in transforms and hierarchy but
is not itself a shape.

This makes "every entity is a node" concrete. Shared transform and compositing
behavior comes from `Node`; layout comes from `Layout`; fill and stroke come
from `Shape`; curve profile behavior comes from `Curve`; `Rect` only supplies
rectangle-specific geometry.

The tradeoff is that inheritance becomes broad: every `Shape` is also a
`Layout` and consequently carries layout and text-style concerns. Simulens can
keep the useful semantic hierarchy without requiring every visual node to own
every optional capability.

### Ownership and hierarchy

Canvas Commons implements a true mutable tree:

- every node has one reactive `parent` reference;
- every node owns an ordered list of children;
- adding a node first removes it from its previous parent, then reparents it;
- removing a node detaches it from its parent;
- local-to-world matrices compose recursively through parents;
- children are drawn recursively and sorted by z-index;
- the API supports insertion, reparenting, sibling movement, traversal, and
  ancestor/descendant queries.

Nodes register with their active scene at construction and receive a stable key.
The scene tracks attached and detached nodes for inspection and disposal. This
is valuable for an editor, although Simulens should avoid requiring an ambient
"current scene" merely to construct a detached node.

### Signals and animation

Almost every node property is a signal. The same property object acts as:

- getter: `rect.opacity()`;
- setter: `rect.opacity(0.5)`;
- tween factory: `rect.opacity(1, 0.5)`;
- reactive binding: a function whose dependencies are tracked automatically.

Computed signals are lazy, cached, and invalidated through dependency tracking.
Canvas Commons uses them for derived state including transformation matrices,
layout, paths, and cache bounds.

Generators express sequential time, while flow generators such as `all`,
`chain`, `delay`, and `sequence` compose concurrency. Scene recalculation
restarts the generator and advances it frame by frame, which supports preview
and seeking but tightly couples authoring semantics to generator replay.

Signals provide an excellent user experience, but a direct Python copy would be
unnatural: Python properties are not normally callable getter/setter/tween
objects. Simulens should copy the capability, not the TypeScript syntax.

### Audio and editable time events

Canvas Commons separates audio playback from synchronization cues. A project
may define a main audio track, and scenes may register additional sound clips.
The editor decodes these sources into waveform peak data and draws them on the
timeline. The main track can be offset by shift-dragging it; scene sounds carry
their own offset, trim, gain, and playback-rate data.

There are three related authoring operations:

```typescript
yield* waitFor(2);                 // fixed two-second delay
yield* waitUntil('sentence-end');  // delay to an editable named event
yield* circle.scale(2, useDuration('grow-end')); // fit work to a cue
```

`waitUntil` is implemented as `waitFor(useDuration(name))`. Registering the
event records the current thread time as its start and returns the non-negative
offset to its saved target time. The event target is stored separately in the
scene's `.meta` file, for example:

```json
{
  "name": "sentence-end",
  "targetTime": 4.82
}
```

In the editor, a cue appears at its target time with a trail back to the point
where code reached `waitUntil`. Dragging the cue reloads and recalculates the
scene. By default the edit ripples later cues; holding Shift preserves their
absolute positions. During final rendering, a read-only time-event manager uses
the saved targets, so synchronization does not depend on the editor being open.

This is the feature needed for voiceover-led animation. It is not automatic
speech-end detection: the author visually aligns named cues to the waveform.
The important abstraction is that code names narrative moments while the editor
owns their exact timestamps.

### Rendering and composition

Rendering is recursive:

1. a node saves the canvas context and applies its local transform;
2. it either draws directly or renders itself and its descendants into a cache;
3. opacity, filters, shadows, composite operations, and shaders may be applied
   to the cached result;
4. children render in ordered traversal;
5. the canvas context is restored.

`Layout` and `Shape` can clip their descendants. A composite node renders its
subtree as a unit, which makes subtree opacity, effects, caching, and shader
processing coherent. These are important precedents for Simulens' proposed
render graph, masks, and layers.

### Extensibility and tooling

Custom components subclass the closest semantic node and declare additional
signal-backed properties. They can create child nodes in their constructor and
expose generator methods for domain-specific animations.

Stable keys, registered properties, creation stacks, bounds, hit testing, and
overlays make the scene tree inspectable by the editor. These facilities were
designed into the node model rather than bolted onto rendering later.

### What Simulens should learn from Canvas Commons

Adopt:

- a root view and strict single-parent hierarchy;
- persistent local transforms composed through the tree;
- explicit reparenting and predictable child order;
- subtree compositing for masks, opacity, effects, and caching;
- stable optional keys and editor-friendly introspection metadata;
- dirty propagation for cached derived values;
- custom node construction through ordinary subclassing;
- lifecycle and resource cleanup independent of whether a node is attached.
- named, editor-adjustable time events stored outside source code;
- waveform-backed audio alignment with deterministic render-time playback;

Avoid:

- reliance on an ambient scene during node construction;
- making all shapes inherit the entire layout and text-style surface;
- requiring framework-specific decorators for every public property;
- encoding the only timeline model in replayed language generators;
- allowing rendering caches and canvas implementation details to define core
  scene semantics.

## Comparison

| Concern | Manim Community | Canvas Commons | Simulens direction |
| --- | --- | --- | --- |
| Scene root | ordered root list | explicit `View2D` root | explicit `View` with `Scene.add` convenience |
| Containment | recursive submobject lists | strict single-parent tree | strict single-parent tree |
| Transforms | commonly baked into geometry | persistent local matrices | persistent local transforms |
| Properties | mutable attributes and methods | reactive signals | typed animatable properties |
| Sequencing | `Scene.play` and animations | generators and flow helpers | deterministic timeline with `play` façade |
| Rendering | Cairo/OpenGL-aware model | recursive Canvas 2D rendering | backend-neutral render description and graph |
| Composition | renderer-specific/specialized | cached subtrees and compositing | first-class render layers and passes |
| Extensibility | subclass/plugin, renderer caveats | subclass plus registered signals | subclass/protocol plus renderer registry |
| Inspection | limited object identity tooling | stable keys and editor integration | stable IDs, metadata, bounds, hit testing |
| Voiceover sync | fixed waits or external helpers | waveform plus editable named events | first-class audio tracks and named cues |

## Recommended Simulens object model

### Semantic hierarchy

```text
Node
├── Group
├── Shape2D
│   ├── Path2D
│   ├── Rectangle
│   │   └── Square
│   ├── Ellipse
│   │   └── Circle
│   └── Line
├── Text
├── Image
├── Camera2D
├── Layer
└── Mask
```

Inheritance should express a durable "is-a" relationship only. Layout,
renderability, hit testing, effects, and animation are better represented by
small protocols or composed state where multiple unrelated node types need
them.

### Base `Node` responsibilities

`Node` should own only cross-cutting scene concerns:

- stable runtime identity and optional user key;
- one parent and ordered children;
- local transform and computed world transform;
- visibility, opacity, and local ordering;
- attachment/disposal lifecycle;
- change version and dirty propagation;
- traversal and reparenting operations;
- optional inspection metadata.

It should not own geometry buffers, fill/stroke details, OpenGL objects,
simulation integration, text layout, or every possible effect.

### Attachment rules

- A scene owns exactly one root `View`.
- `scene.add(node)` delegates to `scene.root.add(node)`.
- Adding an attached node reparents it; it never duplicates it.
- Cycles are rejected before mutation.
- Detached nodes are valid and may be created without a running application or
  renderer.
- Parent transforms affect descendants without modifying their local geometry.
- Removing detaches; disposing is a separate explicit lifecycle operation.
- Child ordering is stable; z-index resolves visually within a documented
  scope, with insertion order breaking ties.

### Proposed Python authoring shape

```python
class Example(Scene):
    def build(self) -> None:
        card = Group()
        box = card.add(Rectangle(width=4, height=2, fill=BLUE))
        label = card.add(Text("Energy"))
        self.add(card)

        self.play(
            card.position.to((3, 0), duration=1),
            box.opacity.to(0.5, duration=1),
        )
```

The exact property syntax remains a design decision. The required semantics are
more important:

- immediate assignment and timed animation are distinct and explicit;
- properties know how to validate and interpolate their values;
- animation evaluates from absolute timeline time;
- derived state can be invalidated without scanning the whole tree;
- author code remains ordinary, typed Python.

### Rendering boundary

Nodes should emit or be compiled into backend-neutral render data. A renderer
registry maps supported render data to backend implementations. Traversal should
produce an explicit render graph for layers, cameras, masks, and effects.

This prevents the current Simulens renderer from growing into a central chain of
concrete-type checks and prevents the Manim problem of renderer-specific public
object hierarchies.

### Voiceover synchronization

A suitable Python-facing design would preserve two distinct operations:

```python
self.play(reveal_title(), duration=0.6)
self.wait_until("title-narration-end")

self.play(
    explain_diagram(),
    until="diagram-narration-end",
)
```

The first animation always takes 0.6 seconds and then holds its completed state
until the named cue. The second animation is fitted to the interval from the
current timeline position to its cue. Once either operation completes, the next
statement proceeds normally.

The underlying design should include:

- one canonical project timeline shared by animation and audio;
- rational or integer-based media time rather than accumulated floating-point
  frame deltas;
- named cues with stable identity, display label, scope, and target time;
- cue times stored in sidecar project metadata, never rewritten into scene code;
- editor mode that creates missing cues at the current time;
- export validation for missing, duplicate, unreachable, or backwards cues;
- waveform rendering and synchronized seek/play/pause behavior;
- explicit ripple and preserve-time editing modes;
- deterministic recomputation after a cue or earlier duration changes.

Audio completion and cue completion should remain separate. A cue can align to
a word, pause, beat, or arbitrary editorial decision, not only to the physical
end of an audio file.

## Decisions this research supports

The following are sufficiently supported to become foundation decisions:

1. Use a strict scene tree rather than a flat scene list.
2. Give the scene an explicit root view.
3. Make all scene entities derive from `Node`.
4. Preserve local transforms instead of baking hierarchy transforms into
   geometry.
5. Separate detachment from disposal.
6. Keep nodes constructible without a window, renderer, or active scene.
7. Build stable IDs and inspection hooks into the foundation.
8. Make subtree composition a core render-graph operation.
9. Keep backend types below the public scene model.
10. Use semantic inheritance sparingly and capabilities for orthogonal behavior.
11. Treat audio, timeline cues, and animation evaluation as separate cooperating
    systems.

## Decisions still requiring prototypes

- Python syntax and implementation for animatable/reactive properties;
- whether `parent.add(child)` returns the parent, child, or a dedicated result;
- how simulation state binds to node properties without hidden mutation;
- render-description granularity and invalidation strategy;
- local z-index scope across nested compositing layers;
- whether masks are nodes, node relationships, render passes, or a combination;
- timeline serialization and seeking behavior;
- editor metadata cost when no editor is in use.
- cue metadata format, naming scope, and missing-cue export policy;
- Python syntax for waiting until a cue versus fitting an animation to one;
- ripple-edit behavior when earlier animation durations change.

These should be resolved with narrow prototypes before expanding the shape
catalogue.
