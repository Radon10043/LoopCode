#include <stdio.h>
#include <stdlib.h>
#include <time.h>
int main()
{
    int ret = 0;
    float max = 99.9;
    srand((unsigned int)time(NULL));
    for (int i = 0; i < 10; i++)
    {
        ret = rand() % (int)max;
        printf("%d ", ret);
    }
    return 0;
}