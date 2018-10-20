#include "TokenConfig.h"
#include "String.h"
#include <sstream>


void TokenConfig::parse(const BinaryReader &reader) {
    std::stringstream stream;
    stream.write(reinterpret_cast<const char*>(reader.getData().data()), reader.getData().size());
    parse(stream);
}

void TokenConfig::parse(std::istream &inputStream) {
    bool hasHeader = false;
    std::string currentLine;
    std::vector<std::string> fields;
    std::stringstream tmpStream;
    while(std::getline(inputStream, currentLine)) {
        currentLine = String::trim(currentLine);
        if(currentLine.empty() || currentLine[0] == '#') {
            continue;
        }

        std::vector<std::string> tokens = String::split(currentLine, '|');
        if(!hasHeader) {
            hasHeader = true;
            for(uint32_t i = 0; i < tokens.size(); ++i) {
                const std::string& token = tokens[i];
                std::string::size_type idx = token.find('!');
                if(idx < 0) {
                    fields.push_back(String::trim(token));
                } else {
                    fields.push_back(String::trim(token.substr(0, idx)));
                }
            }
        } else {
            std::map<std::string, std::string> row;
            for(uint32_t i = 0; i < tokens.size(); ++i) {
                row.insert(std::make_pair(fields[i], tokens[i]));
            }

            mValueMap.push_back(row);
        }
    }
}
