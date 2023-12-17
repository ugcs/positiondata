from setuptools import setup, find_packages

setup(
    name='PositionData',
    version='0.1.4',
    packages=find_packages(),
    description='Gereferenced CSV data processing',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='SPH Engineering',
    author_email='ayankelevich@ugcs.com',
    url='https://github.com/ugcs/positiondata',
    install_requires=[
        'geopandas',
        'pandas',
        'numpy',
        'rasterio',
        'shapely',
        'geopy',
        'windrose'
    ],
    classifiers=[
        # Classifiers help users find your project
        # For example:
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3.9',
        # Add other classifiers as appropriate for your project
    ],
)
