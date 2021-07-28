from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="stableplanets",
    version="v2021.07.28",
    description="Stable Planets",
    author="Joe Glaser, Myrla Phillippe, and Alicia Palmerin",
    author_email="joe.glaser@nanograv.org",
    url="https://github.com/JPGlaser/StablePlanets",
    long_description=long_description,
    long_description_content_type="text/markdown",
    package_dir = {'': 'src'},
    packages = find_packages('src'),
    install_requires=['amuse', 'astropy', 'pyvo', 'numpy'],
    python_requires='>=3.7'
)
