#!/bin/bash

g++ -c main.cpp -std=c++14
g++ -o main main.o -std=c++14
rm main.o
./main

