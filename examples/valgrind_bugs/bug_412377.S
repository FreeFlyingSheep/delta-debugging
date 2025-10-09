/*
 * Source code for bug_412377.
 * Compile with "gcc -nostdlib -o bug_412377 bug_412377.S".
 * Run with "/opt/valgrind-bd4db67/bin/valgrind --tool=none ./bug_412377".
 */

.text
.globl _start
_start:
    dc      cvac, x0
    mov     x0, #0
    mov     w8, #93
    svc     #0
