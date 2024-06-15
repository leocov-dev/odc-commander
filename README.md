# ODC Commander

![GitHub Release](https://img.shields.io/github/v/release/leocov-dev/odc-commander)
![GitHub License](https://img.shields.io/github/license/leocov-dev/odc-commander)
![GitHub Actions Workflow Status](https://img.shields.io/github/actions/workflow/status/leocov-dev/odc-commander/ci.yaml)


> This is still work-in-progress and is not producing usable builds

This is a command and control app for [Open Dynamic Clamp](https://github.com/nsdesai/dynamic_clamp/tree/master/open-dynamic-clamp). 
Different versions may support different flavors of the device firmware. 
Please check the release notes for each release for supported version details.

## Install

Browse the [Releases](https://github.com/leocov-dev/odc-commander/releases) page for pre-compiled app executables.

The builds are not cryptographically signed, so you may be presented with a dialog to allow the app to run.

## Local Development

### Requirements

- [Hatch](https://hatch.pypa.io/latest/)
- Python 3.12

---

Create the default venv
```shell
hatch env create
```

Run the app
```shell
hatch run odc-commander
```

Rebuild `resources.rcc` (only required if changing something in `src/resources`)
```shell
hatch run compile-rcc
```

Create a local release for your operating system. 
Cross compiling to a packaged binary is not supported.
The build is placed in the `dist` directory.
```shell
hatch run release-build
```

Run linting/formatting. Will auto-format code and run formatting and type checking validations.
```shell
hatch fmt
```

Version up the code. This will write the variable `__version__` in `src/odc_commander/__init__.py`
```shell
hatch version 1.2.3
```
