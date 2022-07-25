from setuptools import setup

import versioneer

setup(
    name="measure_temp",
    description="vcgencmd measure_temp for a few Linux boxes",
    author='Gili "OpenBagTwo" Barlev',
    url="https://github.com/OpenBagTwo/measure_temp",
    packages=["measure_temp"],
    license="GPL v3",
    install_requires=["pysensors==0.0.4", "Click>=8"],
    include_package_data=True,
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
)
