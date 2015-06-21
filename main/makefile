# Rule syntax:
##############
# target ... : [prerequisites ...]
#	recipe
#	...

all : algo
algo : main.o
	g++ -o algo -std=c++11  main.o
	mv algo /tmp
main.o : main.cpp
	g++ -c -std=c++11  main.cpp
clean :
	rm main.o 
