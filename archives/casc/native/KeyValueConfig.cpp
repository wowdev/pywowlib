

#include "KeyValueConfig.h"
#include "String.h"

#include <sstream>

void KeyValueConfig::parse(const BinaryReader &reader) {
    std::stringstream stream;
    stream.write(reinterpret_cast<const char*>(reader.getData().data()), reader.getData().size());
    parse(stream);
}

void KeyValueConfig::parse(std::istream &inputStream) {
    std::string curLine;
    while(std::getline(inputStream, curLine)) {
        curLine = String::trim(curLine);
        if(curLine.empty() || curLine[0] == '#') {
            continue;
        }

        std::vector<std::string> tokens = String::split(curLine, '=');
        if(tokens.size() != std::size_t(2)) {
            throw std::runtime_error("Invalid token amount, expected 2");
        }

        mValues.insert(std::make_pair(String::trim(tokens[0]), String::split(String::trim(tokens[1]), ' ')));
    }
}
