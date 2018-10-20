#include <vector>
#include <cstring>
#include "Jenkins96.h"

uint64_t Jenkins96::computeHash(const std::string &str) {
    calcHash(str.c_str(), str.size());
    return mHash;
}

void Jenkins96::calcHash(const char *data, std::size_t size) {
    a = b = c = 0xdeadbeef + static_cast<uint32_t>(size);
    if(size <= 0) {
        mHash = (static_cast<uint64_t>(c) << 32u) | b;
        return;
    }

    const std::size_t newSize = size + ((12 - (size % 12)) % 12);
    std::vector<uint8_t> actualData(newSize);
    memcpy(actualData.data(), data, size);
    const uint32_t* u = reinterpret_cast<const uint32_t*>(actualData.data());

    for(uint32_t i = 0u; i < (newSize - 12); i += 12) {
        a += u[0];
        b += u[1];
        c += u[2];
        mix();
        u += 3;
    }

    a += u[0];
    b += u[1];
    c += u[2];
    final();
    mHash = (static_cast<uint64_t>(c) << 32u) | b;
}

void Jenkins96::mix() {
    a -= c; a ^= rot(c, 4); c += b;
    b -= a; b ^= rot(a, 6); a += c;
    c -= b; c ^= rot(b, 8); b += a;
    a -= c; a ^= rot(c, 16); c += b;
    b -= a; b ^= rot(a, 19); a += c;
    c -= b; c ^= rot(b, 4); b += a;
}

void Jenkins96::final() {
    c ^= b; c -= rot(b, 14);
    a ^= c; a -= rot(c, 11);
    b ^= a; b -= rot(a, 25);
    c ^= b; c -= rot(b, 16);
    a ^= c; a -= rot(c, 4);
    b ^= a; b -= rot(a, 14);
    c ^= b; c -= rot(b, 24);
}
