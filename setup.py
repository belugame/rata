import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="rata",
    version="1.0.0",
    author="belugame",
    author_email="mb@altmuehl.net",
    description="A CLI task time tracker with JSON storage",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/belugame/rata",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.11',
    install_requires=[
        'urwid',
    ],
    entry_points={
        'console_scripts': ['rata=rata.__main__:main'],
    }
)
