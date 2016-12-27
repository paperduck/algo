
#include <iostream>
#include <list>
//#include <stdio.h>
#include <string>

#include "animal.h"
#include "mammal.h"
#include "zebra.h"


using namespace std;

int main ( int argc, const char * argv[] )
{
    // Make a list of animals: 1 mammal, 1 reptile, 1 fish
    list<zebra> animals;
    zebra zebra_1 = zebra("black and white");
    zebra_1.set_name("Steve");
    animals.push_back(move(zebra_1));
    cout << "animals: \n";
    for (list<zebra>::iterator a = animals.begin(); a != animals.end(); ++a)
    {
        cout << a->get_name() << "\n";
    }

    // Feed the animals
    
	return 0;
}


