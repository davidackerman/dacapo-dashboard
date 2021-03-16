from setuptools import setup, find_packages

setup(
    name="dashboard",
    version="0.1",
    url="https://github.com/funkelab/dashboard",
    author="William Patton",
    author_email="pattonw@janelia.hhmi.org",
    license="MIT",
    packages=find_packages(),
    entry_points="""
            [console_scripts]
            dacapo-dashboard=dashboard.cli.cli:cli
        """,
    include_package_data=True,
)
