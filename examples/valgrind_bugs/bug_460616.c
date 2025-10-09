/*
 * Source code for bug_460616.
 * Compile with "gcc -march=armv8.2-a+dotprod -o bug_460616 bug_460616.c".
 * Run with "/opt/valgrind-d97fed7/bin/valgrind --tool=none ./bug_460616".
 */

#include <stdint.h>
#include <stdio.h>

int main() {
    int8_t op0[16] = {
        (int8_t)0x0, (int8_t)0x1, (int8_t)0x2, (int8_t)0x3,
        (int8_t)0x4, (int8_t)0x5, (int8_t)0x6, (int8_t)0x7,
        (int8_t)0x8, (int8_t)0x9, (int8_t)0xA, (int8_t)0xB,
        (int8_t)0xC, (int8_t)0xD, (int8_t)0xE, (int8_t)0xF,
    };
    int8_t op1[16] = {
        (int8_t)0x0, (int8_t)0x1, (int8_t)0x0, (int8_t)0x1,
        (int8_t)0x0, (int8_t)0x0, (int8_t)0x0, (int8_t)0x0,
        (int8_t)0x1, (int8_t)0x0, (int8_t)0x1, (int8_t)0x0,
        (int8_t)0x1, (int8_t)0x1, (int8_t)0x1, (int8_t)0x1,
    };
    int32_t expected[4] = {
        (int32_t)0x4,
        (int32_t)0x0,
        (int32_t)0x12,
        (int32_t)0x36,
    };
    int32_t result[4] = {
        (int32_t)0xDE,
        (int32_t)0xAD,
        (int32_t)0xBE,
        (int32_t)0xEF,
    };

    asm ("MOV x1, %0" : : "r" (op0));
    asm ("MOV x2, %0" : : "r" (op1));
    asm ("MOV x3, %0" : : "r" (result));
    asm ("LD1 {v0.16b}, [x1], #0x10");
    asm ("LD1 {v1.16b}, [x2], #0x10");
    asm ("SDOT v2.4s, v0.16b, v1.16b");
    asm ("ST1 {v2.4s}, [x3], #0x10");

    for (int i = 0; i < 4; i++) {
        printf(
            "index: %d, expected: %x, result: %x\n",
            i,
            expected[i],
            result[i]
        );
    }
}
