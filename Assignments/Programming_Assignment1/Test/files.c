// Dynamically read file from disk 
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
/* read file dynamically from disk*/
int readFromDisk(){
    FILE *fp;
    char *line = NULL;
    size_t len = 0;
    ssize_t read;

    fp = fopen("sub.txt", "r");
    if (fp == NULL)
        return 1;
    // store file in a char pointer


    while ((read = getline(&line, &len, fp)) != -1) {
        printf("Retrieved line of length %zu : ", read);
        printf("%s", line);
    }
    return 0;
}


// store all lines using malloc and realloc
char* readfile(char* filename){
    FILE *fp;
    char *line = NULL;
    size_t len = 0;
    ssize_t read;
    char* file = NULL;
    int size = 0;

    fp = fopen(filename, "r");
    if (fp == NULL)
        return NULL;
    // store file in a char pointer
    while ((read = getline(&line, &len, fp)) != -1) {
        size += read;
        file = realloc(file, size);
        strcat(file, line);
    }
    return file;
    
}


