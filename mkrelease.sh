#!/bin/sh

v=$(python setup.py --version)
git tag $v
git push origin master
git push origin $v
python setup.py sdist register upload
