from setuptools import setup, find_packages

with open('version.txt', 'r', encoding='utf-8') as f:
    version = f.read().strip()

with open('requirements.txt', 'r', encoding='utf-8') as f:
    requirements = [l.strip() for l in f.readlines()]

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

    install_requires=requirements,
    package_dir={'': 'src'},
    packages=find_packages(where='src'),
    entry_points={
        'console_scripts': [
            'webwatcher=webwatcher.main:main'
        ]
    }
)
