"""Setup file"""

from setuptools import setup, find_packages


with open('README.rst') as readme_file:
    LONG_DESCRIPTION = readme_file.read()

setup(
    name='simuplot',
    version='0.1b2',  # Modify __version__ in mainwindow.py accordingly
    description='SimuPlot',
    long_description=LONG_DESCRIPTION,
    author='Jérôme Lafréchoux',
    author_email='jlafrechoux@nobatek.inef4.com',
    license='Internal',
    keywords='thermal simulation postprocessing',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    entry_points={'gui_scripts': ['simuplot = simuplot:main']},
    package_data={
        'simuplot': [
            'resources/ui/*.ui', 'resources/ui/*/*.ui',
            'i18n/ts/*.qm'
        ],
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: End Users/Desktop',
        'Environment :: X11 Applications :: Qt',
        #('License :: OSI Approved :: '
        # 'GNU General Public License v2 or later (GPLv2+)'),
        'Operating System :: POSIX :: Linux',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Scientific/Engineering :: Physics',
    ],
    install_requires=[
        'PyQt5>=5.10.0',
        'numpy>=1.12',
        'matplotlib>=2.0.0'
    ],
#     url='',
#     project_urls={
#         'Bug Tracker': '',
#         'Source Code': '',
#     }
)
