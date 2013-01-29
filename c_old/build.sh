#!/bin/sh

FILES=([0]=main [1]=client [2]=landing_zone)

for file in ${FILES[*]}; do
  rm -rf $file $file.o
  gcc -Wall -g -c $file.c -o $file.o
  g++ -o $file $file.o
done
