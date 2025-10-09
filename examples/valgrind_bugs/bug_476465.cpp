/*
 * Source code for bug_476465.
 * Compile with "g++ -O2 -mcpu=neoverse-v1 -o bug_476465 bug_476465.cpp".
 * Run with "/opt/valgrind-bd4db67/bin/valgrind --tool=none ./bug_476465".
 */

#include <atomic>
#include <iostream>

std::atomic<unsigned long> data;

unsigned long foo()
{
    return data.load(std::memory_order_acquire);
}

int main()
{
    data.store(1, std::memory_order_release);
    std::cout << "data is " << foo() << std::endl;
    return 0;
}
