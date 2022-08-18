# -*- coding: utf-8 -*-
"""
wrapper for get_NDA_DV_mode_info.py

* Hyperparameters:
    deflection time in days
    directions, pro or retrograde
    periapse distance to deflect the asteroid (assumed to be unique throughtout the whole script)
    
* The number of cores may affect the chances of getting nans or unrun cases, depending
  on the internet connection. The lower the numer of cores, the lower the chances are.
  
  A strategy could be 1) run with many cores and 2) run the remnant cases again to get all the results with the minimum cpu time
    
* geckodriver.exe is required to open Firefox with selenium. 
  https://github.com/mozilla/geckodriver/releases
  The exe works at least when it is placed in the same directory than the python.exe (Anaconda)
"""


import get_NDA_DV_mode_info as func
from multiprocessing import cpu_count, Pool
import itertools
import os


def run_parallel(ncores, inputs):  

    pool = Pool(processes=ncores)
    pool.starmap(func.run_NDA_DV_mode, inputs)


if __name__ == '__main__':
    
    ncores = cpu_count()- 4 
    
    tempfiles = os.listdir()

    tempfiles = set([file for file in tempfiles if file.endswith(".csv")])
    
    # remove files from a previous 
    for tempfile in tempfiles:
        os.remove(tempfile)
    
    deflection_times = [400, 800,1000, 1200, 1400, 1600, 1800, 2000, 2200, 2400, 2600, 2800, 3000, 3200, 3400] # days
    directions = [-1,1] # 1 prograde, -1 retrograde
    desired_distance = [1]# times Re
    
    inputs = [deflection_times, desired_distance, directions]   
    inputs = list(itertools.product(*inputs))    
    
    run_parallel(ncores, inputs)

         
    # process and remove the temporary files (runs) and merge all the valid ones into results.csv and states the ones which have to be re-run
    tempfiles = os.listdir()
    tempfiles = set([file for file in tempfiles if file.endswith(".csv")])
    wrongtempfiles = set([file for file in tempfiles if "nan" in file])
    tempfiles -= wrongtempfiles


    inputs_well_run = set([(int(tempfile[tempfile.find('timedeflection_')+len('timedeflection_'):tempfile.find('_days')]),
                            int(desired_distance[0]), 
                            int(tempfile[tempfile.find('direction')+len('direction'):tempfile.find('_dist')]))
                            for tempfile in tempfiles])

    inputs_to_run = set(inputs) - inputs_well_run
    
    
    # remove wrongtempfiles    
    if len(wrongtempfiles) >0:
        list(map(os.remove, wrongtempfiles))

            
    # merge the well-run cases into results.csv
    results = open('results.csv', 'w+')
    results.writelines( 'Deflection time[days]   dva [mm/s]   Periapse distance [Re]   Direction ' + '\n') 
    for tempfile in tempfiles:      
        data = open(tempfile, 'r').readlines()[1]
        results.writelines(  data )  
    results.close()

    # cases that have to be rerun due to the instability dealing with the browser
    if len( inputs_to_run) >0:
        casestorerun = open('casestorerun.csv', 'w+')
        casestorerun.writelines('(Deflection time[days],  Desired distance [Re],  Direction)' + '\n') 
        for input_to_run in inputs_to_run:
            casestorerun.writelines(str(input_to_run)+'\n')
        casestorerun.close()


    
    # remove the rest of temporary files corresponding to the well-run cases
    tempfiles = os.listdir()
    tempfiles = set([file for file in tempfiles if "timedeflection" in file])
    list(map(os.remove, tempfiles)  )  










