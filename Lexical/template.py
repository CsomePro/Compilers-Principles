"""
MIT License

Copyright (c) 2023 Csome陈绍民

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""


template = '''
#include <stdio.h>
#include <fcntl.h>
#include <malloc.h>
#include <string.h>

FILE *file = NULL;
FILE *out = NULL;
#define SIZE_LENGTH 8
unsigned char mp[][128 / SIZE_LENGTH] =
        /// array ///
        ;

char getNextChar(){
    return (char)fgetc(file);
}

void undoGetChar(char c){
    if(c != -1) fseek(file, -1, SEEK_CUR);
}

void error(char* msg) {
    printf("%s\\n", msg);
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
        if(raw[i] == '"' || raw[i] == '\\\\') *p++ = '\\\\';
        *p++ = raw[i];
    }
    *p = 0;
    fprintf(out, "%s \\"%s\\"\\n", token, buffer);
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
            /// code ///
            default:
                error("unknown error");
                return;
        }
    }
}


int main(int argv, char** args) {
    if(argv < 3) {
        printf("Usage: lex file.l target.lex\\n");
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
    printf("success\\n");
}
'''