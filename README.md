# ODC Commander

> This is still work-in-progress and is not producing usable builds

## Install

Browse the Releases page for pre-compiled app executables.

## Requirements

- Hatch
- Python 3.11.*, 3.12.*

## Local Development

Create the default venv
```shell
hatch env create
```

Run the app
```shell
hatch run odc-commander
```

Rebuild theme files
```shell
hatch run compile-rcc
```

Create a local release
```shell
hatch run release-build
```

Run linting/formatting
```shell
hatch fmt
```