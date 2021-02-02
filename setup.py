import io

from setuptools import setup, find_packages

from guacamole import VERSION


install_requires = (
    'future >= 0.15.2',
    'six >= 1.10.0'
)


setup(
    name='pyguacamole',
    version=VERSION,
    url='https://github.com/mohabusama/pyguacamole',
    author='Mohab Usama',
    description=('A Guacamole python client library.'),
    long_description=io.open('README.rst', encoding='utf-8').read(),
    license='The MIT License (MIT)',
    zip_safe=False,
    packages=find_packages(exclude=['tests']),
    install_requires=install_requires,
    tests_require=['nose', 'mock'],
    test_suite='nose.collector',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python',
        'Topic :: Communications',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ]
)
