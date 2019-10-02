from setuptools import setup, find_packages

setup(
    name='exrconverter',
    version='1.0.0',
    author='Manuchehr Taghizadeh-Popp, Jared Feingold, Keyi Chen',
    author_email='mtaghiza@jhu.edu',
    description='Python package for converting EXR images into different file formats, back and forth.',
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    url='https://github.com/idies/exr-converter',
    packages=find_packages(exclude=["contrib", "docs", 'tests*']),
    include_package_data = True,
    keywords=["package", "setup"],
    scripts=[],
    license='Apache 2.0',
    install_requires=['numpy'],
    classifiers = [
                   "Intended Audience :: Developers",
                   "Operating System :: OS Independent",
                   "License :: OSI Approved :: Apache 2.0",
                   "Programming Language :: Python",
                   "Programming Language :: Python :: 3.6",
                   "Programming Language :: Python :: 3.7",
               ]
)