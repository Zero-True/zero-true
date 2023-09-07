from setuptools import setup, find_packages

# Read the contents of requirements.txt
with open('zt_backend/requirements.txt') as f:
    requirements = f.read().splitlines()

setup(
    name='zero-true',
    version='0.1',
    packages=find_packages(),
    install_requires=requirements,  # Use the requirements read from the file
    entry_points={
        'console_scripts': [
            'zero-true=zt_cli.cli:start_servers',
        ],
    }
)
