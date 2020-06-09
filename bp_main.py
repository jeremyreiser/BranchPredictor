#!/usr/bin/python3

import sys, re, fileinput
import branchpredictor

def     sys_error(s):
    print ("Error: " + s)
    exit(1)

def     parse_config(s):
    if s == '':
        return (0, 0, 0)
    fields = s.split(",")
    if (len(fields) != 3):
        sys_error("Invalid configuration. Need three numbers, like 2,1,10.")
    m = int(fields[0]) 
    n = int(fields[1]) 
    k = int(fields[2]) 
    assert m >= 0 and m <= 16
    assert n >= 1 and n <= 4 
    assert k >= 0 and k <= 16
    assert m + k < 24
    return (m, n, k)

argc = len(sys.argv)
if (argc < 2): 
    # triple quotes can be used for a multi-line string in python
    sys_error(''' command line arguments missing.
Usage: bp_main config0 [config1] [tracefile]

config0 or config1 is a string like m,n,k. 
    m : number of bits in global history
    n : number of bits in counter 
    k : number of bits in the index from branch address

For example, 1,2,10 means 1 bit global history, 2-bit counters,
and 10 bits from branch address. The total number of bits in
an index is m + k.

tracefile is text file containing branch traces. If no file 
is specified, the program tries to read from stdin.
''')

verbose = 0
config0 = ""
config1 = "" 
opt_nbts = 10
files = []

for a in sys.argv[1:]:
    if a.startswith('-v'):
        if a[2:]:
            verbose = int(a[2:])
        else:
            verbose = 1
    elif a.startswith('-t'):
        opt_nbts = int(a[2:])
    elif (',' in a):
        if (config0 == ''):
            config0 = a
        else:
            config1 = a
    else: 
        files.append(a)

if verbose:
    print("nbts={} config0='{}', config1='{}'".format(opt_nbts, config0, config1))

if (config0 == ''):
    sys_error("Specify at least one configuration.")

if opt_nbts <= 3 or opt_nbts > 20:
    sys_error("The number of bits for selecting a selector in tournament must be between 4 and 20.") 

config_parsed0 = parse_config(config0)
config_parsed1 = parse_config(config1)

BP = branchpredictor.BranchPredictor()

"""
    If a second configuration was provided and its BHT index size is greater
    than zero, use tournament-style predictor. Else use local or global predictor.
"""
if config_parsed1[2] > 0:
    # the '*' operator unpacks the tuple into positional arguments for this method
    BP.configure_tournament(opt_nbts, *config_parsed0, *config_parsed1)
else:
    BP.configure(*config_parsed0)

BP.set_verbose(verbose)

"""
    This regex pattern matches when the line begins with an address that can
    (optionally) be prefixed with '0x', followed by one or more alphanumeric characters,
    followed by whitespace and then either a 1, T, t (taken) or 0, NT, nt (not taken)
"""
pattern = re.compile('^((0x)*([0-9A-Fa-f]+))\s+(0|1|T|t|NT|nt)\s*$')

n_lines = 0

for line in fileinput.input(files):
    n_lines += 1
    m = re.search(pattern, line)
    if (m):
        # in the pattern, each set of parentheses represents a "group"
        address = int(m.group(1), 0)
        outcome = 1 if m.group(4)[0] in '1Tt' else 0
        prediction = BP.predict(address, outcome)
        if verbose & 4:
            print(address, outcome, prediction)

BP.report()
