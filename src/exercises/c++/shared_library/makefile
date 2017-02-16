# Rule syntax:
##############
# target ... : [prerequisites ...]
#	recipe
#	...

# How to run:
#   # make              automatically runs `make all`
#   # make all          

all : lib
lib : main.o shared.o
	g++ -o lib -std=c++11  main.o shared.o
main.o : main.cpp
	g++ -c -std=c++11  main.cpp shared.cpp
shared.o : shared.cpp shared.h
	g++ -c -std=c++11 shared.cpp 
clean :
	rm main.o shared.o lib
