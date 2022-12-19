# -*- coding: utf-8 -*-
"""
@author: sinannasir
"""

import numpy as np
import matplotlib.pyplot as plt
from itertools import cycle
import json
import matplotlib
matplotlib.use('Qt5Agg')
import argparse

def main(scenario):    
    json_file = scenario['json_file']
    json_file_policy = scenario['json_file_policy']
    num_sim = scenario['num_sim']
    with open ('./config/deployment/'+json_file+'.json','r') as f:
        options = json.load(f)
    
    ## Kumber of samples
    total_samples = options['simulation']['total_samples']
        
    K = options['simulation']['K']
    N = options['simulation']['N']
    
    
    if num_sim == -1:
        num_simulations = options['simulation']['num_simulations']
        simulation = options['simulation']['simulation_index_start']
    else:
        num_simulations = 1
        simulation = num_sim
    
    # simulation parameters
    mobility_params = options['mobility_params']
    mobility_params['alpha_angle'] = options['mobility_params']['alpha_angle_rad'] * np.pi #radian/sec
    
    history = 250
        
    
    mean_p_FP = np.zeros(total_samples)
    mean_time_FP = np.zeros(total_samples)
    mean_iterations_FP = np.zeros(total_samples)
    mean_sum_rate_FP = np.zeros(total_samples)
    mean_p_WMMSE = np.zeros(total_samples)
    mean_time_WMMSE = np.zeros(total_samples)
    mean_iterations_WMMSE = np.zeros(total_samples)
    mean_sum_rate_WMMSE = np.zeros(total_samples)
    
    mean_sum_rate_delayed_central = np.zeros(total_samples)
    mean_sum_rate_random = np.zeros(total_samples)
    mean_sum_rate_max = np.zeros(total_samples)
    
    mean_sum_rate_policy_train_innersims = np.zeros(total_samples)
    mean_p_strategy_all_train_innersims = np.zeros(total_samples)
    
    mean_time_optimization_at_each_slot_takes = []
    mean_time_calculating_strategy_takes = []
    
    for overal_sims in range(simulation,simulation+num_simulations):
        # Get the benchmarks.
        file_path = './simulations/sumrate/benchmarks/%s_network%d'%(json_file,overal_sims)
        data = np.load(file_path+'.npz')
        p_FP            = data['arr_0']
        time_stats_FP   = data['arr_1']
        sum_rate_FP     = data['arr_2']
        p_WMMSE         = data['arr_3']
        time_stats_WMMSE= data['arr_4']
        sum_rate_WMMSE  = data['arr_5']
        sum_rate_delayed_central          = data['arr_6']
        sum_rate_random         = data['arr_7']
        sum_rate_max            = data['arr_8']
        
        file_path = './simulations/sumrate/train/%s_%s_network%d.ckpt'%(json_file,json_file_policy,overal_sims)
        data = np.load(file_path+'.npz')
        # Get the train policy results
        sum_rate_policy_train                      = data['arr_2']
        p_strategy_all                          = data['arr_3']
        time_optimization_at_each_slot_takes    = data['arr_4']
        time_calculating_strategy_takes         = data['arr_5']
    
        # Average
        mean_p_FP = mean_p_FP + np.sum(p_FP,1)/float(num_simulations)
        mean_time_FP = mean_time_FP + time_stats_FP[:,0]/float(num_simulations)
        mean_iterations_FP = mean_iterations_FP + time_stats_FP[:,1]/float(num_simulations)
        mean_sum_rate_FP = mean_sum_rate_FP + sum_rate_FP/float(num_simulations)
        mean_p_WMMSE = mean_p_WMMSE + np.sum(p_WMMSE,1)/float(num_simulations)
        mean_time_WMMSE = mean_time_WMMSE + time_stats_WMMSE[:,0]/float(num_simulations)
        mean_iterations_WMMSE = mean_iterations_WMMSE + time_stats_WMMSE[:,1]/float(num_simulations)
        mean_sum_rate_WMMSE = mean_sum_rate_WMMSE + sum_rate_WMMSE/float(num_simulations)
        
        mean_sum_rate_delayed_central = mean_sum_rate_delayed_central + sum_rate_delayed_central/float(num_simulations)
        mean_sum_rate_random = mean_sum_rate_random + sum_rate_random/float(num_simulations)
        mean_sum_rate_max = mean_sum_rate_max + sum_rate_max/float(num_simulations)
        
        mean_sum_rate_policy_train_innersims = mean_sum_rate_policy_train_innersims + sum_rate_policy_train/float(num_simulations)
        mean_p_strategy_all_train_innersims = mean_p_strategy_all_train_innersims + np.sum(p_strategy_all,1)/float(num_simulations)
        
        mean_time_optimization_at_each_slot_takes.append(time_optimization_at_each_slot_takes)
        mean_time_calculating_strategy_takes.append(time_calculating_strategy_takes)
    
    #print('K '+ str(int(N))+' R '+str(R_defined)+ ' r '+str(min_dist) + ' '+file_path[14:18])
    #print('Test Sum rate wmmse ' + str(np.mean(mean_sum_rate_WMMSE[total_samples-2500:]/N)))
    #print('Test Sum rate optimal ' + str(np.mean(mean_sum_rate[total_samples-2500:]/N)))
    #print('Test Sum rate delayed ' + str(np.mean(mean_sum_rate_delayed_central[total_samples-2500:]/N)))
    #print('Test Sum rate random ' + str(np.mean(mean_sum_rate_random[total_samples-2500:]/N)))
    #print('Test Sum rate max ' + str(np.mean(mean_sum_rate_max[total_samples-2500:]/N)))
    #for i in range(len(power_multiplier_allsims)):
    #    print('Multiplier '+str(power_multiplier_allsims[i])+
    #          ' Test Sum rate ' +str(np.mean(mean_sum_rate_policy_train_innersims[i,total_samples-2500:]/N)))
    
    lines = ["-","--",':','-.',':','-.']
    linecycler = cycle(lines)
    history = 100
    fig = plt.figure()
    
    t=np.arange(0,total_samples,10)
    
    sum_rate_performance_FP = []
    sum_rate_performance_random = []
    sum_rate_performance_max = []
    sum_rate_performance_delayed_central = []
    sum_rate_performance_policy = []
    sum_rate_performance_wmmse = []
    sum_rate_performance_policy = []
    
    ep_start = 0
    for i in range(len(t)):
        if t[i] % options['train_episodes']['T_train'] == 0:
            ep_start = t[i]
        sum_rate_performance_FP.append(np.mean(mean_sum_rate_FP[max(ep_start,t[i]-history):t[i]]))
        sum_rate_performance_random.append(np.mean(mean_sum_rate_random[max(ep_start,t[i]-history):t[i]]))
        sum_rate_performance_max.append(np.mean(mean_sum_rate_max[max(ep_start,t[i]-history):t[i]]))
        sum_rate_performance_delayed_central.append(np.mean(mean_sum_rate_delayed_central[max(ep_start,t[i]-history):t[i]]))
        sum_rate_performance_wmmse.append(np.mean(mean_sum_rate_WMMSE[max(ep_start,t[i]-history):t[i]]))
        sum_rate_performance_policy.append(np.mean(mean_sum_rate_policy_train_innersims[max(ep_start,t[i]-history):t[i]]))
        
        
    #plt.figure(figsize=(5,5))
    t=np.arange(0,total_samples,10)
    plt.plot(t, np.array(sum_rate_performance_wmmse)/float(N), label='WMMSE',linestyle=next(linecycler))
    plt.plot(t, np.array(sum_rate_performance_FP)/float(N), label='FP',linestyle=next(linecycler))
    plt.plot(t, np.array(sum_rate_performance_delayed_central)/float(N), label='FP w delay',linestyle=next(linecycler))
    plt.plot(t, np.array(sum_rate_performance_random)/float(N), label='random',linestyle=next(linecycler))
    plt.plot(t, np.array(sum_rate_performance_max)/float(N),'c', label='full-power',linestyle=next(linecycler))
    plt.plot(t, np.array(sum_rate_performance_policy)/float(N), label='matched policy',linestyle=next(linecycler))# with Multiplier '+str(power_multiplier_allsims[i]),linestyle=next(linecycler))
    
    plt.xlabel('training iterations')
    plt.ylabel('moving average spectral efficiency (bps/Hz) per link')
    plt.grid(True)
    plt.legend(loc=4)
    plt.tight_layout()
    plt.savefig('./fig/spectraleff_%s_network_%d'%(json_file,overal_sims)+'.pdf', format='pdf', dpi=1000)
    plt.savefig('./fig/spectraleff_%s_network_%d'%(json_file,overal_sims)+'.png', format='png', dpi=1000)
    plt.show(block=False)
    
    # Average performance of the last 200 training slots.
    history = 200
    print('Deployment: %s; policy: %s; K: %d; N: %d'%(json_file,json_file_policy,N,K))
    print('Averages for last %d episodes:'%(history))
    print('Sum rate per link - policy: %.2f'%(np.mean(mean_sum_rate_policy_train_innersims[total_samples-history:])/float(N)))
    print('Sum rate per link - WMMSE: %.2f'%(np.mean(mean_sum_rate_WMMSE[total_samples-history:])/float(N)))
    print('Sum rate per link - FP: %.2f'%(np.mean(mean_sum_rate_FP[total_samples-history:])/float(N)))
    print('Sum rate per link - FP w delay: %.2f'%(np.mean(mean_sum_rate_delayed_central[total_samples-history:])/float(N)))
    print('Sum rate per link - random: %.2f'%(np.mean(mean_sum_rate_random[total_samples-history:])/float(N)))
    print('Sum rate per link - full: %.2f'%(np.mean(mean_sum_rate_max[total_samples-history:])/float(N)))
    
    # Average time statistics
    print('Average time for a WMMSE run: %.2f ms'%(1000 * np.mean(mean_time_WMMSE)))
    print('Average time for an FP run: %.2f ms'%(1000 * np.mean(mean_time_FP)))
    print('Average time for a policy agent to determine its action %.2f ms'%(1000 * np.mean(mean_time_calculating_strategy_takes)))
    print('Average time for a policy mini-batch train %.2f ms'%(1000 * np.mean(mean_time_optimization_at_each_slot_takes)))
    print('Average WMMSE iterations per run: %.2f'%(np.mean(mean_iterations_WMMSE)))
    print('Average FP iterations per run: %.2f'%(np.mean(mean_iterations_FP)))
    
if __name__ == "__main__": 
    
    parser = argparse.ArgumentParser(description='give test scenarios.')
    parser.add_argument('--json-file', type=str, default='train_K5_N10_shadow10_episode2-5000_travel50000_vmax2_5',
                       help='json file for the deployment the policies are tested on')
    parser.add_argument('--json-file-policy', type=str, default='ddpg200_100_50',
                       help='json file for the hyperparameters')
    parser.add_argument('--num-sim', type=int, default=0,
                       help='If set to -1, it uses num_simulations of the json file. If set to positive, it runs one simulation with the given id.')
    
    args = parser.parse_args()
    
    test_scenario = {'json_file':args.json_file,
                     'json_file_policy':args.json_file_policy,
                     'num_sim':args.num_sim}
    main(test_scenario)