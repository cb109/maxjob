#!/bin/sh

pyinstaller misc/maxjob.spec
cp maxjob.yml dist

dist/maxjob.exe --help