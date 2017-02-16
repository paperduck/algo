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
        bool get_is_dead();
        string get_name();
        void set_name(string);
        virtual void jump() = 0;    // pure virtual function
    private:
        unsigned short int hunger_level;
        bool is_dead;
    protected:
        string name;
};

#endif
