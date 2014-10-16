from distutils.core import setup

import os
import shutil

if not os.path.exists('scripts'):
    os.makedirs('scripts')
shutil.copyfile('errorless.py', 'errorless')


setup(
    name='errorless',
    version='0.1',
    description='less for compiler errors.',
    author='Martin Fergie',
    author_email='mfergie@gmail.com',
    url='https://github.com/mfergie/errorless,',
    scripts=['errorless'],
)
