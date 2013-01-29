/**
 * This is simply a testing file for ideas that I'm unsure of working.
 **/
#include "calls.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int main(int argc, char *argv[]){
    char **res = NULL;

    printf("Looking to split a string into parts...\n");

    char *tmp = "split";

    res = (char**)malloc(sizeof(char*) * MAX_ARGS);
/*
    int c = get_args(tmp, res);

    printf("Got %d parts.\n", c);

    int i = 0;

    for(; i < c; i++){
        printf("Part %d: %s (%d)\n", i, res[i], strlen(res[i]));
    }
*/
    int c = read_config("conf.nsi", res);
    int i = 0;

    for(; i < c; i++){
        printf("%s\n", res[i]);
    }
    free(res);

    return 0;
}
