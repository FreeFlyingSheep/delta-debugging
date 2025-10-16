/*
 * Source code for bug_508154.
 * Compile with "gcc -O2 -o bug_508154 bug_508154.c".
 * Run with "/opt/valgrind-49dccaf/bin/valgrind --tool=memcheck ./bug_508154".
 */

#include <fcntl.h>
#include <stdio.h>
#include <unistd.h>

int main(void)
{
    if (fchownat(AT_FDCWD, "non_existent_file", 0, 0, 0) == -1) {
        perror("fchownat");
        return -1;
    }
    return 0;
}
