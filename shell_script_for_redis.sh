#!/bin/bash
cd /afs/andrew.cmu.edu/usr21/lmorishe/private/submission/
tar xvf redis-sample.tar
cd ./redis/redis-stable/src
./redis-server --port 6389 --protected-mode no 
