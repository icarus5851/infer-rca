from setuptools import setup

setup(
    name='infer-cli',
    version='1.0.0',
    py_modules=['main', 'engine', 'log_parser', 'code_extractor'], 
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