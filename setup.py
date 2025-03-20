from setuptools import setup, find_packages

setup(
    name='coaiapy',
    version = "0.2.21",
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
        'boto3>=1.20.0,<1.25.0',  # Stable range for Python 3.8
        'mutagen>=1.45.1,<2.0.0',
        'certifi>=2021.10.8,<2023.0.0',
        'charset-normalizer>=2.0.0,<3.0.0',  # Avoid duplicate entry
        'idna>=3.3,<4.0',
        'redis>=4.5.0,<5.0.0',  # Downgrade from 5.1.1
        'requests>=2.26.0,<3.0.0',
        'markdown>=3.3.6,<4.0.0',
        'chardet>=4.0.0,<5.0.0',
        'async_timeout>=4.0.2,<5.0.0',
        'PyYAML>=6.0,<7.0',
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
