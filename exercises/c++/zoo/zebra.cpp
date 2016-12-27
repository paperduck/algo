
#include "zebra.h"

zebra::zebra()
{
    this->name = "<undefined>";
}

zebra::zebra(string hair_color)
{
    this->hair_color = hair_color;
}

zebra::~zebra()
{
    ;
}

void zebra::jump()
{
    cout << "wee!\n";
}

