

#include "String.h"
#include "assert.h"
#include <iostream>
#include <sstream>
#include <cctype>

std::string String::rtrim(const std::string &s) {
    if(s.empty()) {
        return s;
    }

    std::string::size_type index = s.length() - 1;
    while(std::isspace(s[index]) && index >= 0) {
        --index;
    }

    if(index < 0) {
        return s;
    }

    return s.substr(0, index + 1);
}

std::string String::ltrim(const std::string &s) {
    if(s.empty()) {
        return s;
    }

    std::string::size_type maxSize = s.length();
    std::string::size_type index = 0;
    while(std::isspace(s[index]) && index < maxSize) {
        ++index;
    }

    return s.substr(index);
}

std::vector<std::string> String::split(const std::string& s, char delimiter) {
    std::stringstream stream(s);
    std::string token;
    std::vector<std::string> tokens;
    while(std::getline(stream, token, delimiter)) {
        tokens.push_back(token);
    }

    return tokens;
}

std::string String::toLower(const std::string &s) {
    std::string ret;
    ret.resize(s.size());
    for(std::string::size_type i = 0; i < s.size(); ++i) {
        ret[i] = static_cast<char>(std::tolower(s[i]));
    }

    return ret;
}

std::string String::toUpper(const std::string &s) {
    std::string ret;
    ret.resize(s.size());
    for(std::string::size_type i = 0; i < s.size(); ++i) {
        ret[i] = static_cast<char>(std::toupper(s[i]));
    }

    return ret;
}

std::string String::replaceAll(const std::string &s, char search, char replace) {
    std::string ret;
    ret.resize(s.size());
    for(std::string::size_type i = 0; i < s.size(); ++i) {
        if(s[i] == search) {
            ret[i] = replace;
        } else {
            ret[i] = s[i];
        }
    }

    return ret;
}
