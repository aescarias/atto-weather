# Contributing Guidelines

Thank you for considering a contribution to Atto Weather!

## Reporting Issues

When reporting an issue, please provide the information below. This will allow us to debug your issue and implement possible fixes.

1) The version of Atto Weather and your operating system.
2) The log file created by the app (run the app through the command line).
3) Steps showing how to reproduce the issue.
4) Screenshots or videos demonstrating the issue (optional but recommended).

## Translations

Atto Weather uses TOML files for translations. They are stored in the `languages/` folder.

## Updating an existing language

1) Find your language file in the `languages/` folder. Each file is named by its respective ISO 639-1 language code.
2) Look for any missing or commented-out translations. Compare with the `en.toml` file.
3) Translate them accordingly and submit your PR.

## Adding a new language

1) Create a new language file by copying the contents of the `en.toml` file. Use the corresponding ISO 639-1 language code for the filename.
2) Set the `language` field below `[self]` to the name of the language (as it would be called in that language).
3) Apply all equivalent translations. If unable to provide a translation for a specific field, comment that field out and explain your reasoning in English (as in: `# feels_like = null # x reason`).
4) Test your translation by adding it to the `languages` folder and using it within the app.
5) Create a PR as usual.

## Contributing to Source Code

### Style Guide

- Docstrings should be written according to the [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html#docstrings).
- Code is formatted using Ruff. Make sure to follow the [PEP8](https://www.python.org/dev/peps/pep-0008/) style guide as well.
- Markdown documents are linted through [Markdownlint](https://github.com/DavidAnson/markdownlint).
- Commit messages follow [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/). See below.
- Strings within the user interface should be localized.

### Versioning

Our project follows [Semantic Versioning 2.0.0](https://semver.org/spec/v2.0.0.html). In short:

- Major versions are ground-breaking changes. These hold no guarantees (`1.0.0` to `2.0.0` would not be possible, nor would `2.0.0` to `1.0.0`).
- Minor versions include additions that guarantee an upgrade is possible but not a downgrade (`1.0.0` to `1.1.0` is possible, but not `1.1.0` to `1.0.0`).
- Patch versions are small fixes or additions that guarantee either an upgrade or a downgrade is possible (`1.0.0` to `1.0.1` and `1.0.1` to `1.0.0` are possible).

### Commit Messages

Commit messages should be descriptive and concise. Commit messages should also specify their scope. The scope should be the modules or areas affected by the commit (for example, `fix(ui): ...`).

The scopes currently in use are:

- `docs`: Documentation changes within code or associated resources.
- `i18n`: Translations.
- `tests`: Code coverage and unit testing.
- `ui`: Changes to user interface.

The commit types currently in use are:

- `feat` for new features.
- `fix` For bug fixes (if applicable, they should reference the issue this commit resolves).
- `chore` for anything else not covered in the other types.
