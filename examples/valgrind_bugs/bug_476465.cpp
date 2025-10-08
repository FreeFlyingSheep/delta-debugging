/*
 * Source code for bug_476465.
 * Use "g++ -O2 -mcpu=neoverse-v1 -o bug_476465 bug_476465.cpp" to compile.
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
