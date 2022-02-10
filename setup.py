from setuptools import setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name = "Odziemski_PZ",
    version = "1.0.0",
    url = "http://github.com/Rogh1996/ProjektZaliczeniowy",
    author='Rafał Odziemski',
    author_email='r.odziemski@student.uw.edu.pl',
    description = "Projekt zaliczeniowy",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license='MIT',
    packages= ["OdziemskiProjektZaliczeniowy"],
    package_data={"OdziemskiProjektZaliczeniowy": ["requirements.txt"]},
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires = [
        "numpy",
        "pandas",
        "xlsxwriter",
        "openpyxl",
        "pytest"
    ]
)