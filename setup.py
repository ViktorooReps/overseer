from setuptools import setup, find_packages
from io import open
from os import path

import pathlib

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

# automatically captured required modules for install_requires in requirements.txt and as well as configure dependency links
with open(path.join(HERE, 'requirements.txt'), encoding='utf-8') as f:
    all_reqs = f.read().split('\n')

install_requires = [x.strip() for x in all_reqs if ('git+' not in x) and (not x.startswith('#')) and (not x.startswith('-'))]

dependency_links = [x.strip().replace('git+', '') for x in all_reqs if 'git+' not in x]

setup(
    name='gpu-overseer',
    description='Telegram notifier for GPU availability status.',
    version='0.0.8',
    packages=find_packages(),  # list of all packages
    install_requires=install_requires,
    python_requires='>=3.6',
    entry_points='''
        [console_scripts]
        overseer=notifier.__main__:main
    ''',
    author="Viktor Scherbakov",
    keyword="Telegram, bot, notifier, gpu status",
    long_description=README,
    long_description_content_type="text/markdown",
    license='MIT',
    url='https://github.com/ViktorooReps/overseer',
    download_url='https://github.com/ViktorooReps/overseer/archive/0.0.1.tar.gz',
    dependency_links=dependency_links,
    author_email='viktoroo.sch@gmail.com',
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.9",
    ],
    include_package_data=True,
)
