#!/usr/bin/env python


from setuptools import setup, find_packages

console_entry_points = [
    'erleuchten-testcase=erleuchten.cmds.testcase:main',
    'erleuchten-env=erleuchten.cmds.environment:main',
    'erleuchten-vm=erleuchten.cmds.vm:main',
    'erleuchten-script=erleuchten.cmds.script:main',
    'erleuchten-script-set=erleuchten.cmds.script_set:main',
    'erleuchten-img=erleuchten.cmds.img:main',
]


# setup_requires = ['shutil', 'lxml']
setup_requires = []


setup(name='erleuchten',
      version='0.1',
      description='Test Utilities',
      author='kiriisomer',
      author_email='kiriisomer@hotmail.com',
      url='https://github.com/kiriisomer/erleuchten',
      packages=find_packages(),
      entry_points={'console_scripts': console_entry_points},
      setup_requires=setup_requires
      )
