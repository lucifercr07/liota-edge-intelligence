import csv
import time
from linux_metrics import cpu_stat, mem_stat

def read_cpu_procs():
    return cpu_stat.procs_running()

def read_cpu_utilization(sample_duration_sec=1):
    cpu_pcts = cpu_stat.cpu_percents(sample_duration_sec)
    return round((100 - cpu_pcts['idle']), 2)

def read_mem_free():
    total_mem = round(mem_stat.mem_stats()[1], 4)
    free_mem = round(mem_stat.mem_stats()[3], 4)
    mem_free_percent = ((total_mem - free_mem) / total_mem) * 100
    return round(mem_free_percent, 2)

with open('test.csv', 'wb') as f:
    wtr = csv.writer(f, delimiter= ',')
    while True:
	    wtr.writerow([time.asctime(),read_cpu_utilization(), read_mem_free()])