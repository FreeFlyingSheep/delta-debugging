/*
 * Source code for bug_392146.
 * Compile with "gcc -o bug_392146 bug_392146.c".
 * Run with "/opt/valgrind-bd4db67/bin/valgrind --tool=none ./bug_392146".
 */

int main(void)
{
    unsigned long long reg;
    asm ("mrs %x[reg], ID_AA64PFR0_EL1" : [reg] "=r" (reg));
    return (reg & 0xE00000) == 0;
}
