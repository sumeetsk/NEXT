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
        arr = butler.algorithms.get(key='arr')
        ptr = butler.algorithms.get(key='ptr')
        pivot = butler.algorithms.get(key='pivot')
        utils.debug_print('In Quicksort: getQuery')
        return [arr[ptr], arr[pivot]]


    def processAnswer(self, butler, left_id=0, right_id=0, winner_id=0):
        utils.debug_print('In Quicksort: processAnswer')
        utils.debug_print('left_id:'+str(left_id))
        utils.debug_print('right_id:'+str(right_id))
        arr = np.array(butler.algorithms.get(key='arr'))
        utils.debug_print('old arr:'+str(arr))
        f = open('Quicksort.log','a')
        f.write('Old arr \n')
        for rownbr in range(len(arr)-1):
            f.write(str(arr[rownbr])+',')
        f.write(str(arr[rownbr+1])+'\n')
        f.close()
        l = butler.algorithms.get(key='l')
        h = butler.algorithms.get(key='h')
        lmax = butler.algorithms.get(key='lmax')
        pivot = butler.algorithms.get(key='pivot')
        stack = butler.algorithms.get(key='stack')
        ptr = butler.algorithms.get(key='ptr')
        ranking = np.array(butler.algorithms.get(key='ranking'))

        if not ((arr[ptr], arr[pivot])==(left_id, right_id) or (arr[ptr], arr[pivot])==(right_id, left_id)):
        #not the query we're looking for, pass
            f = open('Quicksort.log','a')
            f.write("In Quicksort:processAnswer: Query does not match what I'm expecting")
            f.close()
            return True

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

        utils.debug_print('new arr:'+str(arr))
        f = open('Quicksort.log', 'a')
        f.write('New arr \n')
        for rownbr in range(len(arr)-1):
            f.write(str(arr[rownbr])+',')
        f.write(str(arr[rownbr+1])+'\n')
        f.close()
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
