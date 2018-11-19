

#ifndef PNG_BLP_MIPMAPGENERATOR_H
#define PNG_BLP_MIPMAPGENERATOR_H

#include <vector>
#include <stdint.h>


class MipMapGenerator {
public:
    std::vector<std::vector<uint32_t> > operator ()(const std::vector<uint32_t>& colors, uint32_t width, uint32_t h);
};


#endif //PNG_BLP_MIPMAPGENERATOR_H
