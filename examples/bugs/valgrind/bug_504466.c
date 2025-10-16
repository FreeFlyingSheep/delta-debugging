/*
 * Source code for bug_504466.
 * Compile with "gcc -O2 -o bug_504466 bug_504466.c".
 * Run with "/opt/valgrind-fcdaa47/bin/valgrind --tool=none --track-fds=yes ./bug_504466".
 */

#include <unistd.h>

int main(void)
{
    close(0);
    close(0);
    return 0;
}
