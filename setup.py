import setuptools

with open('README.md', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name='afsm', # Replace with your own username
    version='0.0.1',
    author='Eugeny Volobuev',
    author_email='qulert@gmail.com',
    description='Simple asyncio FSM',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/jintwo/afsm',
    packages=setuptools.find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.7',
)
