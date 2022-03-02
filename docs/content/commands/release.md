# Release

The `slam release` command updates references to the version number in `pyproject.toml` and your source code, updates
the unreleased changelog if you make use of Slam's structured changelogs, as well as updating any other versions
specified in the configuration or detected by other plugins.

It covers the following use cases:

1. Bump the version number (and various features around that event)
2. Validate that the version number is consistent across the project

__Example__

    $ slam release patch --tag --push
    bumping 2 version references:
      pyproject.toml: 0.1.0 → 0.1.1
      src/my_package/__init__.py: 0.1.0 → 0.1.1

    release staged changelog
      .changelog/_unreleased.toml → .changelog/0.1.0.toml

    tagging 0.1.1
    [develop] ec1e9b3] release 0.1.0
    3 files changed, 3 insertions(+), 4 deletions(-)
    rename .changelog/{_unreleased.yml => 0.1.0.yml} (78%)

    pushing develop, 0.1.1 to origin
    Enumerating objects: 24, done.
    Counting objects: 100% (24/24), done.
    Delta compression using up to 8 threads
    Compressing objects: 100% (17/17), done.
    Writing objects: 100% (24/24), 3.87 KiB | 566.00 KiB/s, done.
    Total 24 (delta 4), reused 0 (delta 0)
    To https://github.com/username/repo
    * [new branch]      develop -> develop
    * [new tag]         0.1.1 -> 0.1.1

## Configuration

### `release.branch`

__Type__: `str`  
__Default__: `"develop"`

The branch on which releases are created. Unless `--no-branch-check` is passed to `slam release`, the command will
refuse to continue if the current branch name does not match this value.

### `release.commit-message`

__Type__: `str`  
__Default__: `"release {version}"`

The commit message to use when using the `--tag, -t` option. The string `{version}` will be replaced with the new
version number.

### `release.tag-name`

__Type__: `str`  
__Default__: `"{version}"`

The tag name to use when using the `--tag, -t` option. The string `{version}` will be replaced with the new
version number.

### `release.references`

__Type__: `list[VersionRefConfig]`  
__Default__: `[]`

A list of version references that should be considered in addition to the version references that are automatically
detected by Slam when updating version numbers across the project with the `slam release` command.

A `VersionRefConfig` contains the fields `file: str` and `pattern: str`. The `file` is considered relative to the
project directory (which is the directory where the `slam.toml` or `pyproject.toml` configuration file resides).