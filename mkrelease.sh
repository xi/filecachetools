#!/bin/sh

v=$(grep __version__ filecachetools.py | sed "s/__version__ = //;s/'//g")
git tag $v
git push origin master
git push origin $v
python setup.py sdist register upload
