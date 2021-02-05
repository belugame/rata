import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="rata",
    version="0.0.2",
    author="belugame",
    author_email="mb@altmuehl.net",
    description="A CLI task time tracker loosely based on org-mode",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/belugame/rata",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
    install_requires=[
        'urwid',
    ],
    entry_points={
        'console_scripts': ['rata=rata.__main__:main'],
    }
)
