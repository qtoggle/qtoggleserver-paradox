
from setuptools import setup, find_namespace_packages

from qtoggleserver.paradox import VERSION


setup(
    name='qtoggleserver-paradox',
    version=VERSION,
    description='Control your Paradox alarm with qToggleServer',
    author='Calin Crisan',
    author_email='ccrisan@gmail.com',
    license='Apache 2.0',

    packages=find_namespace_packages(),

    install_requires=[
        'paradox-alarm-interface==2.1.0',
        'pyserial>=3.4',
        'pyserial-asyncio>=0.4',
        'requests'
    ]
)
