
from setuptools import setup

setup(
    
    name='sitelogging',
    version='0.1.0',
    description='Automatic Python logging configuration.',
    url='http://github.com/mikeboers/sitelogging',
    
    py_modules=['sitelogging'],
    
    author='Mike Boers',
    author_email='sitelogging@mikeboers.com',
    license='BSD-3',

    entry_points={
        'sitecustomize': [
            'sitelogging = sitelogging:main',
        ],
    },

)
