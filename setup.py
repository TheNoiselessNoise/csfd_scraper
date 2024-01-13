from setuptools import setup, find_packages

setup(
    author='XYZT',
    author_email='xyzt@xyzt.cz',
    url='https://github.com/TheNoiselessNoise/csfd_scraper',

    name='x-csfd-scraper',
    version='1.0.1',
    description='Simple scraper for CSFD.cz, a Czech movie database.',

    install_requires=[
        'beautifulsoup4>=4.12.2',
        'requests>=2.31.0',
        'lxml>=4.9.2',
    ],

    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
    ],

    license='MIT',

    packages=find_packages(),

    entry_points={
        'console_scripts': [
            'x_csfd_scraper = x_csfd_scraper.main:main'
        ]
    }
)