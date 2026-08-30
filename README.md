<div align="center">
<h1>Simulens</h1>
<p>
	<a href="https://hyp3r00t.github.io/simulens/">
		<img alt="Docs" src="https://img.shields.io/badge/docs-online-0A66C2?style=for-the-badge" />
	</a>
	<a href="https://github.com/sponsors/HYP3R00T">
		<img alt="Sponsor" src="https://img.shields.io/badge/sponsor-GitHub-EA4AAA?style=for-the-badge&logo=githubsponsors&logoColor=white" />
	</a>
	<a href="LICENSE">
		<img alt="License" src="https://img.shields.io/badge/license-MIT-1F883D?style=for-the-badge" />
	</a>
</p>

<p>Simulens is a programmable simulation and visualization toolkit for translating mathematical and physical models into interactive visual experiences. It separates simulation state from rendering, providing reusable representations for particles, paths, meshes, fields, and other scientific data. Simulens uses Python for modelling and orchestration, with ModernGL and GLSL providing GPU-accelerated rendering.</p>

</div>

## Features

- 🌍 Platform-independent development with Dev Containers
- 🧩 Host isolation: no local Python/toolchain setup required
- ⚙️ Auto bootstrap on container create (`scripts/setup.sh`)
- 🛠️ Runtime + task management with `mise`
- ⚡ Fast Python workflow with `uv`, `ruff`, `ty`, and `pytest`
- ✅ CI quality gates (lint, format, type checks, tests, coverage)
- 🔒 Pre-commit + commit-msg hooks with Conventional Commit support
- 🔁 Dependabot automation for dependencies and GitHub Actions
- 🤖 AI-agent-ready guidance via `AGENTS.md` and repo skills
- 📚 Docs pipeline with `zensical` + GitHub Pages deploy

## Quick Start (Dev Container)

Prerequisites: Docker + VS Code with the Dev Containers extension.

```bash
# Clone the template
git clone https://github.com/HYP3R00T/simulens.git

# Enter the project folder
cd simulens

# Open in VS Code
code .
```

Then run: `Dev Containers: Reopen in Container` from the VS Code Command Palette.
