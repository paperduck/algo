#include <iostream>

using namespace std;

int main(int argc, char** argv){

    unsigned int i = 1; // need to be explicit about sign

    for (int x = 1; x <= 35; x++){
        cout << x << ": i = " << i << endl;
        i<<=1;
    }

    return 0;
}

