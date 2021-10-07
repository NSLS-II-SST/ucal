from setuptools import setup, find_packages
from glob import glob

scripts = glob("scripts/*")
scripts = [script for script in scripts if script[-1] != '~']

setup(
    author="Charles Titus",
    author_email="charles.titus@nist.gov",
    install_requires=["bluesky", "ophyd", "bl_base", "bl_funcs"],
    name="sst_common",
    use_scm_version=True,
    packages=find_packages(),
    scripts=scripts
)
