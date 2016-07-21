#!/usr/bin/env python
"""
Monitor a process resource usage with pidstat utility.
Process here is defined with a PID set with -w argument.

sysstat package must be installed before the first use of
procspotter (it contains pidstat).

For all procspotter arguments you can find short explanations
below. '--args' argument though is worth explaining a little 
deeper. You want to use --args when some specific 
statistics should be collected. The value of this argument
should be set in double quotes.

'--args' argument enables you to pass any arguments to pidstat.
By default, pidstat is launched with the following arguments:

pidstat -p PID -d -r -u 2 > pidstat_log_name
              |__________|

where -p sets the process ID that is defined 
         in -w ('watch') argument of procspotter,
      -d is for disk I/O statistics,
      -r is for memory utilization statistics,
      -u is for CPU utilization statistics,
      2 is an interval (in seconds) between two measurements.
      pidstat_log_name is set with -l argument of procspotter.

'count' argument for pidstat is not set here, so pidstat 
will collect statictics until the process finishes.

|__________| is replaced with the value of '--args' if it
is set.

For the whole set of pidstat arguments see 'man pidstat'.

E. g., you may want to set 'interval' and 'count' arguments
for pidstat and to collect only CPU statistics.
You can do it with '--args' as follows:

procspotter.py -w PID -l pidstat_log_name --args "-u 2 10"

where 2 is a value of 'interval' argument and 10 is a value
of 'count' argument.

When -p ('parse') argument is given to procspotter, a pidstat log file 
is parsed and maximum and average values are calculated for all 
statistics measured by pidstat. If some statistic is not numerical 
(e. g., 'Command'), corresponding statistics are set to zero.

Please note that:
1) neither a PID nor a value of '--args' argument is checked for 
   correctness and safety;
2) process with a given PID must be executed at least for several 
   seconds for pidstat to collect some statistics; for 1 - 3 seconds 
   at the very begining statistics are not collected;
3) if -u argument for pidstat is set manually via '--args' argument,
   then its value should be less than one day;
5) process with a given PID will output to stdout and/or stderr 
   just as if it were launched without procspotter;
6) with -p argument statistics for all characteristics are calculated 
   and output, so for fields like 'Command' or 'CPU' (CPU ID) it 
   shouldn't be considered;
7) time utility shouldn't be used within the command: procspotter's 
   log parser will print total execution time anyway.

Usage:
  procspotter.py -w <PID> -l <pidstat_log_name> [--args <arguments_for_pidstat>]
  procspotter.py -p <pidstat_log_name> 

Options:
  -h --help                       Show this screen.
  --version                       Show version.
  -w <PID>                        PID of the process to be watched with pidstat.
  -l <pidstat_log_name>           Name of a log file for pidstat output.
  -p <pidstat_log_name>           Parse log file and print statistics.
  --args <arguments_for_pidstat>  Arguments for pidstat. Default: ''.
"""


import sys

print

modules = ["docopt", "subprocess", "datetime", "os"]
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
import datetime
from os.path import exists
from os.path import isfile


def print_stats(total_time, headers, values, log_name):
    print "Statistics from", log_name + ':'
    print 
    print "Total time:", total_time
    print
    stdout.flush()
    for header_index, header in enumerate(headers):
        current_max_list = [dictionary["maximum"] for dictionary in values[header_index]]
        current_avg_list = [dictionary["avg"] for dictionary in values[header_index]]
        header_line = ' ' * 8 + ''.join(['{0: <14}'.format(head) for head in header])
        max_line = 'Max:    ' + ''.join(['{0: <14.3f}'.format(value) for value in current_max_list])
        avg_line = 'Avg:    ' + ''.join(['{0: <14.3f}'.format(value) for value in current_avg_list])
        print header_line
        print max_line
        print avg_line
        print
        stdout.flush()


def get_time_step(header_line, value_line):
    header_fields = header_line.strip('\n').split()
    value_fields = value_line.strip('\n').split()
    if header_fields[1] != value_fields[1]:
        return 0
    else:
        time1_fields = header_fields[0].split(':')
        time2_fields = value_fields[0].split(':')
        time1 = datetime.datetime(year = 1, month = 1, day = 1, \
                                  hour = int(time1_fields[0]), minute = int(time1_fields[1]), \
                                  second = int(time1_fields[2]))
        time2 = datetime.datetime(year = 1, month = 1, day = 1, \
                                  hour = int(time2_fields[0]), minute = int(time2_fields[1]), \
                                  second = int(time2_fields[2]))
        if time2 < time1:
            return 0
        time_diff = time2 - time1
        return time_diff.seconds


