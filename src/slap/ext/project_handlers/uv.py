"""Project handler for projects using the Poetry build system."""

from __future__ import annotations

import logging
import typing as t

from slap.ext.project_handlers.base import PyprojectHandler
from slap.project import Dependencies, Project
from slap.python.dependency import VersionSpec

if t.TYPE_CHECKING:
    from slap.python.dependency import Dependency

logger = logging.getLogger(__name__)


class UvProjectHandler(PyprojectHandler):
    # ProjectHandlerPlugin

    def matches_project(self, project: Project) -> bool:
        if not project.pyproject_toml.exists():
            return False
        if (project.directory / "uv.lock").exists():
            return True
        if project.pyproject_toml.get("tool", {}).get("uv") is not None:
            return True
        return False

    def get_dist_name(self, project: Project) -> str | None:
        return project.pyproject_toml.get("project", {}).get("name")

    def get_readme(self, project: Project) -> str | None:
        return project.pyproject_toml.get("project", {}).get("readme") or super().get_readme(project)

    def get_dependencies(self, project: Project) -> Dependencies:
        from slap.install.installer import Indexes
        from slap.python.dependency import PypiDependency, parse_dependencies

        python_version = project.pyproject_toml.get("project", {}).get("python")
        dependencies = parse_dependencies(project.pyproject_toml.get("project", {}).get("dependencies", []))
        dev_dependencies = parse_dependencies(
            project.pyproject_toml.get("tool", {}).get("uv", {}).get("dev-dependencies", [])
        )

        # TODO: Support index-url / extra-index-urls options.
        # TODO: Support dependency groups.

        return Dependencies(
            python=VersionSpec(python_version) if python_version else None,
            run=dependencies,
            dev=dev_dependencies,
            extra={},
            build=PypiDependency.parse_list(project.pyproject_toml.get("build-system", {}).get("requires", [])),
            indexes=Indexes(),
        )

    def get_add_dependency_toml_location_and_config(
        self,
        project: Project,
        dependency: Dependency,
        where: str,
    ) -> tuple[list[str], list | dict]:
        raise NotImplementedError("Uv project handler does not support adding dependencies")
