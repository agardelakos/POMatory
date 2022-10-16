import sys
from setuptools import setup
import setuptools

if sys.version_info < (3, 6):
    sys.exit('Sorry, POMatory requires Python >= 3.6')

setup(
    name='POMatory',
    version='0.0.1',
    url='https://github.com/agardelakos/POMatory',
    license='MIT',
    author='agardelakos',
    author_email='agardelakos@gmail.com',
    description="POMatory: Automatically find locators for web elements that can be used in selenium projects",
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(include='pomatory.find_locators'),
    entry_points={
        'console_scripts': ['pomatory=pomatory.app:main_menu'],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        "selenium >= 4.5.0",
        "beautifulsoup4 >= 4.11.1",
    ],
    include_package_data=True,
)
