#include "Parameters.h"

#include <stdio.h>

#include <exception>

Parameters *Parameters::singleton_optimization_parameters = NULL;

Parameters::Parameters(std::string filename_) : filename(filename_) {
    FILE *fp = fopen(filename.c_str(), "r");
    if (fp == NULL) {
        throw std::runtime_error("Error: file with parameters can not be read");
    }

    fseek(fp, 0, SEEK_END);
    int size = ftell(fp);
    fseek(fp, 0, SEEK_SET);
    char *data = (char *)malloc(size + 1);
    fread(data, 1, size, fp);
    data[size] = '\0';
    fclose(fp);

    ini_data = ini_load(data, NULL);
    free(data);
}

Parameters::~Parameters() { ini_destroy(ini_data); }

void Parameters::ReadParameters(std::string filename) {
    if (singleton_optimization_parameters != NULL)
        throw std::runtime_error("Error: reading parameters twice");
    singleton_optimization_parameters = new Parameters(filename);
}

double Parameters::GetValueDouble(std::string parameter_name,
                                  std::string parameter_section) {
    if (singleton_optimization_parameters == NULL)
        throw std::runtime_error("Error: reading parameter " + parameter_name +
                                 " value before parameters are read");
    return singleton_optimization_parameters->GetValueDoubleImplementation(
        parameter_name, parameter_section);
}

double Parameters::GetValueDoubleImplementation(std::string parameter_name,
                                                std::string parameter_section) {
    int section_index =
        parameter_section.size() == 0
            ? INI_GLOBAL_SECTION
            : ini_find_section(ini_data, parameter_section.c_str(), 0);

    int value_index =
        ini_find_property(ini_data, section_index, parameter_name.c_str(), 0);
    char const *value_str =
        ini_property_value(ini_data, section_index, value_index);
    if (value_str == NULL)
        throw std::runtime_error("Error: parameter \"" + parameter_name +
                                 "\" does not exist in section \"" +
                                 parameter_section + "\"");
    const double val = std::stod(value_str);
    return val;
}
