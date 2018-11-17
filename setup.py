from codecs import open
import re
from setuptools import setup


def get_long_description():
    with open('README.md', encoding='utf-8') as f:
        return f.read()


def get_version():
    pattern = r'^__version__ = \'([^\']*)\''
    with open('triex/triex.py', encoding='utf-8') as f:
        text = f.read()
    match = re.search(pattern, text, re.M)

    if match:
        return match.group(1)
    raise RuntimeError('Unable to determine version')


setup(
    name='triex',
    version=get_version(),
    description='Simple utility to enable/disable and hide/show stock macOS applications.',
    long_description=get_long_description(),
    url='https://bitbucket.org/lojoja/triex',
    author='lojoja',
    author_email='github@lojoja.com',
    license='MIT',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: MIT License',
        'Operating System :: MacOS :: MacOS X',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    packages=['triex'],
    install_requires=['click>=6.0'],
    entry_points={'console_scripts': ['triex=triex.cli:cli']},
)
