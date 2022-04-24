#include <iostream>
#include <bitset>
using namespace std;

extern "C" char* BinaryBitset(int n){
        char data[sizeof(int)*8];
        string s=bitset<sizeof(int)*8>(n).to_string();
        strcpy(data,s.c_str());
        return data;
    }

int main(){
    return 0;
}