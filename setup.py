from setuptools import setup, find_packages

setup(
    name='your-package-name',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        'fastapi',
        'pydantic',
        'uvicorn',
        # Add other dependencies here
    ],
    entry_points={
        'console_scripts': [
            'your-app-name=app.api.v1.endpoints:app',  # Replace with your actual entry point
        ],
    },
)