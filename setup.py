from setuptools import setup, find_packages

setup(
    name='coaiapy',
    version = "0.2.16",
    author='Jean GUillaume ISabelle',
    author_email='jgi@jgwill.com',
    description='A Python package for audio transcription, synthesis, and tagging using Boto3.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/jgwill/coaiapy',
    packages=find_packages(
        include=["coaiapy", "test-*.py"], exclude=["test*log", "*test*csv", "*test*png"]
    ),
    #package_dir={'': 'coaiapy'},
    install_requires=[
        'boto3',
        'mutagen',
        'certifi',
        'charset-normalizer',
        'idna',
        'redis==5.1.1',
        'requests',
        'markdown',
        'chardet',
        'charset-normalizer',
        'async_timeout',
        'PyYAML',
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
