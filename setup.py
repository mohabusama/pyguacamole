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
    author_email='mohab.usama@gmail.com',
    description=('A Guacamole python client library.'),
    long_description=open('README.rst').read(),
    license=open('LICENSE').read(),
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
        'Programming Language :: Python',
        'Topic :: Communications',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ]
)
