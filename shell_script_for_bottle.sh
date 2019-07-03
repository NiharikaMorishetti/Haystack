#!/bin/bash
cd /afs/andrew.cmu.edu/usr21/lmorishe/private/submission/
tar xvf virenv-sample.tar
source ./virenv_2/virtualenv-15.2.0/vir/bin/activate
cd ./bottle_code/
python bottleserver.py
