import subprocess
import time
from collections import Counter

cached = None
cached_time = 0

def slurm_handler(name):
    name = name.replace('slurm_jobs_', '')

    global cached, cached_time
    now = time.time()
    if cached == None or now-cached_time > 20:
        w = subprocess.check_output(["squeue", "-h", "-Ostate"]).replace(' ', '').splitlines()
        cached = dict(Counter(w))
        cached_time = now
    if name in cached.keys():
        return cached[name]
    else:
        return 0

def metric_init(params):
    global descriptors
    
    d1 = {'name': 'slurm_jobs_RUNNING',
          'call_back': slurm_handler,
          'time_max': 20,
          'value_type': 'uint',
          'units': 'jobs',
          'slope': 'both',
          'format': '%u',
          'description': 'number of running slurm jobs',
          'groups': 'health'}

    d2 = {'name': 'slurm_jobs_PENDING',
          'call_back': slurm_handler,
          'time_max': 20,
          'value_type': 'uint',
          'units': 'jobs',
          'slope': 'both',
          'format': '%u',
          'description': 'number of pending slurm jobs',
          'groups': 'health'}

    descriptors = [d1, d2]

    return descriptors

if __name__ == '__main__':
    metric_init({})
    for d in descriptors:
        v = d['call_back'](d['name'])
        print 'value for %s is %u' % (d['name'],  v)
