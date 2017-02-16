
#include "mammal.h"


mammal::mammal()
{
    this->hair_color = "<undefined>";
}

mammal::~mammal()
{
    ;
}

string mammal::get_hair_color()
{
    return this->hair_color;
}


