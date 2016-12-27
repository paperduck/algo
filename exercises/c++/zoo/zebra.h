#ifndef ZEBRA_H
#define ZEBRA_H

#include "mammal.h"
#include <string>
#include <iostream>

using namespace std;

class zebra: public mammal
{
    public:
        zebra();
        zebra(string);
        ~zebra();
        //virtual void jump() override { }
        void jump();
    private:
};

#endif
