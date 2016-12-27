
#include "mammal.h"


mammal::mammal()
{
    this->hair_color = "<not set>";
}

mammal::mammal(string hair_color)
{
    this->hair_color = hair_color;
}

mammal::~mammal()
{
    ;
}

string mammal::get_hair_color()
{
    return this->hair_color;
}

string mammal::get_name()
{
    return this->name;
}




