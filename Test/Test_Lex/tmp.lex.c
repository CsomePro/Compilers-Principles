
#include <stdio.h>
#include <fcntl.h>
#include <malloc.h>
#include <string.h>

FILE *file = NULL;
FILE *out = NULL;
#define SIZE_LENGTH 8
unsigned char mp[][128 / SIZE_LENGTH] =
        {
{0,0,0,0,0,0,0,0,0,0,0,0,32,0,0,0},
{0,6,0,0,1,0,0,0,0,0,0,0,0,0,0,0},
{0,0,0,0,0,0,0,0,0,0,0,0,0,2,0,0},
{0,0,0,0,0,0,0,0,0,0,0,0,0,16,0,0},
{0,6,0,0,1,0,0,0,0,0,0,0,0,0,0,0},
{0,0,0,0,0,0,0,0,0,0,0,0,64,0,0,0},
{0,0,0,0,0,0,0,0,0,0,0,0,0,0,8,0},
{0,0,0,0,0,0,0,0,0,0,0,0,32,0,0,0},
}
        ;

char getNextChar(){
    return (char)fgetc(file);
}

void undoGetChar(char c){
    if(c != -1) fseek(file, -1, SEEK_CUR);
}

void error(char* msg) {
    printf("%s\n", msg);
    exit(0);
}

int check(int id, char x) {
    return (mp[id][x / SIZE_LENGTH] & (1 << (x % SIZE_LENGTH))) != 0;
}

void output(char* token, char* raw) {
    size_t length = strlen(raw);
    char* buffer = calloc(1, length * 2 + 1);
    char* p = buffer;
    for(size_t i = 0; i < length; ++i) {
        if(raw[i] == '"' || raw[i] == '\\') *p++ = '\\';
        *p++ = raw[i];
    }
    *p = 0;
    fprintf(out, "%s \"%s\"\n", token, buffer);
    free(buffer);
    buffer = NULL;
    p = NULL;
}


void next(){
    int state = 0;
    char* buffer = calloc(1, 1024), *p = buffer;
    while (1) {
        char c = getNextChar();
        switch (state) {
            case 0: 
if(check(0, c)) { *p++ = c; state=2; }
else if(check(1, c)) { *p++ = c; state=3; }
else if(check(2, c)) { *p++ = c; state=1; }
else if(c == -1) { return; }
else { undoGetChar(c); *p = 0; error("Lex Error"); }
break;
case 2: 
if(check(3, c)) { *p++ = c; state=5; }
else { undoGetChar(c); *p = 0; error("Lex Error"); }
break;
case 3: 
if(check(4, c)) { *p++ = c; state=3; }
else { undoGetChar(c); p = buffer; state = 0; }
break;
case 1: 
if(check(5, c)) { *p++ = c; state=4; }
else { undoGetChar(c); *p = 0; error("Lex Error"); }
break;
case 5: 
if(check(6, c)) { *p++ = c; state=6; }
else { undoGetChar(c); *p = 0; error("Lex Error"); }
break;
case 4: 
{ undoGetChar(c); *p = 0; output("IF", buffer); p = buffer; state = 0; }
break;
case 6: 
if(check(7, c)) { *p++ = c; state=7; }
else { undoGetChar(c); *p = 0; error("Lex Error"); }
break;
case 7: 
{ undoGetChar(c); *p = 0; output("ELSE", buffer); p = buffer; state = 0; }
break;

            default:
                error("unknown error");
                return;
        }
    }
}


int main(int argv, char** args) {
    if(argv < 3) {
        printf("Usage: lex file.l target.lex\n");
        return 0;
    }
    file = fopen(args[1], "r+");
    if(file == NULL) {
        printf("Open %s Error.", args[1]);
        return 0;
    }
    out = fopen(args[2], "w");
    if(file == NULL) {
        printf("Open %s Error.", args[2]);
        return 0;
    }
    next();
    fclose(file);
    fclose(out);
    printf("success\n");
}
