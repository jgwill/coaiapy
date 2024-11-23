from setuptools import setup, find_packages

setup(
    name='coaiapy',
    version='0.1.0',
    author='Jean GUillaume ISabelle',
    author_email='jgi@jgwill.com',
    description='A Python package for audio transcription, synthesis, and tagging using Boto3.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/jgwill/coaiapy',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    install_requires=[
        'boto3',
        'mutagen',
        'certifi',
        'charset-normalizer',
        'idna',
        'redis',
        'requests',
        'pytest'
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)