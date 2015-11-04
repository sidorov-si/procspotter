#!/usr/bin/env python
"""
Monitor a process resource usage with pidstat utility.
Process here is a command set with -c argument.
This simple wrapper helps to avoid some manual work:
first, to start a command, then - to find its PID (process
id), and finally start pidstat utility to watch it.

sysstat package must be installed before the first use of
procspotter (it contains pidstat).

For all procspotter arguments you can find short explanations
below. --args argument though is worth explaining a little 
deeper. You want to use --args when some specific 
statistics should be collected. The value of this argument
should be set in double quotes.

'--args' argument enables you to pass any arguments to pidstat.
By default, pidstat is launched with the following arguments:

pidstat -p PID -d -r -u 2 > <pidstat_log_name>
              |__________|

where -p sets the process ID that is determined 
         automatically by procspotter,
      -d is for disk I/O statistics,
      -r is for memory utilization statistics,
      -u is for CPU utilization statistics,
      2 is an interval (in seconds) between two measures.
      <pidstat_log_name> is set with -l argument of procspotter.

'count' argument for pidstat is not set here, so pidstat 
will collect statictics until the process finishes.

|__________| is replaced with the value of '--args' if it
is set.

For the whole set of pidstat arguments see 'man pidstat'.

E. g., you may want to set 'interval' and 'count' arguments
for pidstat and to collect only CPU statistics.
You can do it with '--args' as follows:

procspotter.py -c <command> -l <pidstat_lot_name> --args "-u 2 10"

where 2 is a value of 'interval' argument and 10 is a value
of 'count' argument.

Please note that neither the <command> nor the value 
of '--args' argument is checked for correctness and safety.
The <command> must be executed at least for several
seconds for pidstat to collect some statistics. <command>
mustn't contain output redirectiron ('>') or pipes ('|').

Usage:
  procspotter.py -c <command> -l <pidstat_log_name> [--verbose --args <arguments_for_pidstat>]

Options:
  -h --help                       Show this screen.
  --version                       Show version.
  -c <command>                    Command to be watched with pidstat.
  -l <pidstat_log_name>           Name of a log file for pidstat output.
  --verbose                       Print info about the launched <command>.
  --args <arguments_for_pidstat>  Arguments for pidstat. Default: ''.
"""


import sys

print

modules = ["docopt", "subprocess"]
exit_flag = False
for module in modules:
    try:
        __import__(module)
    except ImportError:
        exit_flag = True
        sys.stderr.write("Error: Python module " + module + " is not installed.\n")

if exit_flag:
    sys.stderr.write("You can install these modules with a command: pip install <module>\n")
    sys.stderr.write("(Administrator privileges may be required.)\n")
    sys.exit(1)


from docopt import docopt
from sys import stdout
import subprocess


def set_pidstat(command, log_name, verbose, args):
    with open(log_name, 'w') as log:
        command_list = command.split()
        process = subprocess.Popen(command_list, close_fds = True)
        pid = str(process.pid)
        if verbose:
            print 'The following command is launched:'
            print command
            print 'PID:', pid
            print 'All statistics are being logged in', log_name
        pidstat_args = args if args != None else '-d -r -u 2'
        pidstat_args_list = pidstat_args.split()
        pidstat_list = ['pidstat', '-p', pid] + pidstat_args_list
        pidstat_process = subprocess.Popen(pidstat_list, stdout = log)
        pidstat_pid = str(pidstat_process.pid)
        if verbose:
            print 'Statistics are being collected with the following pidstat process:'
            print ' '.join(pidstat_list), '>', log_name
            print 'PID of the pidstat process:', pidstat_pid


if __name__ == '__main__':
    arguments = docopt(__doc__, version='procspotter 0.1')
    command = arguments["-c"]
    log_name = arguments["-l"]
    args = arguments["--args"]
    verbose = arguments["--verbose"] # True or False
    
    set_pidstat(command, log_name, verbose, args)

