int check(int a[]) {
    int i;
    int ans;
    i = 0;
    ans = 1;
    do{
        if(a[i] == 0) ans = ans + 1;
        i = i + 1;
    }while(i < 10);
    return ans != 1;
}

int main(void) {
    int a[10];
    int i;
    int j;
    i = 0;
    do{
        j = 1;
        do{
            if(a[i] != 1) { j = j + 1; }
            i = i + 1;
            i = i % 10;
        }while(j < 3);
        if(a[i] != 0) {
            do{
                i = i + 1;
                i = i % 10;
            }while(a[i] != 0);
        }
        a[i] = 1;
    } while(check(a));
    return i + 1;
}