

#ifndef CYTHON_CASC_KEYVALUECONFIG_H
#define CYTHON_CASC_KEYVALUECONFIG_H

#include <map>
#include <string>
#include <vector>

#include "BinaryReader.h"

class KeyValueConfig {
    typedef std::map<std::string, std::vector<std::string> > tKeyValueMap;

    tKeyValueMap mValues;

public:
    void parse(std::istream& inputStream);
    void parse(const BinaryReader& reader);

    std::vector<std::string> operator [] (const std::string& key) const {
        return mValues.at(key);
    }
};


#endif //CYTHON_CASC_KEYVALUECONFIG_H
