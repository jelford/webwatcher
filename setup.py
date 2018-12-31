from setuptools import setup, find_packages
import json

with open('version.txt', 'r', encoding='utf-8') as f:
    version = f.read().strip()

def load_requirements():
    with open('Pipfile.lock', 'rb') as f:
        requirements_json = json.load(f)
    return [
            f'{rname}{rspec["version"]}' for rname, rspec in requirements_json['default'].items()
            if 'editable' not in rspec
    ]
        

setup(
    name='webwatcher',
    version=version,
    description='A tool for checking webpages for changes',
    url='https://github.com/jelford/webwatcher',
    author='James Elford',
    author_email='jelford@protonmail.com',
    license='ISC',
    classifiers=[
        'Develpment Status :: 4 - Alpha',
        'Intended Audience :: Information Technology',
        'Programming Language :: Python :: 3.6',
    ],

    install_requires=load_requirements(),
    package_dir={'': 'src'},
    packages=find_packages(where='src'),
    entry_points={
        'console_scripts': [
            'webwatcher=webwatcher.main:main'
        ]
    }
)
