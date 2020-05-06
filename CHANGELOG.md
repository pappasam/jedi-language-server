# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## 0.12.3

### Removed

- Removed initialization message directly from the server. This should be handled and configured by LanguageClient plugins.

## 0.12.2

### Changed

- jedi completion `param` sorts first in COMPLETION. Resolves https://github.com/pappasam/jedi-language-server/issues/19

## 0.12.1

### Changed

- Removed `)` from signatureHelp triggerCharacters (now just `(` and `,`). Thanks to [rwols](https://github.com/rwols) in <https://github.com/pappasam/jedi-language-server/issues/15#issuecomment-623295867>!

## 0.12.0

### Changed

- Most registrations moved to `static` registrations
- Configuration options for `triggerCharacters` and other server-managed feature options were removed. See <https://github.com/pappasam/jedi-language-server/issues/15>
- Elegant solution overriding `bf_*` thanks to [harismandal](https://github.com/harismandal) and [muffinmad](https://github.com/muffinmad/anakin-language-server/blob/539fedc41c7263bb3cd95d1350b7f5cca7f97872/anakinls/server.py#L41-L50)

## 0.11.0

### Added

- hierarchicalDocumentSymbolSupport (eg, you get a nice outline when making a documentSymbol request). Conditionally provides this functionality based on whether your language client supports this.

## 0.10.2

### Changed

- Highlight function is now slightly less accurate but much faster. Since highlight is called repeatedly (like complete), its speed is much more important to its accuracy.

## 0.10.1

### Changed

- Jedi now ignores ".venv" for searches. The implementation is kind of a hack, but it solves my personal problem at the moment.

## 0.10.0

### Added

- Support `textDocument.documentHighlight`

## 0.9.0

### Added

- Support `textDocument.signatureHelp`

### Removed

- A bunch of `try/except Exception` blocks around Jedi calls. Hopefully those aren't still necessary on `jedi>=0.17`...

## 0.8.0

### Added

- Support Jedi-powered diagnostics

## 0.7.2

### Changed

- Server does not initialize non-initialization features if `"jedi.enabled": false`

## 0.7.1

### Changed

- `lookup_feature_id` initialized in `__init__`; no longer a class variable
- although tests are still mostly missing, `test_cli` now imports `cli`; helps determine if there are any runtime errors on import

## 0.7.0

### Added

- Support user-configuration rooted at `jedi`. Only 1 option for now: `jedi.completion.triggerCharacters`. Same defaults as version `0.6.1`.
- Message flashes after initialization.

### Changed

- `pygls` types now checked. Version `0.9.0` provides type-hint checking support.

## 0.6.1

### Changed

- Trigger characters are now: ", ', and . to account for dictionary completions

### Fixed

- Trigger characters finally work (use underscore in pygls decorator, not camel case...)
- Completion insert items now remove leading " and ' if preceding character is ' or "

## 0.6.0

### Added

- Re-added `workspace/symbol` support using Jedi's `Project` object. This is much simpler and faster than the previous implementation.

## 0.5.2

### Changed

- Implementation details involving `Projects` and `Scripts` were re-organized in preparation for the next minor release.

### Fixed

- Fixed `DOCUMENT_SYMBOL`. Line and row numbers were incorrectly passed to this argument before which silently broke this function. These incorrect arguments were removed.

## 0.5.1

### Changed

- Hover uses Jedi's `help` method, instead of `infer`. Provides better help message information.

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
