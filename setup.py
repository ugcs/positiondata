from setuptools import setup, find_packages

# Read dependencies from requirements.txt, excluding certain packages
with open('requirements.txt') as f:
    requirements = [line.strip() for line in f if line.strip() and not line.startswith(('setuptools', 'twine', 'wheel'))]

setup(
    name='PositionData',
    version='0.1.7',
    packages=find_packages(),
    description='Georeferenced CSV data processing',
    long_description=open('DEVGUIDE.md').read(),
    long_description_content_type='text/markdown',
    author='SPH Engineering',
    author_email='ayankelevich@ugcs.com',
    url='https://github.com/ugcs/positiondata',
    install_requires=requirements,
    classifiers=[
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        # Add other classifiers as appropriate for your project
    ],
)
