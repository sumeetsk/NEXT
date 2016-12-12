import numpy
import numpy as np
import numpy.random
import random
import json
import time
from datetime import datetime
import requests
from scipy.linalg import norm
import time
from multiprocessing import Pool
import os
import sys
from joblib import Parallel, delayed
try:
    import next.apps.test_utils as test_utils
except:
    sys.path.append('../../../next/apps/')
    import test_utils


def test_validation_params():
    params = [{'num_tries': 5},
              {'query_list': [[0, 1], [1, 2], [3, 4]]}]
    for param in params:
        print(param)
        test_api(params=param)


def test_api(assert_200=True, num_arms=100, num_clients=100, delta=0.05,
             total_pulls_per_client=300, num_experiments=1,
             params={'num_tries': 5}):

    app_id = 'ActiveRanking'
    true_means = numpy.array(range(num_arms)[::-1])/float(num_arms)
    true_means = np.arange(num_arms)
    pool = Pool(processes=num_clients)
    supported_alg_ids = ['AR_Random', 'Quicksort', 'ValidationSampling']

    alg_list = []
    for i, alg_id in enumerate(supported_alg_ids):
        alg_item = {}
        if alg_id == 'ValidationSampling':
            alg_item['params'] = params
        alg_item['alg_id'] = alg_id
        alg_item['alg_label'] = alg_id+'_'+str(i)
        alg_list.append(alg_item)

    #params = []
    #for algorithm in alg_list:
    #    params.append({'alg_label': algorithm['alg_label'], 'proportion':1./len(alg_list)})
    params = [{'alg_label': 'AR_Random', 'proportion': 10./28},
        {'alg_label': 'Quicksort', 'proportion': 15./28},
        {'alg_label': 'ValidationSampling', 'proportion': 3./28}]
    algorithm_management_settings = {}
    #algorithm_management_settings['mode'] = 'fixed_proportions'
    algorithm_management_settings['mode'] = 'custom'
    algorithm_management_settings['params'] = params

    print algorithm_management_settings

    #################################################
    # Test POST Experiment
    #################################################
    initExp_args_dict = {}
    initExp_args_dict['args'] = {'alg_list': alg_list,
                                 'algorithm_management_settings': algorithm_management_settings,
                                 'context': 'Which place looks safer?',
                                 'context_type': 'text',
                                 'debrief': 'Test debried.',
                                 #'failure_probability': 0.05,
                                 'instructions': 'Test instructions.',
                                 'participant_to_algorithm_management': 'one_to_many',
                                 'targets': {'n': num_arms}}

    initExp_args_dict['app_id'] = app_id
    initExp_args_dict['site_id'] = 'replace this with working site id'
    initExp_args_dict['site_key'] = 'replace this with working site key'

    exp_info = []
    for ell in range(num_experiments):
        print 'launching experiment'
        exp_info += [test_utils.initExp(initExp_args_dict)[1]]
        print 'done launching'

    # Generate participants
    participants = []
    pool_args = []
    for i in range(num_clients):
        participant_uid = '%030x' % random.randrange(16**30)
        participants.append(participant_uid)

        experiment = numpy.random.choice(exp_info)
        exp_uid = experiment['exp_uid']
        pool_args.append((exp_uid, participant_uid, total_pulls_per_client,
                          true_means,assert_200))

    print 'starting to simulate all the clients...'
    results = pool.map(simulate_one_client, pool_args)
    # results = Parallel(n_jobs=num_clients, backend='threading')(
    #             (delayed(simulate_one_client, check_pickle=False)(a) for a in pool_args))
    print 'done simulating clients'

    for result in results:
        result

    #test_utils.getModel(exp_uid, app_id, supported_alg_ids, alg_list)

def simulate_one_client(input_args):
    exp_uid,participant_uid,total_pulls,true_means,assert_200 = input_args

    getQuery_times = []
    processAnswer_times = []
    for t in range(total_pulls):
        print "        Participant {} is pulling {}/{} arms: ".format(participant_uid, t, total_pulls)

        # test POST getQuery #
        # return a widget 1/5 of the time (normally, use HTML)
        widget = random.choice([True] + 4*[False])
        getQuery_args_dict = {'args': {'participant_uid': participant_uid,
                                       'widget': widget},
                              'exp_uid': exp_uid}
        query_dict, dt = test_utils.getQuery(getQuery_args_dict)
        getQuery_times.append(dt)

        if widget:
            query_dict = query_dict['args']
        query_uid = query_dict['query_uid']
        targets = query_dict['target_indices']

        left = targets[0]['target']
        right = targets[1]['target']

        if np.random.random()<1./1000:
            f = open('Drops.log', 'a')
            f.write(str(query_dict)+'\n\n')
            f.close()
            break

        # sleep for a bit to simulate response time
        ts = test_utils.response_delay(mean=0, std=0)

        #  print left
        reward_left = true_means[left['target_id']]# + numpy.random.randn()*0.5
        reward_right = true_means[right['target_id']]# + numpy.random.randn()*0.5
        if reward_left > reward_right:
            target_winner = left
        else:
            target_winner = right

        response_time = time.time() - ts

        # test POST processAnswer 
        processAnswer_args_dict = {'args': {'query_uid': query_uid,
                                            'response_time': response_time,
                                            'target_winner': target_winner["target_id"]},
                                   'exp_uid': exp_uid}
        processAnswer_json_response, dt = test_utils.processAnswer(processAnswer_args_dict)
        processAnswer_times += [dt]


    r = test_utils.format_times(getQuery_times, processAnswer_times, total_pulls,
                   participant_uid)
    print(r)
    return r


if __name__ == '__main__':
    test_api()
    #test_api(assert_200=True, num_arms=5, num_clients=10, delta=0.05,
                #    total_pulls_per_client=10, num_experiments=1)
