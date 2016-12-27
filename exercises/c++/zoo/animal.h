#ifndef ANIMAL_H
#define ANIMAL_H

#include <string>

using namespace std;

class animal
{
    public:
        animal();
        ~animal();
        bool feed();
        virtual string get_name() = 0;  // pure virtual function
        bool get_is_dead();
    private:
        unsigned short int hunger_level;
        bool is_dead;
    protected:
        string name;
};

#endif
