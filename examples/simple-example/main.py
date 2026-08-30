from simulens import Application, Scene, Triangle

if __name__ == "__main__":
    app = Application()
    scene = Scene(
        background_color=(0.05, 0.10, 0.20, 1.0),
    )
    scene.add(
        Triangle(
            vertices=(
                (-0.5, -0.5),
                (0.5, -0.5),
                (0.0, 0.5),
            ),
            color=(0.2, 0.7, 1.0, 1.0),
        )
    )

    app.run(scene)
