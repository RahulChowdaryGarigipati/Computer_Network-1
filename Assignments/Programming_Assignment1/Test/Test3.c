#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/socket.h>
#include <arpa/inet.h>
#include <regex.h>
#include <string.h>

#define MAX 1024 // max size of buffer

// function to check if the email address is valid
int checkEmail(char *email)
{
    // regex to check if the email address is valid
    // char *regex = "^[a-zA-Z0-9_+&*-]+(?:\\.[a-zA-Z0-9_+&*-]+)*@(?:[a-zA-Z0-9-]+\\.)+[a-zA-Z]{2,7}$";
    char *regex = "^\\w+@[a-zA-Z_]+?\\.[a-zA-Z]{2,3}$";
    regex_t re;
    if (regcomp(&re, regex, REG_EXTENDED|REG_NOSUB) != 0)
        return 0;
    int status = regexec(&re, email, 0, NULL, 0);
    regfree(&re);
    if (status != 0)
        return 0;
    return 1;
}

// function to check if the IP address is valid
int checkIP(char *ip)
{
    // regex to check if the IP address is valid
    char *regex = "^([0-9]{1,3}\\.){3}[0-9]{1,3}$";
    regex_t re;
    if (regcomp(&re, regex, REG_EXTENDED|REG_NOSUB) != 0)
        return 0;
    int status = regexec(&re, ip, 0, NULL, 0);
    regfree(&re);
    if (status != 0)
        return 0;
    return 1;
}

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
    // close the file
    // fclose(fp);
    return file;
    
}


// function to check if file exists
int fileExists(char *file)
{
    FILE *fp;
    if ((fp = fopen(file, "r")) == NULL)
        return 0;
    fclose(fp);
    return 1;
}

