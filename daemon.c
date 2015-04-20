/*
 * =====================================================================================
 *
 *       Filename:  daemon.c
 *
 *    Description:  
 *
 *        Version:  1.0
 *        Created:  06/16/2014 04:58:46 PM
 *       Revision:  none
 *       Compiler:  gcc
 *
 *         Author:  Black REN 
 *   Organization:  
 *
 * =====================================================================================
 */
#include<stdio.h>
#include<stdlib.h>
#include<string.h>
#include<fcntl.h>
#include<sys/types.h>
#include<unistd.h>
#include<sys/wait.h>
#define MAXFILE 65535

si
signal(SIGTERM, sigterm_handler);
void sigterm_handler(int arg)
{
_running = 0;
}
void sigterm_handler(int arg);
volatile sig_atomic_t _running = 1;
int main()
{
pid_t pc,pid;
int i,fd,len,flag = 1;
char *buf="this is a Dameon\n";
len = strlen(buf);
pc = fork(); //第一步
if(pc<0){
printf("error fork\n");
exit(1);
}
else if(pc>0)
exit(0);
pid = setsid(); //第二步[1] 
if (pid < 0)
perror("setsid error");
chdir("/"); //第三步
umask(0); //第四步
for(i=0;i<MAXFILE;i++) //第五步
close(i);
signal(SIGTERM, sigterm_handler);
while( _running )
{
if( flag ==1 &&(fd=open("/tmp/daemon.log",O_CREAT|O_WRONLY|O_APPEND,0600))<0)
{
perror("open");
flag=0;
exit(1);
}
write(fd,buf,len);
close(fd);
usleep(10*1000); //10毫秒
}
}
void sigterm_handler(int arg)
{
_running = 0;
}
