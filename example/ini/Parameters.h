#pragma once

#include <map>
#include <string>

#include "ini.h"

class Parameters {
private:
    static Parameters* singleton_optimization_parameters;
    Parameters(std::string filename);
    ~Parameters();

public:
    static void ReadParameters(std::string filename);
    static double GetValueDouble(std::string parameter_name,
                                 std::string parameter_section = "");

private:
    double GetValueDoubleImplementation(std::string parameter_name,
                                        std::string parameter_section = "");

private:
    const std::string filename;
    ini_t* ini_data;
};
