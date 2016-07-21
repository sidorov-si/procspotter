# procspotter

Monitor a process resource usage with pidstat utility.
Process here is defined with a PID set with -w argument.

sysstat package must be installed before the first use of procspotter (it contains pidstat).

For all procspotter arguments you can find short explanations below. '--args' argument though is worth explaining a little deeper. You want to use --args when some specific statistics should be collected. The value of this argument should be set in double quotes.

'--args' argument enables you to pass any arguments to pidstat.

By default, pidstat is launched with the following arguments:

pidstat -p PID -d -r -u 2 > pidstat_log_name

where 

      -p sets the process ID that is defined in -w ('watch') argument of procspotter,

      -d is for disk I/O statistics,

      -r is for memory utilization statistics,

      -u is for CPU utilization statistics,

      2 is an interval (in seconds) between two measurements.

      pidstat_log_name is set with -l argument of procspotter.

'count' argument for pidstat is not set here, so pidstat 
will collect statictics until the process finishes.

"-d -r -u 2" is replaced with the value of '--args' if it is set.

For the whole set of pidstat arguments see 'man pidstat'.

E. g., you may want to set 'interval' and 'count' arguments for pidstat and to collect only CPU statistics.

You can do it with '--args' as follows:

procspotter.py -w PID -l pidstat_log_name --args "-u 2 10"

where 2 is a value of 'interval' argument and 10 is a value of 'count' argument.

When -p ('parse') argument is given to procspotter, a pidstat log file is parsed and maximum and average values are calculated for all statistics measured by pidstat. If some statistic is not numerical (e. g., 'Command'), corresponding statistics are set to zero.

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

