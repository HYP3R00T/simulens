from simulens import Application, Scene

if __name__ == "__main__":
    app = Application()
    scene = Scene(
        background_color=(0.05, 0.10, 0.20, 1.0),
    )

    app.run(scene)
