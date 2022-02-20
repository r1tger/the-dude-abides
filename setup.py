from setuptools import setup

setup(
    name='thedudeabides',
    version='0.8.4',
    description='The dude abides',
    url='https://github.com/r1tger/the-dude-abides',
    author='Ritger Teunissen',
    author_email='github@ritger.nl',
    packages=['thedudeabides'],
    package_data={'thedudeabides': ['templates/*.tpl']},
    install_requires=[
        'click',
        'jinja2',
        'markdown-it-py',
        'mdit-py-plugins',
        'networkx',
        'python-frontmatter'
    ],
    entry_points={'console_scripts': [
        'thedudeabides = thedudeabides.__main__:main',
    ]},
    zip_safe=False
)
