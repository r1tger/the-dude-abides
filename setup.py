from setuptools import setup

setup(
    name='thedudeabides',
    version='0.4.0',
    description='The dude abides',
    url='https://github.com/r1tger/the-dude-abides',
    author='Ritger Teunissen',
    author_email='github@ritger.nl',
    packages=['thedudeabides'],
    install_requires=[
        'graph-tools',
        'ngram',
        'frontmatter',
        'markdown-it-py',
        'jinja2'
    ],
    entry_points={'console_scripts': [
        'thedudeabides = thedudeabides.__main__:main',
    ]},
    zip_safe=False
)
