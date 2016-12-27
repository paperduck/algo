# Rule syntax:
##############
# target ... : [prerequisites ...]
#	recipe
#	...

# How to run:
#   # make                  automatically runs first rule
#   # make all          

CC=g++                      # compiler
CFLAGS=-I. -std=c++14       # compilation flags

all : zoo
zoo : main.o animal.o mammal.o
	$(CC) -o zoo main.o animal.o mammal.o $(CFLAGS)
mammal.o : mammal.cpp mammal.h
	$(CC) -c mammal.cpp $(CFLAGS)
animal.o : animal.cpp animal.h
	$(CC) -c animal.cpp $(CFLAGS)
main.o : main.cpp
	$(CC) -c main.cpp $(CFLAGS)
clean :
	rm main.o animal.o mammal.o zoo
