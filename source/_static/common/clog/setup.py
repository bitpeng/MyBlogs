from setuptools import setup, find_packages
#from distutils.core import setup


setup(
    name='clog',
    version='0.1',

    packages=find_packages(),
    #packages=['gtutils'],
    include_package_data=True,
    author='chenshiqiang',
    author_email='bitpeng@yeah.net',
    description='some useful utils for myself',
    #zip_safe=False,
)
