from setuptools import setup

setup(
    name='thedudeabides',
    version='0.2.0',
    description='The dude abides',
    url='https://github.com/r1tger/the-dude-abides',
    author='Ritger Teunissen',
    author_email='github@ritger.nl',
    packages=['thedudeabides'],
    # setup_requires=['pytest-runner'],
    # tests_require=['pytest>=3.0.0', 'freezegun'],
    install_requires=[
        'ReParser',
        'graph-tools',
        'ngram'
    ],
    entry_points={'console_scripts': [
        'thedudeabides = thedudeabides.__main__:main',
    ]},
    zip_safe=False
)
