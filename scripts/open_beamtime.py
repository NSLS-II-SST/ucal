from sst_base.users import new_experiment
from sst_base.beamtime import save_config

base_folder = "/tmp"


print("Enter user name")
name = input("Full name: ")
gup = input("GUP number: ")
saf = input("SAF number: ")


user_directory = new_experiment(base_folder, gup, saf, name)

beamtime_md = {"user_directory": user_directory}
save_config(beamtime_md)
