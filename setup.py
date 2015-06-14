from setuptools import setup

setup(
    
    name='sitetools',
    version='0.1.0',
    description='Customize your Python startup sequence.',
    url='http://github.com/westernx/sitetools',
    
    packages=['sitetools'],
    
    entry_points={
        'sitehooks': {
            '000_sitetools = sitetools._startup:sitehook'
        },
    },
    
    author='Mike Boers',
    author_email='sitetools@mikeboers.com',
    license='BSD-3',

)
