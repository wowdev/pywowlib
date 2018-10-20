

#ifndef CYTHON_CASC_JENKINS96_H
#define CYTHON_CASC_JENKINS96_H

#include <stdint.h>
#include <cstdlib>
#include <string>

class Jenkins96 {
    uint32_t a, b, c;
    uint64_t mHash;

    static uint32_t rot(uint32_t x, uint32_t k) {
        return (x << k) | (x >> (32 - k));
    }

    void mix();
    void final();
    void calcHash(const char* data, std::size_t size);

public:
    uint64_t computeHash(const std::string& str);
};


#endif //CYTHON_CASC_JENKINS96_H
