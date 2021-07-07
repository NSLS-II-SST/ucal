from setuptools import setup, find_packages

setup(
    author="Charles Titus",
    author_email="charles.titus@nist.gov",
    install_requires=["bluesky", "ophyd", "sst_base"],
    name="sst_core",
    version="0.1.0",
    packages=find_packages()
)
