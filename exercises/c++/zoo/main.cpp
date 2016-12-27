
#include "animal.h"
#include <iostream>
#include <list>
#include "mammal.h"
//#include <stdio.h>
#include <string>

using namespace std;

int main ( int argc, const char * argv[] )
{
    // Make a list of animals: 1 mammal, 1 reptile, 1 fish
    list<mammal> animals;
    mammal zebra_1 = mammal("brown");
    animals.push_back(move(zebra_1));
    cout << "animals: \n";
    for (list<mammal>::iterator a = animals.begin(); a != animals.end(); ++a)
    {
        cout << (*a).get_name() << "\n";
    }

    // Feed the animals
    
	return 0;
}


