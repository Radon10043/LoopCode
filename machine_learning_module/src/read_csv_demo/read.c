#include <stdlib.h>
#include <stdio.h>
#include <string.h>
int main(int argc, char *argv[])
{
    FILE *in= fopen("/home/yagol/PycharmProjects/LoopCode/machine_learning_module/out/fusion.csv", "r");
    if(in==NULL){
        return -1;
    }
    char buf[1024];
    float mapper[100]={0};
    float sum_prob=0;
    
    while (fgets(buf, sizeof(buf), in) != NULL)
    {
        char * split=strtok(buf,",");
        int temp=atoi(split);
        split=strtok(NULL,",");
        mapper[temp]=atof(split);
        sum_prob+=atof(split);
        printf("%d->%f\n",temp,mapper[temp]);
    }
    printf("===============================\n");
    for(int i=0;i<100;i++){
        printf("%d->%f\n",i,mapper[i]);
    }
    fclose(in);
    printf("sum of prob is :%f\n",sum_prob);
    return 0;
}