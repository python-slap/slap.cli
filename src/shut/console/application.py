
from lib2to3.refactor import get_all_fix_names
import typing as t
from pathlib import Path

from cleo.application import Application as _CleoApplication  # type: ignore[import]
from nr.util import Optional
from nr.util.algorithm.longest_common_substring import longest_common_substring
from nr.util.plugins import load_plugins

from shut import __version__
from shut.config.global_ import GlobalConfig
from shut.config.project import ProjectConfig
from shut.plugins.application_plugin import ApplicationPlugin, ENTRYPOINT as APPLICATION_PLUGIN_ENTRYPOINT
from shut.plugins.remote_plugin import RemotePlugin, detect_remote
from shut.plugins.plugin_registry import PluginRegistry
from shut.util.python_package import Package, detect_packages
from shut.util.fs import get_file_in_directory

__all__ = ['Application']

PYPROJECT_TOML = Path('pyproject.toml')
GLOBAL_CONFIG_TOML = Path('~/.config/shut/config.toml').expanduser()


class Application:
  """ The central management unit for the Shut CLI. """

  def __init__(self) -> None:
    self.cleo = _CleoApplication('shut', __version__)
    self._pyproject_cache: dict[str, t.Any] | None = None
    self._global_config_cache: dict[str, t.Any] | None = None
    self._remote: RemotePlugin | None = None
    self._registries: dict[str, PluginRegistry] = {}

  def registry(self, registry_id: str) -> PluginRegistry:
    return self._registries.setdefault(registry_id, PluginRegistry())

  def load_plugins(self) -> None:
    """ Load all #ApplicationPlugin#s and activate them. """

    for plugin in load_plugins(APPLICATION_PLUGIN_ENTRYPOINT, ApplicationPlugin).values():  # type: ignore[misc]  # https://github.com/python/mypy/issues/5374
      config = plugin.load_config(self)
      plugin.activate(self, config)

  def load_pyproject(self, force_reload: bool = False) -> dict[str, t.Any]:
    """ Load the `pyproject.toml` configuration in the current working directory and return it.

    If *force_reload* is `True`, the configuration will be reloaded instead of relying on the cache. """

    import tomli
    if self._pyproject_cache is None or force_reload:
      self._pyproject_cache = tomli.loads(PYPROJECT_TOML.read_text())
    return self._pyproject_cache

  def save_pyproject(self, data: dict[str, t.Any] | None = None) -> None:
    """ Save *data* to the `pyproject.toml` file.

    If *data* is `None`, the internal cache that is initialized with #load_pyproject() will be used. Note
    that this does preserve any style information or comments.

    :raise RuntimeError: If *data* is `None` and #load_pyproject() has not been called before. """

    import tomli_w
    if data is None:
      if self._pyproject_cache is None:
        raise RuntimeError('not internal cache')
      data = self._pyproject_cache
    PYPROJECT_TOML.write_text(tomli_w.dumps(data))

  def load_global_config(self) -> dict[str, t.Any]:
    """ Load the `~/.config/shut/config.toml` configuration file. """

    import tomli
    if self._global_config_cache is None and GLOBAL_CONFIG_TOML.is_file():
      self._global_config_cache =  tomli.loads(GLOBAL_CONFIG_TOML.read_text())
    elif self._global_config_cache is None:
      self._global_config_cache = {}
    return self._global_config_cache

  @property
  def project_config(self) -> ProjectConfig:
    import databind.json
    data = self.load_pyproject().get('tool', {}).get('shut', {})
    return databind.json.load(data, ProjectConfig)

  @property
  def global_config(self) -> GlobalConfig:
    import databind.json
    data = self.load_global_config()
    return databind.json.load(data, GlobalConfig)

  @property
  def remote(self) -> RemotePlugin | None:
    if self._remote is None:
      self._remote = self.project_config.remote or detect_remote(Path.cwd())
    return self._remote

  def get_packages(self) -> list[Package]:
    """ Tries to detect the packages in the project directory. Uses `tool.poetry.packages` if that configuration
    exists, otherwise it attempts to automatically determine it. The `tool.shut.source-directory` option is used
    if set, otherwise the `src/` directory or alternatively the project directory is used to detect the packages.
    """

    if (directory := Optional(self.project_config.source_directory).map(Path).or_else(None)):
      return detect_packages(Path(directory))

    for directory in [Path('src'), Path()]:
      packages = detect_packages(directory)
      if packages:
        break

    return packages

  def get_readme_path(self) -> Path | None:
    """ Tries to detect the project readme. If `tool.poetry.readme` is set, that file will be returned. """

    if (readme := self.load_pyproject().get('tool', {}).get('poetry', {}).get('readme')) and Path(readme).is_file():
      return Path(readme)

    return get_file_in_directory(Path.cwd(), 'README', ['README.md', 'README.rst'], case_sensitive=False)

  def __call__(self) -> None:
    self.load_plugins()
    self.cleo.run()


app = Application()
