
from setuptools import setup, find_namespace_packages


setup(
    name='qtoggleserver-paradox',
    version='1.0.0',
    description='Control your Paradox alarm with qToggleServer',
    author='Calin Crisan',
    author_email='ccrisan@gmail.com',
    license='Apache 2.0',

    packages=find_namespace_packages(),

    # TODO reorganize this once paradox-alarm-interface gets published to PyPI
    install_requires=[
        'paradox-alarm-interface @ https://github.com/ParadoxAlarmInterface/pai/archive/'
                '5c983c21fa8b10f009d4b449af290da37b86eb67.tar.gz',
        'require-python-3',
        'construct>=2.9.43',
        'pyserial>=3.4',
        'pyserial-asyncio>=0.4',
        'PyPubSub>=4.0.3',
        'requests>=2.20.0'
    ]
)
