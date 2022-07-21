# `measure_temp`
A re-implementation of the RPI `vcgencmd measure_temp` script that
should work across all of my Linux boxes to report one
key performance temperature for each device.

This is engineered for my specific use-case
(using [a plugin for JuiceSSH](https://github.com/Sonelli/juicessh-performancemonitor)),
and I'm sure there are better general-purpose packages out there.
_That being said..._

## Usage Instructions

0. Make sure your system is running Python 3.7 or greater and install
   `lm-sensors`.
1. Install this package via `pip`:
   ```bash
   $ python3 -m pip install git+https://github.com/OpenBagTwo/measure_temp
   ```
   (throwing in a `sudo` if needed)
1. Get your temp via:
   ```bash
   $ measure_temp
   ```
   which, if all goes according to plan, should spit out a value like
   ```
   temp=62.3'C
   ```

## Development instructions

0. [Install `mambaforge`](https://github.com/conda-forge/miniforge#mambaforge)
   (not required, just highly recommended over `venv` or `conda`)
1. If using `conda` or `mamba`, create the development environment by
   navigating to the project root and calling:
   ```bash
   $ mamba env create
   ```
   (substitute `conda` if you have to)
1. Then run:
   ```bash
   $ pre-commit install
   ```
   to set up the pre-commit hooks.

## License

This package is licensed under GPLv3. If you have a use case for adapting
this code that requires a more permissive license, please post an issue,
and I'd be more than willing to consider a dual license.
