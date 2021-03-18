#!/usr/bin/env python3

import scipy as sp
import numpy as np
import pandas as pd
import subprocess
import argparse
import subprocess
from scipy.optimize import root, minimize
from collections import namedtuple

from ipdb import set_trace

fmt_value = "{:20.16g}"

parser = argparse.ArgumentParser(
    description="""Optimize / find root of a model in external progam""",
    usage='use "%(prog)s --help" for more information',
)

parser.add_argument(
    "--optimization-choice",
    type=str,
    required=True,
    choices=["minimum", "root"],
    help="""Optimization: look for minimum or a root""",
)

parser.add_argument(
    "--optimization-solver-minimization",
    type=str,
    required=False,
    default="Nelder-Mead",
    help="""A valid minimization solver name. See
https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.minimize.html#scipy.optimize.minimize """,
)

parser.add_argument(
    "--optimization-solver-root",
    type=str,
    required=False,
    default="hybr",
    help="""A valid root-finding solver name. See
https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.root.html#scipy.optimize.root""",
)

parser.add_argument(
    "--optimization-tolerance",
    type=float,
    default=1e-4,
    help="""Tolerance for optimization""",
)

parser.add_argument(
    "--parameter-passing",
    type=str,
    required=True,
    choices=["ini", "data-txt", "header-const", "header-define"],
    help="""How to pass parameters to the program: by writing the parameters to an ini file,
    a txt file with data, header with const double values or header with defines""",
)

parser.add_argument(
    "--program-command",
    type=str,
    required=True,
    help="""The program or script to execute [shell command]""",
)

parser.add_argument(
    "--parameter-file",
    type=str,
    required=True,
    help="""File into which the parameters are written""",
)

parser.add_argument(
    "--result-file",
    type=str,
    required=True,
    help="""File that contains the result of the model""",
)

parser.add_argument(
    "--calculation-cache-file",
    type=str,
    default=None,
    required=False,
    help="""If set, the results of program calls are cached and reused""",
)

parser.add_argument(
    "--calculation-cache-tol",
    type=float,
    default=1e-8,
    required=False,
    help="""If program results are cached, the lookup of values returns the first match with this tolerance in parameter values""",
)

t_parameter = namedtuple("parameter", "name min max value")


def parameter_verifier(s):
    try:
        opt = s.split(":")
        assert len(opt) == 3
        name, val_min, val_max = opt[0], float(opt[1]), float(opt[2])
        return t_parameter(name, val_min, val_max, (val_max - val_min) / 2.0)
    except Exception as e:
        raise argparse.ArgumentTypeError(
            "Error converting " + str(s) + ", " + str(e)
        )


parser.add_argument(
    "--parameter",
    type=parameter_verifier,
    default=[],
    action="append",
    help="List of parameters to pass to the model. Format : --parameter=<name>:min:max, --parameter=phi:-3.14142:+3.14142"
    "",
)


def generate_parameter_file(filename, parameters, parameter_passing):
    # choices=["ini", "data-txt", "header-const", "header-define"],
    with open(filename, "wt") as f:
        if "header-" in parameter_passing:
            f.write("#pragma once\n")
        elif "ini" == parameter_passing:
            f.write("[parameters]\n")

        fmt_line = {
            "ini": "{:s} = " + fmt_value + "\n",
            "data-txt": fmt_value + "\n",
            "header-const": "const double {:s} = " + fmt_value + ";\n",
            "header-define": "#define {:s} " + fmt_value + "\n",
        }[parameter_passing]

        for parameter in parameters:
            f.write(fmt_line.format(parameter.name, parameter.value))


def run_program(
    program, parameter_file, parameter_passing, value_file, parameters
):
    generate_parameter_file(parameter_file, parameters, parameter_passing)
    subprocess.run(program, shell=True, check=True)
    with open(value_file, "r") as f:
        value = float(f.readline())
    return value


class CalculationCache:
    def __init__(self, filename, tolerance):
        self.filename = filename
        self.tolerance = tolerance
        try:
            self.df = pd.read_csv(self.filename, sep=r"\s+")
        except (FileNotFoundError, pd.errors.EmptyDataError) as e:
            self.df = None

    def save(self):
        self.df.to_csv(self.filename, sep="\t")

    def look_up_results(self, program, parameters):
        if self.df is None:
            return None
        index = self.df["program"] == program
        for parameter in parameters:
            index = index & (
                abs(self.df[parameter.name] - parameter.value)
                < self.tolerance * parameter.value
            )
        n_match = np.sum(index.values)
        if n_match == 0:
            return None
        elif n_match > 1:
            raise Exception(
                "Error: more than one value in the cache matches the lookup"
            )
        val = self.df[index]["value"].values[0]
        return val

    def add_results(self, program, parameters, value):
        if self.df is None:
            self.df = pd.DataFrame(
                columns=[
                    "program",
                ]
                + [parameter.name for parameter in parameters]
                + [
                    "value",
                ]
            )
        d = {p.name: p.value for p in parameters}
        d["program"] = program
        d["value"] = value
        self.df = self.df.append(d, ignore_index=True)


def make_optimization_function(
    calculation_cache,
    program,
    parameter_file,
    parameter_passing,
    value_file,
    parameters,
):
    def fun(x, *args):
        new_parameters = []
        for xx, parameter in zip(x, parameters):
            new_parameters.append(parameter._replace(value=xx))

        if calculation_cache is not None:
            result = calculation_cache.look_up_results(program, new_parameters)
            if result is not None:
                return result
        print("Running program with paremeters: ")
        parameter_line = "{{:20s}} = {:s} [ {:s}, {:s} ]".format(
            fmt_value, fmt_value, fmt_value
        )
        for p in new_parameters:
            print(parameter_line.format(p.name, p.value, p.min, p.max))
        result = run_program(
            program,
            parameter_file,
            parameter_passing,
            value_file,
            new_parameters,
        )
        if calculation_cache is not None:
            calculation_cache.add_results(program, new_parameters, result)
            calculation_cache.save()
        return result

    return fun


if __name__ == "__main__":
    args = parser.parse_args()
    if args.calculation_cache_file is not None:
        calculation_cache = CalculationCache(
            args.calculation_cache_file, args.calculation_cache_tol
        )
    else:
        calculation_cache = None

    print(args)
    fun = make_optimization_function(
        calculation_cache,
        args.program_command,
        args.parameter_file,
        args.parameter_passing,
        args.result_file,
        args.parameter,
    )

    x0 = [p.value for p in args.parameter]
    if args.optimization_choice == "minimum":
        optimization_result = minimize(
            fun,
            x0,
            method=args.optimization_solver_minimization,
            tol=args.optimization_tolerance,
        )
    else:
        optimization_result = minimize(
            fun,
            x0,
            method=args.optimization_solver_root,
            bounds=[(p.min, p.max) for p in args.parameter],
            tol=args.optimization_tolerance,
        )

    print(optimization_result)

    generate_parameter_file(
        args.parameter_file, args.parameter, args.parameter_passing
    )
