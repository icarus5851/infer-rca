from setuptools import setup, find_packages 

setup(
    name='infer-cli',
    version='2.0.0',
    py_modules=['main'], 
    packages=['modules'], 
    install_requires=[
        'google-genai',
        'langchain-chroma',
        'langchain-google-genai',
        'python-dotenv',
        'rich'
    ],
    entry_points={
        'console_scripts': [
            'infer=main:main',
        ],
    },
)