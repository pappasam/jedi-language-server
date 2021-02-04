# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## 0.23.1

### Fixed

- workspace/didChangeConfiguration option is now defined. It currently does nothing, but this resolves some feedback errors on some language clients. See <https://github.com/pappasam/jedi-language-server/issues/58>.

## 0.23.0

### Added

- Implemented `completionItem/resolve`; the Jedi completion data are held until the next `textDocument/completion` arrives
- Added `completion.resolveEagerly` option to allow users to opt out of the change (in anticipation for their editor to support `completionItem/resolve` if it does not already)

## 0.22.0

### Changed

- Support only jedi `0.18.0`. Stopped using `from_fs_path` from pygls, using `as_uri` method on the returned pathlib.Path objects instead. Note: older versions of Jedi are not supported by this version.

## 0.21.0

### Added

- The ability to add extra paths for your workspace's code completion (`"workspace.extraPaths"`). Thanks to [Karl](https://github.com/theangryangel) and his [PR](https://github.com/pappasam/jedi-language-server/pull/39) which inspired this feature.

### Changed

- Only 1 Jedi project is created / managed by jls. In the past, a new project was created on a per-call basis. This may have positive performance implications.

## 0.20.1

### Fixed

- documentSymbol now classifies methods/properties somewhat correctly
- Replace unnecessary private attribute access within jedi with self-managed constant

## 0.20.0

### Changed

- Update documentSymbol query
  - Uses native Jedi position finders (faster)
  - Removes noisy symbols from hierarchical output. Makes document outliners prettier / more visually useful

## 0.19.5

### Fixed

- Large character position values are now translated correctly for Jedi. See <https://github.com/pappasam/jedi-language-server/issues/42>

### Changed

- Jedi version is now pinned to protect ourselves from changes to private interfaces that we currently rely on.
- `pygls` updated to `^0.9.1`

## 0.19.4

### Fixed

- `WorkspaceSymbols` query now performs efficiently / is somewhat useable.

## 0.19.3

### Fixed

- `pygls` dependency version was locked at the wrong version. Now constrained to `^0.9.0`

## 0.19.2

### Fixed

- `ParameterInformation`, `SignatureInformation`, and `SignatureHelp` caused problems with `nvim-lsp`. Resolves <https://github.com/pappasam/jedi-language-server/issues/38>

## 0.19.1

### Changed

- `jedi>=0.17.2`

## 0.19.0

### Changed

- `jedi>=0.17.1`

### Fixed

- Hover now works more-generally correctly (thanks to Jedi's new handling of in-module references)
- Syntax message now uses Jedi's new `get_message` method on the returned error object (syntax errors now contain more human-readable messages)
- Remove now-unnecessary `.venv` hack that was introduced in `0.10.1`

## 0.18.1

### Fixed

- Refactoring code actions now properly support multi-line range where possible

## 0.18.0

### Added

- Support for CodeActions: `inline`, `extract_function`, and `extract_variable`

### Changed

- Rename now uses Jedi's rename capabilities, relying on some clever code using difflib and a range lookup mechanism

### Fixed

- Features now all return Optional values, preferring `null` to `[]`.

## 0.17.1

### Fixed

- Clean up snippet edge cases
  - Only classes and functions return snippets
  - "No parameters returned" places cursor outside of function signature
  - Snippet generation error now does not return a snippet

## 0.17.0

### Added

- cc19816 2020-05-29 | Completion opto: add jedi option to auto import modules [Sam Roeca]

### Changed

- 4c670fa 2020-05-29 | Simplify snippet contents (types were too much) (HEAD -> master, origin/master, origin/HEAD) [Sam Roeca]

## 0.16.0

### Added

- All properties in initializer are cached using "cached_property". 3rd party library used for Python 3.6 and 3.7.
- Snippet support for `CompletionItem`
- Configuration option to disable `CompletionItem` snippets (preserving existing behavior)

### Changed

- Reflecting the recent version of Jedi, the type map between Jedi and `pygls` has been reduced to reflect only the public types available in Jedi.
- Cache now no longer explicitly referenced.

### Fixed

- Some code cleanup.

## 0.15.1

### Fixed

- f44ef53 2020-05-24 | Completion: explicit insert_text_format=PlainText [Sam Roeca]
- 0d63b25 2020-05-23 | Replace symbol position functions with public ones [Sam Roeca]
- fdc0b99 2020-05-23 | Completion sorting now sorts sections, not labels [Sam Roeca]

## 0.15.0

### Changed

- 1d5a11e 2020-05-19 | Set MarkupKind based on client configuration [Sam Roeca]
- 3c41272 2020-05-19 | Save initializeParams in storage container [Sam Roeca]

## 0.14.0

### Changed

- 5e2bc3b 2020-05-17 | Completion item documentation is in PlainText (HEAD -> hover-improve) [Sam Roeca
- 44292b9 2020-05-17 | Hover now returns MarkupContent + Range [Sam Roeca]
- 0871c6d 2020-05-17 | Ensure that preferred parameters end in "=" [Sam Roeca]
- d66c402 2020-05-17 | current_word_range function added to pygls_utils [Sam Roeca]

## 0.13.2

### Changed

- Document symbol range selection made more accurate. Thanks to <https://github.com/davidhalter/jedi/issues/1576#issuecomment-627557560>!

## 0.13.1

### Changed

- Attribute access on InitializeParams now exclusively uses `rgetattr` in case Language Client omits optional fields in request.

## 0.13.0

### Changed

- Configuration takes place using initializationOptions instead of asynchronous reads of the current user config. Improves startup time and supports more LanguageClients.

### Removed

- Dynamic registration. All registration is now static since static registration is widely supported.

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
