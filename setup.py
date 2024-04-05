from setuptools import setup, find_packages
from glob import glob

scripts = glob("scripts/*")
scripts = [script for script in scripts if script[-1] != '~']

setup(
    author="Charles Titus",
    author_email="charles.titus@nist.gov",
    install_requires=["bluesky", "ophyd", "sst_base", "sst_funcs"],
    name="ucal",
    use_scm_version=True,
    packages=find_packages(),
    package_data={"ucal": ["*.yaml"]},
    scripts=scripts,
    entry_points={"sst_gui.plans": ["ucal-tes-count=ucal.qt.plans.tesBasic:TESCountWidget",
                                    "ucal-tes-scan=ucal.qt.plans.tesBasic:TESScanWidget",
                                    "ucal-tes-cal=ucal.qt.plans.tesBasic:TESCalibrateWidget"]}
)
