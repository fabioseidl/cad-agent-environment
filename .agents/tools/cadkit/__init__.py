"""cadkit - repeatable build123d operations for agent-driven CAD projects.

The package is intentionally dependency-light on top of build123d so it can run
inside the CAD container (see docker/Dockerfile) or in a local virtualenv.

Entry point: ``python -m cadkit.cli`` (wrapped by ``.agents/tools/cad``).
"""

__version__ = "0.1.0"
