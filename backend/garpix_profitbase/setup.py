from setuptools import setup, find_packages
from os import path
from m2r import convert
from django.conf import settings

with open(path.join(settings.BASE_DIR, '..', 'README.md'), encoding='utf-8') as f:
    long_description = convert(f.read())

setup(
    name='garpix_profitbase',
    version='1.3.1',
    description='',
    long_description=long_description,
    url='https://github.com/garpixcms/garpix_profitbase',
    author='Garpix LTD',
    author_email='info@garpix.com',
    license='MIT',
    packages=find_packages(exclude=['testproject', 'testproject.*']),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Framework :: Django',
        'Programming Language :: Python :: 3.8',
    ],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'garpixcms >= 1.7.1',
        'transliterate == 1.10.2',
        'requests == 2.26.0',
    ],
)