// main function
int main(int argc, char *argv[])
{

    // print argc
    if (argc != 4)
    {
        fprintf(stderr, "Usage: %s <smtp server ip> <to email> <email file>", argv[0]);
        return 1;
    }

    // check if the IP address is valid
    if (!checkIP(argv[1]))
    {
        fprintf(stderr, "Invalid IP address");
        return 1;
    }
    
    // check if the from email is valid
    if (!checkEmail(argv[2]))
    {
        fprintf(stderr, "Invalid from email");
        return 1;
    }
    
    
    // check if the email file is valid
    if (!fileExists(argv[3]))
    {
        fprintf(stderr, "Invalid email file");
        return 1;
    }

    // create a socket
    int fd = socket(AF_INET, SOCK_STREAM, 0);
    if ((fd = socket(AF_INET, SOCK_STREAM, 0)) < 0) {
	perror("cannot create socket");
	return 0;
}

    // create a socket address
    struct sockaddr_in addr;
    memset((char *)&addr, 0, sizeof(addr));
    addr.sin_family = AF_INET;
    addr.sin_port = htons(25); // SMTP port
    addr.sin_addr.s_addr = inet_addr(argv[1]);

    // // put the server address in the socket address
    // memccpy((char *)&addr, (char *)addr->h_addr, server->h_length, 1);

    // connect to the server
    if (connect(fd, (struct sockaddr *)&addr, sizeof(addr)) < 0)
    {
        fprintf(stderr, "Error connecting to the server");
        return 1;
    }

    // read the response from the server
    char buffer[MAX];
    int n = read(fd, buffer, sizeof(buffer));
    buffer[n] = '\0';
    printf("%s", buffer);

    // check if the response is 220
    if (strncmp(buffer, "220", 3) != 0)
    {
        fprintf(stderr, "Error connecting to the server");
        return 1;
    }

    // send HELO command and print server response
    char *msg = "HELO\r";
    write(fd, msg, strlen(msg));
    n = read(fd, buffer, sizeof(buffer));
    buffer[n] = '\0';
    printf("%s", buffer);

    // check if the response is 250
    if (strncmp(buffer, "250", 3) != 0)
    {
        fprintf(stderr, "Error connecting to the server");
        return 1;
    }

    // send MAIL FROM command and print server response
    // define msg1 and concatenate the email address
    char msg1[100];
    strcpy(msg1, "MAIL FROM: ");
    strcat(msg1, argv[2]);
    strcat(msg1, "\r");
    // char *msg1 = "MAIL FROM: ";
    // strcat(msg1, argv[2]);
    // strcat(msg1, "\r");
    write(fd, msg1, strlen(msg1));
    n = read(fd, buffer, sizeof(buffer));
    buffer[n] = '\0';
    printf("%s", buffer);

    // check if the response is 250
    if (strncmp(buffer, "250", 3) != 0)
    {
        fprintf(stderr, "Error connecting to the server");
        return 1;
    }

    // define msg2 and 
    // send RCPT TO command and print server response
    char msg2[100];
    strcpy(msg2, "RCPT TO: ");
    strcat(msg2, argv[2]);
    strcat(msg2, "\r");
    
    // char *msg2 = "RCPT TO: ";
    // strcat(msg2, argv[2]);
    // strcat(msg2, "\r");
    write(fd, msg2, strlen(msg2));
    n = read(fd, buffer, sizeof(buffer));
    buffer[n] = '\0';
    printf("%s", buffer);

    // check if the response is 250
    if (strncmp(buffer, "250", 3) != 0)
    {
        fprintf(stderr, "Error connecting to the server");
        return 1;
    }

    // send DATA command by reading a file and print server response
    char msg3[10];
    strcpy(msg3, "DATA\r");
    // char *msg3 = "DATA\r";
    write(fd, msg3, strlen(msg3));
    n = read(fd, buffer, sizeof(buffer));
    buffer[n] = '\0';
    printf("%s", buffer);

    // check if the response is 354
    if (strncmp(buffer, "354", 3) != 0)
    {
        fprintf(stderr, "Error connecting to the server");
        return 1;
    }

    // read the file and send it to the server
    // char *file = readfile(argv[3]);
    // // write the file to the server
    // printf("%s", file);
    // write(fd, file, strlen(file));

    // send the file to the server
    FILE *fp;
    char *line = NULL;
    size_t len = 0;
    ssize_t read_l;
    fp = fopen(argv[3], "r");
    if (fp == NULL)
        exit(EXIT_FAILURE);
    while ((read_l = getline(&line, &len, fp)) != -1) {
        printf("%s", line);
        
        // add \r to the end of the line
        strcat(line, "\r\n");
        write(fd, line, strlen(line));
    }
    fclose(fp);


    // write(fd, "Subject: Hello\r\n\r\n", strlen("Subject: Hello\r\n\r\n"));
    // write(fd, "Hello World\r\n", strlen("Hello World\r\n"));
    write(fd, ".\r", strlen(".\r"));

    // send a new line and a period
    char *msg4 = ".\r\n";
    write(fd, msg4, strlen(msg4));

    // FILE *fp = fopen(argv[4], "r");
    // char line[1024];
    // while (fgets(line, sizeof(line), fp))
    // {
    //     write(fd, line, strlen(line));
    // }
    // fclose(fp); // close the file

    // send the end of data command and print server response
    // char *msg4 = "\r.\r";
    // char *msg4 = ".";
    // write(fd, msg4, strlen(msg4));


    n = read(fd, buffer, sizeof(buffer));
    buffer[n] = '\0';
    printf("%s", buffer);
 
    // check if the response is 250
    if (strncmp(buffer, "250", 3) != 0)
    {
        fprintf(stderr, "Error connecting to the server");
        return 1;
    }

    // send QUIT command and print server response
    char *msg5 = "QUIT\r";
    write(fd, msg5, strlen(msg5));
    n = read(fd, buffer, sizeof(buffer));
    buffer[n] = '\0';
    printf("%s", buffer);

    // check if the response is 221
    if (strncmp(buffer, "221", 3) != 0)
    {
        fprintf(stderr, "Error connecting to the server");
        return 1;
    }

    // close the socket
    close(fd);
    
    return 0;
}