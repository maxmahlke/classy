from setuptools import setup, find_packages

setup(
    name="classy",
    version="0.1",
    packages=find_packages(),
    include_package_data=True,
    py_modules=["classy"],
    install_requires=[
        "click",
        "iterfzf",
        "matplotlib",
        "numpy",
        "pandas",
        "pandarallel",
        "pymc3",
        #  "sbpy",
        "sklearn",
    ],
    entry_points="""
        [console_scripts]
        classy=classy.cli:cli_classy
    """,
)
