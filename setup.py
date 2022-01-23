import setuptools

import os

readme_filename = os.path.join(os.path.dirname(__file__), 'README.md')
with open(readme_filename, 'r') as fh:
    long_description = '> Description from GitHub `readme.md`:\n'+\
                       fh.read()

setuptools.setup(
    name='ConsurfDB-client-API',
    version='1.0',
    packages=setuptools.find_packages(),
    url='https://github.com/matteoferla/ConsurfDB-client-API',
    license='MIT',
    author='Matteo Ferla',
    author_email='matteo.ferla@gmail.com',
    description='Python3 client API for ConsurfDB',
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: Bio-Informatics',
        # 'Topic :: Scientific/Engineering :: Chemistry',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        "Operating System :: OS Independent",
    ],
    install_requires=['typing-extensions']
)
