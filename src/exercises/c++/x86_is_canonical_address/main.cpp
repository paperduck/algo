/* The 64-bit representation of a 48-bit address is said to be in canonical
form if bits 63 through 48 are either all ones or all zeroes. Implement
X86IsCanonicalAddress(). 
NOTE: This problem description doesn't specify that bits 48 through 63 should
be copies of bit 47, so I didn't implement that.*/

#include <iostream>
#include <ios> // std::hex
using namespace std;

// n:      integral to output in binary
// bytes:  size of n in bytes
ostream & cout_binary(long long n, int bytes){
    for (int i = (bytes*8)-1; i >= 0; i--){
        cout << ((n >> i) & 1);
    }
}

bool x86_is_canonical_address(unsigned long long address){
    address >>= 47;
    unsigned long long bit = (address>>1) & 1;
    for (int i = 1; i <= 16; i++){
        if (((address >>= 1) & 1) != bit){
            return false;
        }
    }
    return true;
}

int main(int argc, char** argv){

    // need to be explicit about sign
    // 64 bits
    //    3210987654321098765432109876543210987654321098765432109876543210
    unsigned long long ns[] = {
    // true
        0b0000000000000000000000000000000000000000000000000000000000000000,
        0b1111111111111111111111111111111111111111111111111111111111111111,
        0b1111111111111111000000000000000000000000000000000000000000000000,
        0b0000000000000000111111111111111111111111111111111111111111111111,
    // false
        0b1111011111111111000000000000000000000000000000000000000000000000,
        0b0000010000000000111111111111111111111111111111111111111111111111,
        0b0111111111111111000000000000000000000000000000000000000000000000,
        0b1000000000000000111111111111111111111111111111111111111111111111,
        0b1111111111111110000000000000000000000000000000000000000000000000,
        0b0000000000000001111111111111111111111111111111111111111111111111
    };
        

    for (int i = 0; i < 10; i++){
        //cout << "sizeof(unsigned long long) = " << sizeof(unsigned long long) << endl;
        //cout << "sizeof(n)       = " << sizeof(n) << endl;
        //cout << "n (decimal)     = " << std::dec << n << endl;
        //cout << "n (hexadecimal) = " << std::hex << n << endl;
        //cout << "n (octal)       = " << std::oct << n << endl;
        cout << "n (binary)      = ";
        cout_binary(ns[i], sizeof(ns[i])) << endl;
        cout << "is canonical:     " << x86_is_canonical_address(ns[i]) << endl;
    }
    return 0;
}

