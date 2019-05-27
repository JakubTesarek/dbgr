from setuptools import setup, find_packages
from os import path
from dbgr.meta import __version__

with open('requirements.txt') as fp:
    install_requires = fp.read()

with open('requirements-dev.txt') as fp:
    extras_require = fp.read()

with open('README.md') as readme:
    long_description = readme.read()

setup(
    name='dbgr',
    version=__version__,
    python_requires='>=3.7',
    description='REST API testing tool',
    long_description=long_description,
    long_description_content_type='text/markdown',
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
    install_requires=install_requires,
    extras_require={'test': extras_require},
    entry_points={'console_scripts': ['dbgr = app:dbgr']}
)
