import subprocess
import time
import re
from collections import Counter

cached = {}
cached_time = 0

def slurm_handler(name):
    global cached, cached_time
    p = name.split('_')
    now = time.time()

    if now-cached_time > 20:
        cached_time = now
        w = subprocess.check_output(["squeue", "-h", "-Ostate"])
        w = w.replace(' ', '').splitlines()
        cached['jobs'] = dict(Counter(w))

        w = subprocess.check_output(["scontrol", "show", "node", "-o"]).splitlines()
        cached['gpu'] = {'alloc': 0, 'free': 0}
        for l in w:
            alloc = re.search('.*AllocTRES=([\w=,]*)gres/gpu=([0-9]?).*', l)
            alloc = int(alloc.group(2)) if alloc != None else 0
            cfg = re.search('.*CfgTRES=([\w=,]*)gres/gpu=([0-9]?).*', l)
            cfg = int(cfg.group(2)) if cfg != None else 0
            cached['gpu']['free'] += (int(cfg) - int(alloc))
            cached['gpu']['alloc'] += int(alloc)

    if p[1] in cached.keys() and p[2] in cached[p[1]].keys():
        return cached[p[1]][p[2]]
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

    d3 = {'name': 'slurm_gpu_free',
          'call_back': slurm_handler,
          'time_max': 20,
          'value_type': 'uint',
          'units': 'jobs',
          'slope': 'both',
          'format': '%u',
          'description': 'number of free gpus',
          'groups': 'health'}

    d4 = {'name': 'slurm_gpu_alloc',
          'call_back': slurm_handler,
          'time_max': 20,
          'value_type': 'uint',
          'units': 'jobs',
          'slope': 'both',
          'format': '%u',
          'description': 'number of alloc gpus',
          'groups': 'health'}

    descriptors = [d1, d2, d3, d4]

    return descriptors

if __name__ == '__main__':
    metric_init({})
    for d in descriptors:
        v = d['call_back'](d['name'])
        print 'value for %s is %u' % (d['name'],  v)
