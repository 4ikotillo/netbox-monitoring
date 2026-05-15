from setuptools import setup, find_packages
setup(name='netbox-monitoring',version='0.2.0',packages=find_packages(),include_package_data=True,install_requires=['requests'],package_data={'netbox_monitoring':['templates/**/*.html']},python_requires='>=3.10')
