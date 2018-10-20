

#ifndef CYTHON_CASC_STRING_H
#define CYTHON_CASC_STRING_H

#include <string>
#include <vector>

class String {
private:
    String() { }
    String(const String&) { }

public:
    static std::string toLower(const std::string& s);
    static std::string toUpper(const std::string& s);

    static std::string replaceAll(const std::string &s, char search, char replace);

    static std::string trim(const std::string& s) { return ltrim(rtrim(s)); }
    static std::string rtrim(const std::string& s);
    static std::string ltrim(const std::string& s);

    static std::vector<std::string> split(const std::string& s, char delimiter);
};


#endif //CYTHON_CASC_STRING_H
