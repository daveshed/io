from setuptools import setup, find_packages
setup(
    name="io",
    version="0.0.0",
    packages=find_packages(),
    install_requires=[
        'stage',     # needs interface
        'RPi.GPIO',  # needs pi drivers
    ],
)
