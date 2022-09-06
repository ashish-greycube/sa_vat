from setuptools import setup, find_packages

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

# get version from __version__ variable in sa_vat/__init__.py
from sa_vat import __version__ as version

setup(
	name="sa_vat",
	version=version,
	description="VAT customizations for South Africa",
	author="Greycube",
	author_email="admin@greycube.in",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
