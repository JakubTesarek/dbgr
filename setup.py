from setuptools import setup, find_packages
from os import path

here = path.abspath(path.dirname(__file__))

with open('README.md') as readme:
    long_description = readme.read()

setup(
    name='dbgr',
    version='1.0.0',
    python_requires='>=3.7',
    description='REST API testing tool',
    long_description=long_description,
    url='https://github.com/JakubTesarek/dbgr',
    author='Jakub Tesárek',
    author_email='jakub@tesarek.me',
    license='APACHE LICENSE 2.0',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: Apache Software License',
        'Intended Audience :: Developers'
    ],
    keywords='api rest api testing',
    packages=find_packages(),
    py_modules = ['app'],
    include_package_data=True,
    install_requires=['aiohttp', 'jinja2', 'colorama', 'argcomplete', 'pygments'],
    extras_require={'test': ['pytest', 'pylint', 'pytest-cov']},
    entry_points={'console_scripts': ['dbgr = app:dbgr']}
)
