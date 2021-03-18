Parameter optimization script
=============================

This project contains a pyton script for finding optimal values of parameters 
in models that read their parameters from `.ini` files 
or where the source code is available.


```bash
$ ./parameter_optimizer.py --help
usage: use "parameter_optimizer.py --help" for more information

Optimize / find root of a model in external progam

optional arguments:
  -h, --help            show this help message and exit
  --optimization-choice {minimum,root}
                        Optimization: look for minimum or a root
  --optimization-solver-minimization OPTIMIZATION_SOLVER_MINIMIZATION
                        A valid minimization solver name. See https://docs.scipy.org/doc/
                        scipy/reference/generated/scipy.optimize.minimize.html#scipy.opti
                        mize.minimize
  --optimization-solver-root OPTIMIZATION_SOLVER_ROOT
                        A valid root-finding solver name. See https://docs.scipy.org/doc/
                        scipy/reference/generated/scipy.optimize.root.html#scipy.optimize
                        .root
  --optimization-tolerance OPTIMIZATION_TOLERANCE
                        Tolerance for optimization
  --parameter-passing {ini,data-txt,header-const,header-define}
                        How to pass parameters to the program: by writing the parameters
                        to an ini file, a txt file with data, header with const double
                        values or header with defines
  --program-command PROGRAM_COMMAND
                        The program or script to execute [shell command]
  --parameter-file PARAMETER_FILE
                        File into which the parameters are written
  --result-file RESULT_FILE
                        File that contains the result of the model
  --calculation-cache-file CALCULATION_CACHE_FILE
                        If set, the results of program calls are cached and reused
  --calculation-cache-tol CALCULATION_CACHE_TOL
                        If program results are cached, the lookup of values returns the
                        first match with this tolerance in parameter values
  --parameter PARAMETER
                        List of parameters to pass to the model. Format :
                        --parameter=<name>:min:max, --parameter=phi:-3.14142:+3.14142
```


Why
---

I frequently need to find good values for parameters
in various models, written in C++. 

The scripts in this project require minimal modifications
to the source code of the model.

How
---

This project includes a python script that wraps a call to an extenal program
into a function that is then passed to 
`scipy.optimize.root` or `scipy.optimize.minimize`.

The script, before running the external program,
writes to disk a file containing the values of parameters passed to the function.

The parameters can be written to file as a c++ header as `#define` constants
or `const double` values, as an `.ini` file or simply as a list of values, 
one value per line.

The script reads the value of the function to be optimized from
a file, and returns this value to the optimization routine.

Optionally the results of the model can be cached and reused on subsequent
runs of the program.

A simple wrapper for reading parameters from an `.ini` file
is provided together with 
the [`ini.h`](https://github.com/mattiasgustavsson/libs/blob/main/ini.h) library.

[Header file example](./example/example-header-const.sh): 
c++ model, compiled with generated header on each iteration.

[Ini example](./example/example-ini.sh): 
c++ model, reading parameters from `.ini` file.

