#ifndef MAMMAL_H
#define MAMMAL_H

#include "animal.h"
#include <string>

class mammal: public animal
{
    public:
        mammal();
        ~mammal();
        string get_hair_color();
    protected:
        string hair_color;
    private:
};

#endif
