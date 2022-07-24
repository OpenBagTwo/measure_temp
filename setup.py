from setuptools import setup

import versioneer

setup(
    name="measure_temp",
    description="vcgencmd measure_temp for a few Linux boxes",
    author='Gili "OpenBagTwo" Barlev',
    url="https://github.com/OpenBagTwo/measure_temp",
    packages=["measuretemp"],
    license="GPL v3",
    install_requires=["pysensors"],
    include_package_data=True,
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
)
