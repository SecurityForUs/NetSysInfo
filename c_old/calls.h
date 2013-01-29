#ifndef CALLS_H_INCLUDED
#define CALLS_H_INCLUDED

#include <unistd.h>
#include <error.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/sysinfo.h>
#include <utmp.h>
#include <time.h>
#include <stdint.h>

#define MAX_ARGS 256

struct sysinfo sys_info(void){
    struct sysinfo inf;

    sysinfo(&inf);

    return inf;
}

void get_hostname(char *buf){
    gethostname(buf, sizeof(buf));
}

void get_uptime(char *buf){
    struct sysinfo inf = sys_info();

    sprintf(buf, "%lu", inf.uptime);
}

void get_logged_in(char *buf){
    struct utmp *tmp = getutent();

    while(tmp != NULL){
        if(tmp->ut_type == 7){
            char time[256] = {'\0'};

            printf("%s on %s\n", tmp->ut_user, tmp->ut_line);
            struct tm *ti = localtime(&tmp->ut_tv);
            strftime(time, sizeof(time), "%c", ti);
            printf("-!- Time: %s.%d\n", time, tmp->ut_tv.tv_usec);
        }

        tmp = getutent();
    }

    endutent();
}

uint64_t rx_bytes(char *adp){
    char fn[256] = {'\0'};
    uint64_t bytes = 0;

    sprintf(fn, "/sys/class/net/%s/statistics/rx_bytes", adp);

    FILE *fp = NULL;

    if((fp = fopen(fn, "rt")) == NULL){
        return -1;
    }

    fscanf(fp, "%d", &bytes);

    fclose(fp);

    return bytes;
}

int get_args(char *str, char **buff){
    char *tmp = (char*)malloc(sizeof(char*) * strlen(str));
    memset(tmp, 0, sizeof(char*)*strlen(str));
    memcpy(tmp, str, strlen(str));

    char *tok = strtok(tmp, " ");

    int i = 0;

    for(; tok != NULL; i++){
        buff[i] = strdup(tok);
        tok = strtok(NULL, " ");
    }

    free(tmp);

    return i;
}

int read_config(const char *fn, char **buff){
    FILE *fp = fopen(fn, "rt");

    int pos = 0;

    if(fp != NULL){

        char line[MAX_ARGS];
        char **res = (char**)malloc(sizeof(char*) * MAX_ARGS);

        while(fgets(line, MAX_ARGS, fp) != NULL){
            printf("> line = (%s)\n", line);

            get_args(line, res);

            //printf("> read_config: res[0] = %s ; res[1] = %s\n", res[0], res[1]);

            if(res[0] == "net"){
                printf("> storing %s into buff\n", res[1]);
                buff[pos] = res[1];
                printf("> buff[%d] = %s\n", pos, buff[pos]);
            }

            pos++;
        }

        free(res);

        fclose(fp);
    }

    return pos;
}

#endif // CALLS_H_INCLUDED
