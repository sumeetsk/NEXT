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
        nquicksorts = 8
        butler.algorithms.set(key='nquicksorts', value=nquicksorts)
        butler.algorithms.set(key='n', value=n)

        arrlist = []
        for _ in range(nquicksorts):
            arrlist.append(list(np.random.permutation(range(n))))
        butler.algorithms.set(key='arrlist', value=arrlist)

        butler.algorithms.set(key='llist', value=[0]*nquicksorts)
        butler.algorithms.set(key='hlist', value=[n-1]*nquicksorts)
        butler.algorithms.set(key='ptrlist', value=[0]*nquicksorts)
        butler.algorithms.set(key='lmaxlist', value=[-1]*nquicksorts)
        butler.algorithms.set(key='pivotlist', value=[n-1]*nquicksorts)
        butler.algorithms.set(key='stacklist', value= [[]]*nquicksorts)

        rankinglist = []
        for _ in range(nquicksorts):
            rankinglist.append(np.zeros(n))
        butler.algorithms.set(key='rankinglist', value=rankinglist)
        return True

    def getQuery(self, butler, participant_uid):
        nquicksorts = butler.algorithms.get(key='nquicksorts')
        quicksort_id = np.random.randint(nquicksorts)
        arrlist = butler.algorithms.get(key='arrlist')
        arr = arrlist[quicksort_id]
        ptrlist = butler.algorithms.get(key='ptrlist')
        ptr = ptrlist[quicksort_id]
        pivotlist = butler.algorithms.get(key='pivotlist')
        pivot = pivotlist[quicksort_id]
        return [arr[ptr], arr[pivot], quicksort_id]

    def processAnswer(self, butler, left_id=0, right_id=0, winner_id=0, quicksort_id=0):
        utils.debug_print('In Quicksort: processAnswer')
        utils.debug_print('left_id:'+str(left_id))
        utils.debug_print('right_id:'+str(right_id))
        arrlist = butler.algorithms.get(key='arrlist')
        arr = np.array(arrlist[quicksort_id])
        utils.debug_print('old arrlist:'+str(arrlist))
        f = open('Quicksort.log','a')
        f.write('Old arr \n')
        for rownbr in range(len(arrlist)-1):
            f.write(str(arrlist[rownbr])+',')
        f.write(str(arrlist[rownbr+1])+'\n')
        f.close()
        llist = butler.algorithms.get(key='llist')
        l = llist[quicksort_id]
        hlist = butler.algorithms.get(key='hlist')
        h = hlist[quicksort_id]
        lmaxlist = butler.algorithms.get(key='lmaxlist')
        lmax = lmaxlist[quicksort_id]
        pivotlist = butler.algorithms.get(key='pivotlist')
        pivot = pivotlist[quicksort_id]
        stacklist = butler.algorithms.get(key='stacklist')
        stack = stacklist[quicksort_id]
        ptrlist = butler.algorithms.get(key='ptrlist')
        ptr = ptrlist[quicksort_id]
        rankinglist = butler.algorithms.get(key='rankinglist')
        ranking = np.array(rankinglist[quicksort_id])

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

        arrlist[quicksort_id] = list(arr)
        llist[quicksort_id] = l
        hlist[quicksort_id] = h
        lmaxlist[quicksort_id] = lmax
        pivotlist[quicksort_id] = pivot
        stacklist[quicksort_id] = stack
        ptrlist[quicksort_id] = ptr
        rankinglist[quicksort_id] = list(ranking)

        utils.debug_print('new arr:'+str(arrlist))
        f = open('Quicksort.log', 'a')
        f.write('New arr \n')
        for rownbr in range(len(arrlist)-1):
            f.write(str(arrlist[rownbr])+',')
        f.write(str(arrlist[rownbr+1])+'\n')
        f.close()
        butler.algorithms.set(key='arrlist', value=arrlist)
        butler.algorithms.set(key='llist', value=llist)
        butler.algorithms.set(key='hlist', value=hlist)
        butler.algorithms.set(key='lmaxlist', value=lmaxlist)
        butler.algorithms.set(key='pivotlist', value=pivotlist)
        butler.algorithms.set(key='stacklist', value=stacklist)
        butler.algorithms.set(key='ptrlist', value=ptrlist)
        butler.algorithms.set(key='rankinglist', value=rankinglist)
        return True

    def getModel(self,butler):
        return range(n), range(n)
