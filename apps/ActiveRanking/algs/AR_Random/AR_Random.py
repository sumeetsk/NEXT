"""
AR_Random app implements Active ranking Random
author: Sumeet Katariya, sumeetsk@gmail.com
last updated: 09/24/2016

AR_Random implements random sampling 
"""

import numpy as np
import next.utils as utils
#import pickle
#import logging
#logging.basicConfig(filename='logging_AR_Random.log', level=logging.DEBUG, filemode='w')

class AR_Random:
    app_id = 'ActiveRanking'
    def initExp(self, butler, n=None, params=None):
        """
        This function is meant to set keys used later by the algorith implemented
        in this file.
        """
        butler.algorithms.set(key='n', value=n)

        W = np.zeros((n,n))

        butler.algorithms.set(key='W', value=W)
        f = open('AR_Random.log','w')
        f.close()
        #with open('pickle_log.pkl', 'wb') as f:
        #    pickle.dump({'obj': 'obj'}, f)

        return True

    def getQuery(self, butler, participant_uid):
        utils.debug_print('In AR_Random: getQuery')
        n = butler.algorithms.get(key='n')

        index = np.random.randint(n)
        alt_index = np.random.randint(n)
        while alt_index == index:
            alt_index = np.random.randint(n)

        return [index, alt_index, 0]

    def processAnswer(self, butler, left_id=0, right_id=0, winner_id=0, quicksort_data=0):
        utils.debug_print('In AR_Random: processAnswer')
        utils.debug_print('left_id:'+str(left_id))
        utils.debug_print('right_id:'+str(right_id))
        W = np.array(butler.algorithms.get(key='W'))
        utils.debug_print('old W:'+str(W))
        f = open('AR_Random.log','a')
        f.write(str([left_id,right_id,winner_id])+'\n')
        f.close()
        #f.write('Old W \n')
        #for rownbr in range(np.shape(W)[0]):
        #    for colnbr in range(np.shape(W)[1]-1):
        #        f.write(str(W[rownbr, colnbr])+',')
        #    f.write(str(W[rownbr, colnbr+1])+'\n')
        #f.write('\n')
        #f.close()
        if left_id == winner_id:
            W[left_id, right_id] = W[left_id, right_id] + 1
        else:
            W[right_id, left_id] = W[right_id, left_id] + 1

        butler.algorithms.set(key='W', value=W)
        #logging.debug('W = ',W) 
        utils.debug_print('new W:'+str(W))
        return True

    def getModel(self,butler):
        W = butler.algorithms.get(key='W')
        return W, range(5)
