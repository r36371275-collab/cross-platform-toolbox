# Cross-platform Toolbox

Three small command-line utilities for Windows, macOS, and Linux. They use only the Python standard library and work offline.

## Requirements

- Python 3.10 or newer

## Run

No installation is required. From this folder, run:

```sh
python3 toolbox.py --help
```

On Windows, use `py toolbox.py --help` in PowerShell or Command Prompt.

### Organize a folder

Preview changes first; files are not moved unless `--apply` is supplied.

```sh
python3 toolbox.py organize ~/Downloads
python3 toolbox.py organize ~/Downloads --apply
```

Files are grouped into folders by extension. Existing files are never overwritten; collisions get a numbered filename.

### Generate a password

```sh
python3 toolbox.py password --length 24
```

The password is generated locally with Python's secure random source and is printed once. The tool does not save it.

### Check disk space

```sh
python3 toolbox.py disk
python3 toolbox.py disk ~/ --json
```

## Safety

The organizer only examines files directly inside the selected folder, does not follow directory symlinks, and defaults to preview mode. Review the preview before using `--apply`. The password generator never writes credentials to disk.

## Test

```sh
python3 -m unittest discover -s tests -v
```

Licensed under the MIT License; see [LICENSE](LICENSE).