def parse_pidstat(log_name):
    with open(log_name, 'r') as log:
        # init
        counter = 0
        time_step = 0
        header_joints = []
        headers = [] # [[field11, ..., field1K], ..., 
                     #  [fieldN1, ..., fieldNM]]
        values = [] # [[{maximum:field11_max, total:field11_sum, avg:field11_avg}, ..., 
                    #   {maximum:field1K_max, total:field1K_sum, avg:field1K_avg}], ...,
                    #  [{maximum:fieldN1_max, total:fieldN1_sum, avg:fieldN1_avg}, ..., 
                    #   {maximum:fieldNM_max, total:fieldNM_sum, avg:fieldNM_avg}]]
        # read header and the next empty line
        _ = log.readline()
        _ = log.readline()
        # read line pairs and store info
        header_line = log.readline()
        value_line = log.readline()
        while value_line != '\n':
            counter += 1
            if counter % 1000 == 0:
                print 'Processed', counter, 'records.'
                stdout.flush()
            header_fields = header_line.strip('\n').split()
            current_fields = header_fields[4:]
            header_joint = ''.join(current_fields)
            if header_joint not in header_joints:
                header_joints.append(header_joint)
                headers.append(current_fields)
                values.append([{"maximum":0, "total":0, "avg":0} for i in current_fields])
            sublist_index = header_joints.index(header_joint)
            value_fields = value_line.strip('\n').split()
            current_values = value_fields[4:]
            if time_step == 0:
                time_step = get_time_step(header_line, value_line)
            for value_index, value in enumerate(current_values):
                try:
                    float_value = float(value)
                except:
                    float_value = 0
                current_values[value_index] = float_value
            for dict_index, dictionary in enumerate(values[sublist_index]):
                current_value = current_values[dict_index]
                current_max = values[sublist_index][dict_index]["maximum"]
                if current_value > current_max:
                    values[sublist_index][dict_index]["maximum"] = current_value
                values[sublist_index][dict_index]["total"] += current_value
            _ = log.readline() # pass an empty line
            header_line = log.readline() # get the next header
            value_line = log.readline() # get the next values

        number_of_records = counter / len(header_joints)
        total_time = datetime.timedelta(seconds = time_step * number_of_records)
        for sublist_index, sublist in enumerate(values):
            for dict_index, dictionary in enumerate(sublist):
                current_total = values[sublist_index][dict_index]["total"]
                values[sublist_index][dict_index]["avg"] = float(current_total) / number_of_records

        print_stats(total_time, headers, values, log_name)


def set_pidstat(pid, log_name, args):
    with open(log_name, 'w') as log:
        print 'The following process is watched (PID):', pid
        print 'All statistics are being logged in', log_name
        stdout.flush()
        pidstat_args = args if args != None else '-d -r -u 2'
        pidstat_args_list = pidstat_args.split()
        pidstat_list = ['pidstat', '-p', pid] + pidstat_args_list
        pidstat_process = subprocess.Popen(pidstat_list, stdout = log)
        pidstat_pid = str(pidstat_process.pid)
        print 'Statistics are being collected with the following pidstat process:'
        print ' '.join(pidstat_list), '>', log_name
        print 'PID of the pidstat process:', pidstat_pid
        stdout.flush()


if __name__ == '__main__':
    arguments = docopt(__doc__, version='procspotter 0.3')
    case = ""
    if arguments["-w"] != None:
        case = "watch"
        pid = arguments["-w"]
        log_name = arguments["-l"]
        args = arguments["--args"]
    elif arguments["-p"] != None:
        case = "parse"
        log_name = arguments["-p"]
        if not exists(log_name):
            print "Error: Can't find log file: no such file '" + \
                  log_name + "'. Exit.\n"
            sys.exit(1)
        if not isfile(log_name):
            print "Error: log filemust be a regular file. " + \
                  "Something else given. Exit.\n"
            sys.exit(1)
    
    if case == "watch":
        set_pidstat(pid, log_name, args)
    elif case == "parse":
        parse_pidstat(log_name)

