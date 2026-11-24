# Spatial and simulation model

Status: internal design direction; not part of the public documentation.

## Decision

Simulens should support 2D and 3D from one spatial foundation. It should also
support multiple physics and mathematical domains through independent solver
packages connected to the scene graph by explicit bindings.

This is ambitious but realistic if the scope is incremental. Building a useful
mechanics, circuits, and optics platform is feasible. Building a universally
accurate substitute for specialist scientific software is not the goal.

## Lessons from Manim Community

Manim already provides a broad mathematical visual vocabulary:

- number lines, 2D axes, 3D axes, polar and complex planes;
- explicit, parametric, and implicit functions;
- plots, areas, coordinate labels, charts, and sample spaces;
- vector fields, streamlines, surfaces, meshes, and point clouds;
- spheres, cubes, prisms, cones, cylinders, polyhedra, and 3D arrows;
- movable 3D cameras and fixed-orientation or fixed-in-frame overlays.

These are valuable product and API references. They are mostly visual
constructions, however. A sphere has geometry and appearance but does not imply
mass, velocity, collision, or gravity. A plotted circuit symbol does not imply
an electrical component model.

Simulens should preserve this distinction: visual primitives explain state;
domain models calculate state.

## Spatial foundation

### Build the base model in 3D

Every node should use a spatial transform capable of representing:

- 3D position;
- quaternion or equivalent 3D rotation;
- non-uniform 3D scale;
- parent-relative and world transforms;
- stable composition and inversion.

Two-dimensional objects live in a plane, normally `z = 0`, and receive friendly
2D accessors for `(x, y)`, width, height, and rotation about the plane normal.
A 2D scene is an orthographic camera looking at that plane, not a separate
incompatible universe.

Doing this now avoids replacing every transform, camera, bounds, picking, and
animation API when 3D arrives.

### Cameras

The shared camera contract should define:

- transform or look-at target;
- orthographic or perspective projection;
- viewport and render target;
- near and far clipping planes;
- layer or visibility filtering;
- conversion among world, view, clip, and screen coordinates.

`Camera2D` can be an orthographic specialization. `Camera3D` adds perspective
defaults and 3D navigation. Both produce the same lower-level camera data for
the renderer.

### Minimum 3D rendering scope

The initial 3D renderer needs:

- depth buffering and depth-aware picking;
- triangles, lines, points, and instancing;
- mesh positions, indices, normals, colors, and scalar/vector attributes;
- simple unlit and lit materials;
- directional, point, and ambient lighting sufficient for explanation;
- opaque and deliberately constrained transparent rendering;
- 2D text and annotation overlays attached to 3D positions;
- render targets, masks, layers, and multiple cameras.

It does not initially need photorealistic materials, sculpting, rigging,
production asset editing, or Blender-compatible scene authoring.

### Mathematical visual layer

Mathematical objects should be data-driven visual nodes or builders:

- `NumberLine`, `Axes2D`, `Axes3D`, `PolarAxes`, and `ComplexPlane`;
- function plots and sampled data plots;
- parametric curves and surfaces;
- implicit curves and surfaces;
- vector and scalar fields;
- grids, streamlines, contours, and volume slices;
- labels, braces, measurements, projections, and annotations.

Sampling, discontinuity handling, adaptive resolution, and coordinate mapping
belong in reusable math utilities. Rendering consumes the generated paths,
meshes, points, or field data.

## Simulation architecture

### Do not put physics into `Node`

A visual node must not automatically become a physical body. Many visuals are
annotations, trails, labels, graphs, or alternate views of the same simulated
entity. Conversely, a simulation may run without rendering.

Use two cooperating graphs:

```text
simulation world                    visual scene tree
----------------                    -----------------
state + domain models  ─binding─>   nodes + appearance
systems + solvers                   cameras + composition
fixed simulation clock              render evaluation
```

A binding maps selected simulation output to one or more animatable visual
properties. It must not make the solver depend on rendering classes.

### Shared simulation contract

Domain worlds should share a small lifecycle rather than one universal data
model:

```python
class SimulationWorld(Protocol):
    def reset(self, seed: int) -> None: ...
    def step(self, dt: float) -> None: ...
    def snapshot(self) -> Snapshot: ...
    def restore(self, snapshot: Snapshot) -> None: ...
```

Each domain owns its meaningful entities, state, systems, constraints, and
solvers. Cross-domain coupling must be explicit through adapters or exchanged
signals, not accidental access to internal arrays.

### Mechanics

A mechanics world may contain:

- particles and rigid bodies in 2D or 3D;
- shape-independent mass, inertia, pose, velocity, and force state;
- colliders separated from rendered geometry;
- broad-phase and narrow-phase collision detection;
- contact constraints and collision response;
- force fields and body forces;
- joints and other constraints;
- selectable numerical integrators.

The desired "layers" translate into different concepts:

- uniform gravity is a force field;
- mutual Newtonian gravity is a body-to-body force system;
- drag and damping are force or integration systems;
- collision detection and contact solving are systems;
- coefficient of restitution and friction are contact-material properties;
- a circle or sphere is a collider shape, independent of its visual style.

