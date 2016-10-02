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

        queryqueuesallqs = [] #list of queryqueues for all the quicksorts
        for _ in range(nquicksorts):
            queryqueuesallqs.append([])

        stackparametersallqs = []
        for _ in range(nquicksorts):
            stackparametersallqs.append({})

        for c1 in range(nquicksorts):
            arr = arrlist[c1]
            l = 0
            h = n
            pivot = arr[n-1]
            smallerthanpivot = []
            largerthanpivot = []
            stackvalue = {'l':l, 'h':n, 'pivot':pivot, 'smallerthanpivot':smallerthanpivot, 'largerthanpivot':largerthanpivot, 'count':0}
            stackkey = utils.getNewUID()
            stacks = {stackkey: stackvalue}
            stackparametersallqs[c1] = stacks
            queryqueue = []
            for c2 in range(len(arr)-1):
                queryqueue.append([arr[c2], pivot, [c1,stackkey]])
                #each query maintains a quicksort_id and a stack index (which is stackkey in the beginning)
            queryqueuesallqs[c1] = queryqueue

        butler.algorithms.set(key='stackparametersallqs', value= stackparametersallqs)
        butler.algorithms.set(key='queryqueuesallqs', value=queryqueuesallqs)
        waitingforresponse = []
        for _ in range(nquicksorts):
            waitingforresponse.append({})
        butler.algorithms.set(key='waitingforresponse', value=waitingforresponse)

        ranking = np.zeros(n)
        butler.algorithms.set(key='ranking', value=ranking)

        return True

    def getQuery(self, butler, participant_uid):
        nquicksorts = butler.algorithms.get(key='nquicksorts')
        n = butler.algorithms.get(key='n')
        quicksort_id = np.random.randint(nquicksorts)
        arrlist = butler.algorithms.get(key='arrlist')
        arr = arrlist[quicksort_id]
        queryqueuesallqs = butler.algorithms.get(key='queryqueuesallqs')
        if queryqueuesallqs == [[]]*nquicksorts:
            #all quicksort queues empty: fork a new quicksort
            nquicksorts = nquicksorts + 1
            arr = np.random.permutation(range(n))
            arrlist.append(list(arr))
            stackvalue = {'l':0, 'h':n, 'pivot':arr[-1], 'smallerthanpivot':[], 'largerthanpivot':[], 'count':0}
            stackkey = utils.getNewUID()
            stackparametersallqs.append({stackkey: stackvalue})
            quicksort_id = nquicksorts-1
            queryqueue = []
            for c1 in range(len(arr)-1):
                queryqueue.append([arr[c1], arr[-1], [quicksort_id, stackkey]])
            queryqueuesallqs.append(queryqueue)
            waitingforresponse.append({})
            butler.algorithms.set(key='nquicksorts', value=nquicksorts)
            butler.algorithms.set(key='stackparametersallqs', value= stackparametersallqs)
            butler.algorithms.set(key='arrlist', value=arrlist)
        else:
            while queryqueuesallqs[quicksort_id] == []:
                #current queue empty, switch to a different one
                quicksort_id = np.random.randint(nquicksorts)

        #query = queryqueuesallqs[quicksort_id].pop(0)
        #pop a random query
        query = queryqueuesallqs[quicksort_id].pop(np.random.randint(len(queryqueuesallqs[quicksort_id])))
        butler.algorithms.set(key='queryqueuesallqs', value=queryqueuesallqs)

        waitingforresponse = butler.algorithms.get(key='waitingforresponse')
        waitingforresponse[quicksort_id][str(query[0])+','+str(query[1])] = query
        butler.algorithms.set(key='waitingforresponse', value=waitingforresponse)
        return query

    def processAnswer(self, butler, left_id=0, right_id=0, winner_id=0, quicksort_data=0):
