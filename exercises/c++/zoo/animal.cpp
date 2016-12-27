#include "animal.h"

animal::animal()
{
    this->hunger_level = 0;
    this->name = "<undefined>";
}

animal::~animal()
{
    ;
}

bool animal::feed()
{
    if (hunger_level > 0)
    {
        hunger_level -= 1;
    }
}

bool animal::get_is_dead()
{
    return this->is_dead;
}

string animal::get_name()
{
    return this->name;
}

void animal::set_name(string new_name)
{
    this->name = new_name;
}

