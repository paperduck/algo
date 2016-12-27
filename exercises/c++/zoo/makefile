# Rule syntax:
##############
# target ... : [prerequisites ...]
#	recipe
#	...

# How to run:
#   # make              automatically runs `make all`
#   # make all          

all : zoo
	make clean
	clear
	./zoo
zoo : main.o animal.o mammal.o
	g++ -o zoo -std=c++11  main.o animal.o mammal.o
mammal.o : animal.o
	g++ -c -std=c++11 mammal.cpp
animal.o : main.o
	g++ -c -std=c++11 animal.cpp
main.o : main.cpp
	g++ -c -std=c++11  main.cpp
clean :
	rm main.o animal.o mammal.o
