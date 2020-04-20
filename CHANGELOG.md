# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## 0.5.0

### Added

- Support for Jedi `0.17`

### Changed

- Major internal updates to helper functions. Jedi `0.17` has a different public API.

### Removed

- Remove support for Workspace symbols. I never used this feature and I figure we can do this better with Jedi's new project constructs.
- Remove support for any version of Jedi before `0.17`. If you must use an older Jedi, stick to `0.4.2`.

## 0.4.2

### Changed

- Reformat this changelog with `prettier`.

### Fixed

- Jedi `0.17` introduces major public API breaking changes. Temporarily version constrain Jedi to `>=0.15.1,<0.17.0` to keep language server usable until we can address all public API changes in upstream Jedi. Version `0.5.0` will require Jedi `>=0.17.0`.

## 0.4.1

### Fixed

- docstring for `lsp_rename`
- `README` now provides clearer overview of supported features and usage.

## 0.4.0

### Added

- Support for `workspace/symbol`
  - NOTE: currently ignores the query. Maybe something worth considering the query in future.

### Fixed

- Document symbols are now properly mapped to jedi symbols. Before, I was incorrectly using the completion item mapping. I need to use the separate symbol mapping.

## 0.3.1

### Fixed

- Rename Jedi functionality is wrapped in `try/except`, increasing language server's resilience.

## 0.3.0

### Added

- This `CHANGELOG.md`
- Support for `textDocument/documentSymbol`

### Changed

- `locations_from_definitions` to `get_location_from_definition`. More generally useful.

### Fixed

- `mypy`, `pylint`, `black`, `toml-sort`, and `isort` all pass.
