

#ifndef CYTHON_CASC_TOKENCONFIG_H
#define CYTHON_CASC_TOKENCONFIG_H

#include <vector>
#include <map>
#include <string>

#include "BinaryReader.h"

class TokenConfig {
public:
    typedef std::vector<std::map<std::string, std::string> > tTokenMapList;
private:
    tTokenMapList mValueMap;

public:
    void parse(std::istream& inputStream);
    void parse(const BinaryReader& reader);

    std::size_t size() const {
        return mValueMap.size();
    }

    const tTokenMapList::value_type& operator [] (const std::size_t& index) const {
        return mValueMap.at(index);
    }
};


#endif //CYTHON_CASC_TOKENCONFIG_H
