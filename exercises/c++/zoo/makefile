# Rule syntax:
##############
# target ... : [prerequisites ...]
#	recipe
#	...

# How to run:
#   # make                  automatically runs first rule
#   # make all          

# compiler
CC=g++
# compilation flags
CFLAGS=-I. -std=c++14
# object files
OBJS = main.o animal.o mammal.o zebra.o

all : zoo
zoo : $(OBJS)
	$(CC) -o zoo $(OBJS) $(CFLAGS)
main.o : main.cpp
	$(CC) -c main.cpp $(CFLAGS)
mammal.o : mammal.cpp mammal.h
	$(CC) -c mammal.cpp $(CFLAGS)
animal.o : animal.cpp animal.h
	$(CC) -c animal.cpp $(CFLAGS)
zebra.o : zebra.cpp zebra.h
	$(CC) -c zebra.cpp $(CFLAGS)
clean :
	rm main.o animal.o mammal.o zoo