#left_id is actually left item, similarly right_id, winner_id
        utils.debug_print('In Quicksort: processAnswer')
        utils.debug_print('left_id:'+str(left_id))
        utils.debug_print('right_id:'+str(right_id))
        quicksort_id = quicksort_data[0]
        utils.debug_print('quicksort_id'+str(quicksort_id))
        arrlist = butler.algorithms.get(key='arrlist')
        queryqueuesallqs = butler.algorithms.get(key='queryqueuesallqs')
        stackparametersallqs = butler.algorithms.get(key='stackparametersallqs')
        waitingforresponse = butler.algorithms.get(key='waitingforresponse')

        arr = np.array(arrlist[quicksort_id])

        stackkey = quicksort_data[1]

        #utils.debug_print('quicksort_id:'+str(quicksort_id))
        stacks = stackparametersallqs[quicksort_id] #dictionary of stacks for current quicksort_id

        try:
            query = waitingforresponse[quicksort_id][str(left_id)+','+str(right_id)]
        except KeyError:
            #this means that the query response has been received from a different user maybe, and this response should be ignored. This shouldn't happen too often.
            utils.debug_print('Query not found')
            return True
        
        del waitingforresponse[quicksort_id][str(left_id)+','+str(right_id)]
        #if waitingforresponse is empty, it means there might be queries that have not been sent out to users so far.

        curquerystackvalue = stacks[stackkey]
        if winner_id==left_id:
            loser = right_id
        else:
            loser = left_id

        if winner_id==curquerystackvalue['pivot']:
            curquerystackvalue['smallerthanpivot'].append(loser)
        else:
            curquerystackvalue['largerthanpivot'].append(winner_id)

        curquerystackvalue['count'] = curquerystackvalue['count']+1
        if curquerystackvalue['count'] == curquerystackvalue['h']-curquerystackvalue['l']-1:
            del stackparametersallqs[quicksort_id][stackkey]
            l = curquerystackvalue['l']
            h = curquerystackvalue['h']
            smallerthanpivot = curquerystackvalue['smallerthanpivot']
            largerthanpivot = curquerystackvalue['largerthanpivot']
            pivot = curquerystackvalue['pivot']

            #update array
            arr[l:h] = smallerthanpivot + [pivot] + largerthanpivot
            arrlist[quicksort_id] = list(arr)
            butler.algorithms.set(key='arrlist', value=arrlist)

            #create two new stacks
            if len(smallerthanpivot) > 1:
                newstackvalue = {'l':l, 'h':l+len(smallerthanpivot), 'pivot':smallerthanpivot[-1], 'smallerthanpivot':[], 'largerthanpivot':[], 'count':0}
                newstackkey = utils.getNewUID()
                stackparametersallqs[quicksort_id][newstackkey] = newstackvalue
                for c3 in range(len(smallerthanpivot)-1):
                    queryqueuesallqs[quicksort_id].append([smallerthanpivot[c3], smallerthanpivot[-1], [quicksort_id, newstackkey]])
            if len(largerthanpivot) > 1:
                newstackvalue = {'l': l+len(smallerthanpivot)+1, 'h':h, 'pivot':largerthanpivot[-1], 'smallerthanpivot':[], 'largerthanpivot':[], 'count':0}
                newstackkey = utils.getNewUID()
                stackparametersallqs[quicksort_id][newstackkey] = newstackvalue
                for c3 in range(len(largerthanpivot)-1):
                    queryqueuesallqs[quicksort_id].append([largerthanpivot[c3], largerthanpivot[-1], [quicksort_id, newstackkey]])

            if stackparametersallqs[quicksort_id] == {}:
                #if stack is empty

                #1) update ranking
                ranking = np.array(butler.algorithms.get(key='ranking'))
                ranking = ranking + arr
                butler.algorithms.set(key='ranking', value=ranking)
                    
                #2) create a new permutation
                arr = np.random.permutation(range(n))
                arrlist[quicksort_id] = arr
                butler.algorithms.set(key='arrlist', value=arrlist)
        
                #3) add queries to queue, and stack parameters to stack
                stackvalue = {'l':0, 'h':len(arr), 'pivot':arr[-1], 'smallerthanpivot':[], 'largerthanpivot':[], 'count':0}
                stackkey = utils.getNewUID()
                stackparametersallqs[quicksort_id] = {stackkey: stackvalue}
                for c4 in range(len(arr)-1):
                    queryqueuesallqs[quicksort_id].append([arr[c4], arr[-1], [quicksort_id, stackkey]])

        #write everything back
        butler.algorithms.set(key='stackparametersallqs', value=stackparametersallqs)
        butler.algorithms.set(key='queryqueuesallqs', value=queryqueuesallqs)
        butler.algorithms.set(key='waitingforresponse', value=waitingforresponse)
        
        utils.debug_print('stackparametersallqs')
        for x in stackparametersallqs:
            utils.debug_print(str(x))

        utils.debug_print('new arr:')
        for x in arrlist:
            utils.debug_print(str(x))
        return True

    def getModel(self,butler):
        return range(n), range(n)
