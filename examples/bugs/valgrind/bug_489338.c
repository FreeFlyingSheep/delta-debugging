/*
 * Source code for bug_489338.
 * Compile with "gcc -g -O2 -o bug_489338 bug_489338.c".
 * Run with "/opt/valgrind-d97fed7/bin/valgrind --tool=memcheck ./bug_489338".
*/

#include <stdio.h>
#include <math.h>

double __attribute__((optimize("O0"))) value(void)
{
    return -322.5;
}

int main()
{
    double a = value();
    int b = (int)round(a);
    printf("%d\n", b);
    return 0;
}
