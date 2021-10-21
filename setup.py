import setuptools
import spacebarheating

with open("README.md", "r") as f:
    long_description = f.read()

setuptools.setup(
    name="spacebarheating",
    version=spacebarheating.VERSION,
    description="Heat up your CPU by holding the spacebar, inspired by https://xkcd.com/1172/",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/elesiuta/spacebarheating",
    license="MIT",
    py_modules=["spacebarheating"],
    entry_points={"console_scripts": [
        "spacebarheating = spacebarheating:cli",
        "spacebarheating.win32svc = spacebarheating:win32svc"
    ]},
    install_requires=["keyboard"],
    extras_require={"pywin32": ["pywin32"]},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Topic :: Utilities"
    ],
)
