# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## 0.38.0

### Added

- Support for Python 3.11
- Support `workspace.environmentPath` initialization option. Enables configuration of [Jedi's Project environment path](https://jedi.readthedocs.io/en/latest/docs/api.html#jedi.Project).

### Changed

- `pygls` version constraint updated to `^0.12.4`

## 0.37.0

### Added

- Support `textDocument/typeDefinition`. Resolves <https://github.com/pappasam/jedi-language-server/issues/221>

## 0.36.1

- Dependency updates, most relevant being pydantic to 1.9.1.

## 0.36.0

### Removed

- Drop support for Python 3.6

### Fixed

- Class properties now hover as simple properties. Resolves <https://github.com/pappasam/jedi-language-server/issues/200>

## 0.35.1

### Changed

- `jedi` version constraint has been relaxed to `^0.18.0`. Resolves <https://github.com/pappasam/jedi-language-server/issues/190>.

## 0.35.0

### Changed

- Default log level has been changed to `WARN`, suppresses verbose `INFO` messages provided by pygls.

## 0.34.12

### Changed

- Completions are now sorted public, private, then dunder.
- The order of completion items returned by Jedi is now preserved across clients through explicit sort order.

## 0.34.11

### Fixed

- Fix edge case where LSP methods that relied on `jedi_utils.lsp_range` (like Highlight) would break if `jedi.api.classes.Name` returned an empty line/column. Now, module builtins like `__name__` and `__file__` will Highlight / Hover correctly.

## 0.34.10

### Fixed

- `CompletionItem.detail` no longer provides redundant information that is already provided in `CompletionItem.kind`.
- Explicit calls to `get_type_hint` are removed for performance reasons.
- classes and functions with no arguments sometimes return no jedi signatures. In these cases, we manually provide `()` at the end of said classes and functions to ensure a consisten detail experience for end users.

## 0.34.9

### Changed

- Completion detail now has full signature.
- Descriptive text is now more standardized across Completion, Hover, and Signature Items. Main difference comes down to inclusion of full name (Hover) and inclusion of multiple signatures (Signature).

## 0.34.8

### Fixed

- Fixed bug where classes nested inside functions cause exceptions in textDocument/documentSymbol. This release avoids the crash and includes info about classes and functions nested inside functions. See [this issue](https://github.com/pappasam/jedi-language-server/issues/170)

## 0.34.7

### Added

- InitializationOption `completion.ignorePatterns`, an option for users to conditionally ignore certain completion patterns. A generalized solution to [this issue](https://github.com/pappasam/jedi-language-server/issues/168).

## 0.34.6

### Fixed

- Completion at beginning of line now works.
- Per comment [here](https://github.com/pappasam/jedi-language-server/issues/162#issue-1004770374), may resolve issues associated with Windows line endings.
- `jedi_line_column` now returns a tuple instead of a dict. Since this function is often used, it makes sense to choose a more-performant data type.

## 0.34.5

### Fixed

- InitializationOption `jediSettings.debug` now writes to stderr, not stdout. stdout broke the language server.

## 0.34.4

### Added

- InitializationOption `jediSettings.debug` that lets user configure jedi's debugging messages to print to stdout.

## 0.34.3

### Fixed

- Jedi Names may have no `module_path`, so `lsp_location` now returns an `Optional[Location]`. Thanks @dimbleby !

## 0.34.2

### Fixed

- Empty docstrings no longer result in unnecessary newlines for signatureHelp (and potentially other requests). Resolves <https://github.com/pappasam/jedi-language-server/issues/158>.

## 0.34.1

### Fixed

- From Jedi's perspective, operations at the beginning of a line now assume they are at position 1. This ensures that hover operations work correctly at the beginning of the line.

## 0.34.0

### Changed

- Diagnostics are now cleared on document close.

## 0.33.1

### Added

- Support for serving content over web sockets.

## 0.33.0

### Changed

- Now support all Python 3.6 versions; we don't need to constrain our runtime requirements to anything less than 3.6 because only our development dependencies require Python > 3.6.0.
- Updated pygls to latest version.

## 0.32.0

### Added

- Initialization options to granularly disable names and full names for hover operations based on their Jedi type. This is useful because some text editors will automatically send hover requests when a user pauses their cursor over text and the large amount of information can get annoying for some users. Resolves: <https://github.com/pappasam/jedi-language-server/issues/147>. Jedi types are currently: `module`, `class`, `instance`, `function`, `param`, `path`, `keyword`, `property`, and `statement`.
- Initialization option to disable hover entirely. If `enable` is set to false, the hover language feature will not be registered. May consider adding something similar to most language server features if this proves useful.

### Changed

- In Hover, `Path` has been renamed to `Full name`, which is more accurate and is directly tied to the hover disabling options.
- Restrict Python version support to >= 3.6.2. Upgraded development dependencies. Latest black doesn't support Python < 3.6.2, so to keep things simple here we're now not supporting Python versions below that version either.

## 0.31.2

### Fixed

- Docstring now presents same information as before, but organized more-tersely, (arguably) more clearly, and with much better markdown syntax support. For example, the name / signature has been pulled out from the main docstring and wrapped in python triple back ticks while the docstring is conditionally replaced with the description where relevant.

## 0.31.1

### Fixed

- `get_type_hint` is now wrapped in general Exception. It's more broken than thought, so we'll prevent this from bubbling up to users.
- Conditionally show markdown. If users / editors want to prefer plaintext, we won't return markdown-formatted titles for the hover text

## 0.31.0

### Changed

- Markdown text that is not recognized by `docstring-to-markdown` is no longer automatically wrapped in a code block. I found that, more often than not, this resulted in annoying formatting for me.
- Hover text now displays a lot more information, taking advantage of Jedi's Name methods and properties. Information now includes the module path to the name, the description, and an inferred type hint in addition to the docstring. This is all formatted with markdown so it looks pretty.

## 0.30.3

### Fixed

RenameFile now works correctly: `kind` now correctly passed to RenameFile due to recently-released pygls updates. Minimum pygls version now 0.10.3.

## 0.30.2

### Changed

Require importlib-metadata for Python 3.6 and 3.7. It is technically required and some clients might check jls version. See: <https://github.com/pappasam/coc-jedi/issues/32>

## 0.30.1

### Fixed

- null initializationOption is now accepted as valid input, without warning. Resolves <https://github.com/pappasam/jedi-language-server/issues/104>

## 0.30.0

### Added

- New initialization options to configure extracted variable and extracted function codeAction: nameExtractVariable and nameExtractFunction.

### Changed

- Configurable codeAction extraction names. Names are no longer randomly-generated. Instead, they are configurable in initializationOptions, defaulting to a name that's specific to jedi-language-server.

## 0.29.0

### Added

- The following CLI options:
  - `--tcp`: use TCP server instead of stdio
  - `--host`: host for TCP server (default 127.0.0.1)
  - `--port`: port for TCP server (default 2087)
  - `--log-file`: redirect logs to the given file instead of writing to stderr
  - `-v` / `--verbose`: increase verbosity of log output
- Logging. To stderr by default, but optionally a file on the file system.

## 0.28.8

### Changed

- Updated cli to use `argparse` instead of `click`.
- Required pygls version updated to `0.10.2` to accommodate recent bugfixes / prevent users from filing issues based on old version.

### Removed

- Removed `click` from dependencies.

## 0.28.7

### Changed

- Within TextEdit utils, simplify mapping from file offset to Position. This is clearer, handles edge cases better, and is more algorithmically efficient.

## 0.28.6

### Fixed

General TextEdit fixes for code refactoring:

- Update fix from 0.28.5 so that it doesn't pad at the start; no opcode will refer to old[-1:n].
- Revert opcode.old_end -> opcode.old_end - 1. This becomes unnecessary with prior update, and indeed could be a bad idea when in the middle of a file (if you're unlucky, you could end up finding the line before the one you wanted).
- Use pygls.document to get the old code, rather than the private jedi method.

## 0.28.5

### Fixed

- Handle TextEdit edge case where opcode is checked for 1 past last character. Resolves <https://github.com/pappasam/jedi-language-server/issues/96>
- No longer return textEdit actions from Jedi that aren't valid Python. Prevents all sorts of wonkiness.

## 0.28.4

### Fixed

- Handle null rootUri's by not creating a Jedi project, fixes <https://github.com/pappasam/jedi-language-server/issues/95>
- Tolerate invalid InitializationOptions by using default values on error

## 0.28.3

### Fixed

- completionItem/resolve now works again (broke with 0.28.0's migration to pygls 0.10.0)

## 0.28.2

### Added

- signatureHelp now also returns documentation, if available.

## 0.28.1

Same functions as 0.28, but different tag.

## 0.28.0

### Changed

- pygls `0.10.0`. This version explicitly uses `pydantic` and better supports initialization options. This enables use to remove the `cached-property` dependency for Python versions 3.6 and 3.7.
- pydantic is now used for initialization options parsing. Simplified so much that we were able to remove initializationOption-specific tests.
- Explicitly add method for `did_open`, for some weird reason the latest pygls bugs out if you don't explicitly set this function to at least an empty function.

### Removed

- Support for Python 3.6.0. We now only support Python 3.6.1+.
- Monkey patch for `null` versus `missing` attributes. `pydantic` / `pygls>=0.10.0` handles this.

## 0.27.2

### Fixed

- Provide correct version information on `TextDocumentEdit`.

## 0.27.1

### Fixed

- Monkey patched pygls to remove null types from response. This is a temporary fix to more-fully support nvim-lsp et al, necessary until pygls releases its next version.

## 0.27.0

### Added

- Initialization option `workspace.symbols.ignoreFolders` to set names of folders that are ignored during the workspace symbols action. For performance reasons; things slow down a LOT when symbols come from 3rd party library locations.

### Changed

- (Breaking from 0.26.0) Initialization option `workspace.maxSymbols` changed to `workspace.symbols.maxSymbols`.

## 0.26.0

### Added

- Initialization option `workspace.maxSymbols` to set the max workspace symbols returned by Jedi. Set to 0 or fewer to disable the setting of max and to return as many symbols as are found.

## 0.25.7

### Fixed

- Stop putting keyword-only arguments in snippets. That turned out to be more annoying than helpful.

## 0.25.6

### Fixed

- Fixes renaming edge case where lines at end get KeyError.

## 0.25.5

### Fixed

- Fix renaming a variable that appears at the start of a line
- Fix handling of `completionItem/resolve` when not all fields are present on the `CompletionItem`.
- Fix handling of eager resolution of completions.

## 0.25.4

### Fixed

- SymbolKind and CompletionItemKind now support `Property`. Support is still a bit finicky, and I'm not sure whether it's Jedi's issue or an issue with jedi-language-server at this time.
- `jedi_utils.line_column` now ensures that line length never falls below 0. Resolves <https://github.com/pappasam/jedi-language-server/issues/74>

## 0.25.3

### Changed

- Relax version constraints for `docstring-to-markdown` to be compatible with all versions below `1.0`. Author confirms there won't be breaking changes until at least then: <https://github.com/pappasam/jedi-language-server/issues/68#issuecomment-778844918>

## 0.25.2

### Fixed

- Markdown-formatted text that cannot be converted is now surrounded by fences
- An edge case where markup_kind variable is a string, and not MarkupKind, is properly handled

## 0.25.1

### Fixed

- Bug where client-supported markupkind wasn't being properly converted to `MarkupKind`, which caused problems when relying on client-provided defaults.

## 0.25.0

### Added

- When `MarkupKind` is `"markdown"`, convert docstrings from rst to markdown. Currently uses <https://github.com/krassowski/docstring-to-markdown>, thanks @krassowski for the awesome library! Special attention has been paid to error handling here to give @krassowski leeway to develop the library further.

## 0.24.0

### Added

- `caseInsensitiveCompletion` initialization option added. The user can now tell Jedi to only return case sensitive completions by setting this value to false.

### Fixed

- Handle jedi 0.18.0's change from `str` to `pathlib.Path` for workspace symbols.

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

- jedi completion `param` sorts first in COMPLETION. Resolves <https://github.com/pappasam/jedi-language-server/issues/19>

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
