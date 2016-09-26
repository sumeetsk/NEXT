"""
Quicksort app implements Quicksort Active Sampling Algorithm
author: Sumeet Katariya, sumeetsk@gmail.com
last updated: 09/20/2016
"""

import numpy as np
import next.utils as utils

class Quicksort:
    app_id = 'ActiveRanking'
    def initExp(self, butler, n=None, params=None):
        butler.algorithms.set(key='n', value=n)
        arr = np.random.permutation(range(n))
        butler.algorithms.set(key='arr', value=arr)
        butler.algorithms.set(key='l', value=0)
        butler.algorithms.set(key='h', value=n-1)
        butler.algorithms.set(key='ptr', value=0)
        butler.algorithms.set(key='lmax', value=-1)
        butler.algorithms.set(key='pivot', value=n-1)
        butler.algorithms.set(key='stack', value= [])
        butler.algorithms.set(key='ranking', value=np.zeros(n))
        return True

    def getQuery(self, butler, participant_uid):
        #print arr
        #print arr[ptr],arr[pivot]
        arr = butler.algorithms.get('arr')
        ptr = butler.algorithms.get('ptr')
        pivot = butler.algorithms.get('pivot')
# pick a random Quicksort
# get a query from this chosen Quicksort
# Add to the butler dictionary a key with the query_uid and a value equal to the chosen quicksort number
# return this query
        return [arr[ptr], arr[pivot]]


    def processAnswer(self, butler, left_id=0, right_id=0, winner_id=0):
        arr = butler.algorithms.get('arr')
        l = butler.algorithms.get('l')
        h = butler.algorithms.get('h')
        lmax = butler.algorithms.get('lmax')
        pivot = butler.algorithms.get('pivot')
        stack = butler.algorithms.get('stack')
        ptr = butler.algorithms.get('ptr')
        ranking = butler.algorithms.get('ranking')
        #pdb.set_trace()

        if winner_id==arr[pivot]:
            lmax = lmax + 1
            arr[lmax],arr[ptr] = arr[ptr],arr[lmax]
        ptr = ptr + 1
        if ptr == h:
            arr[lmax+1],arr[pivot] = arr[pivot],arr[lmax+1]
            if l<lmax:
                stack.append([l,lmax])
            if lmax+2<h:
                stack.append([lmax+2,h])
            if stack==[]:
                ranking = ranking + np.array(arr)
                n = len(arr)
                arr = np.random.permutation(arr)
                l = 0
                h = n-1
                ptr = 0
                lmax = -1
                pivot = n-1
                stack = []
            else:
                x = stack.pop(0)
                l = x[0]
                h = x[1]
                lmax = l-1
                pivot = h
                ptr = l
        butler.algorithms.set(key='arr', value=arr)
        butler.algorithms.set(key='l', value=l)
        butler.algorithms.set(key='h', value=h)
        butler.algorithms.set(key='lmax', value=lmax)
        butler.algorithms.set(key='pivot', value=pivot)
        butler.algorithms.set(key='stack', value=stack)
        butler.algorithms.set(key='ptr', value=ptr)
        butler.algorithms.set(key='ranking', value=ranking)
        #print ranking
        return True

    def getModel(self,butler):
        return range(n), range(n)
