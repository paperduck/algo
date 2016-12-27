#ifndef MAMMAL_H
#define MAMMAL_H

#include "animal.h"
#include <string>

class mammal: public animal
{
    public:
        mammal();
        mammal(string);
        ~mammal();
        string get_hair_color();
        string get_name();
    private:
        string hair_color;
};

#endif