Example direction:

```python
world = MechanicsWorld2D(
    systems=[
        NewtonianGravity(gravitational_constant=1.0),
        CollisionSystem(),
    ],
)

body = world.add(
    RigidBody2D(
        mass=2.0,
        collider=CircleCollider(radius=0.5),
        material=ContactMaterial(restitution=0.7),
    )
)

node = scene.add(Circle(radius=0.5))
scene.bind(node.position, body.position)
```

This composition is flexible without pretending all behaviors are equivalent
stackable effects.

### Circuits

Circuits require a network model rather than spatial mechanics:

- electrical nodes and terminals;
- wires and topology;
- resistors, capacitors, inductors, sources, diodes, and transistors;
- component parameters and nonlinear equations;
- DC operating-point, transient, and later AC analysis;
- solver diagnostics for singular or non-convergent systems.

The visual circuit diagram binds to the electrical network but remains
independent. Current arrows, voltage colors, plots, annotations, and component
state can all be alternate presentations of the same solver output.

Start with a small validated component set. A diode animation should be able to
choose between an ideal educational model and a documented nonlinear model;
"proper physics" must always identify the assumptions being used.

### Optics

Optics should begin with geometric optics:

- rays and ray bundles;
- reflective and refractive interfaces;
- mirrors and thin lenses;
- media with refractive indices;
- intersections, normals, Snell's law, and total internal reflection;
- detectors or image planes.

Wave optics, interference, diffraction, polarization, and full electromagnetic
simulation are separate later models. They should not be approximated silently
by the ray solver.

### Other domains

The same boundary permits later packages for orbital mechanics, electromagnetism,
waves, fluids, thermodynamics, control systems, or statistics. Inclusion should
depend on a well-defined model, validation strategy, and compelling visual use
cases—not on placing every scientific feature in the core package.

## Time, playback, and seeking

Simulation time, animation time, and audio time share one project timeline but
have different evaluation rules.

- Rendering evaluates at requested presentation timestamps.
- Deterministic mechanics normally advances with a fixed simulation step.
- Visual frames may interpolate between simulation snapshots.
- Expensive worlds periodically checkpoint state for responsive seeking.
- Replaying from a checkpoint with identical inputs must reproduce the result.
- Timeline cues such as `wait_until` control presentation, not solver physics.
- Changing an audio cue must not change physical results at an earlier time.

Interactive real-time mode may fall behind; offline export must never vary its
physics step merely to finish a frame faster.

## Numerical and scientific reliability

Each simulation feature needs more than visual tests.

### General requirements

- declared coordinate, time, and unit conventions;
- deterministic seeds and stable stepping rules;
- documented solver assumptions and ranges of validity;
- explicit tolerances and failure diagnostics;
- float64 simulation state where numerical behavior requires it;
- float32 conversion only at the rendering boundary when appropriate;
- reference examples and performance benchmarks.

### Mechanics validation

- constant-acceleration trajectories;
- two-body momentum conservation;
- elastic and inelastic collision outcomes;
- orbital behavior and bounded energy error;
- friction, constraints, and resting-contact stability;
- results independent of render frame rate.

### Circuit validation

- Ohm's law and Kirchhoff-law networks;
- RC and RL transient responses;
- diode operating points against known reference values;
- conservation and convergence diagnostics;
- timestep convergence for transient analysis.

### Optics validation

- reflection and Snell-law angles;
- critical-angle and total-internal-reflection cases;
- thin-lens equation and focal intersections;
- consistent behavior under world transforms;
- robust handling of grazing and degenerate intersections.

## Package boundaries

The initial repository can remain one distribution while enforcing internal
boundaries resembling:

```text
simulens.scene          node tree, transforms, cameras, bindings
simulens.animation      timeline, interpolation, cues
simulens.rendering      render descriptions, graph, backend contracts
simulens.math           coordinates, sampling, plots, fields
simulens.simulation     shared world lifecycle and snapshots
simulens.mechanics      mechanics entities, systems, and solvers
simulens.circuits       network and component solvers
simulens.optics         optical models and solvers
```

Domains can become separate installable packages if dependency weight or release
cadence later demands it. Core scene and renderer code must not import domain
implementations.

## Staged delivery

1. Establish 3D transforms, bounds, cameras, and render descriptions while the
   visible feature set is still small.
2. Deliver strong 2D primitives using the shared spatial model.
3. Add minimal 3D meshes, depth, camera control, and mathematical axes/surfaces.
4. Build deterministic simulation stepping, snapshots, checkpoints, and scene
   bindings.
5. Validate a small 2D mechanics package: particles, circles, gravity, contacts,
   and restitution.
6. Generalize proven mechanics contracts to 3D without forcing circuits or
   optics into them.
7. Add small, separately validated circuit and geometric-optics packages.
8. Expand domain features only through reference use cases and tests.

This sequence lays scalable boundaries without attempting to implement the full
feature catalogue at once.
