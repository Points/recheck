import setuptools

install_requires = open('requirements.txt').readlines()

setuptools.setup(
    name="recheck",
    version="0.1.0",
    url="https://github.com/kevinjqiu/recheck",

    author="Kevin J. Qiu",
    author_email="kevin.qiu@points.com",

    description="Re(quirements)Check",
    long_description=open('README.rst').read(),

    packages=setuptools.find_packages(),

    install_requires=install_requires,

    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
    ],
    entry_points={
        'console_scripts': [
            'recheck=recheck.cli:main',
        ],
    },
)
