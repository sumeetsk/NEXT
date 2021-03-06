"""
Quicksort app implements Quicksort Active Sampling Algorithm
author: Sumeet Katariya, sumeetsk@gmail.com
last updated: 09/20/2016
"""

import numpy as np
import random
#import next.utils as utils
import pdb
import string
from termcolor import colored

class Quicksort:
    #def __init__(self, butler, n=None, params=None):
    def __init__(self, n=None):
        global nquicksorts, arrlist, queryqueuesallqs, stackparametersallqs, waitingforresponse, ranking

        nquicksorts = 10
        #butler.algorithms.set(key='nquicksorts', value=nquicksorts)
        #butler.algorithms.set(key='n', value=n)

        arrlist = []
        for _ in range(nquicksorts):
            arrlist.append(list(np.random.permutation(range(n))))
        #butler.algorithms.set(key='arrlist', value=arrlist)

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
            stackkey = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(32))
            #stackkey = utils.getNewUID()
            stacks = {stackkey: stackvalue}
            stackparametersallqs[c1] = stacks
            queryqueue = []
            for c2 in range(len(arr)-1):
                queryqueue.append([arr[c2], pivot, [c1,stackkey]])
                #each query maintains a quicksort_id and a stack index (which is stackkey in the beginning)
            queryqueuesallqs[c1] = queryqueue

        #butler.algorithms.set(key='stackparametersallqs', value= stackparametersallqs)
        #butler.algorithms.set(key='queryqueuesallqs', value=queryqueuesallqs)
        waitingforresponse = []
        for _ in range(nquicksorts):
            waitingforresponse.append({})
        #butler.algorithms.set(key='waitingforresponse', value=waitingforresponse)

        ranking = np.zeros(n)
        #butler.algorithms.set(key='ranking', value=ranking)
        return None

    #def getQuery(self, butler, participant_uid):
    def getQuery(self):
        global nquicksorts, n, arrlist, queryqueuesallqs, stackparametersallqs, waitingforresponse, ranking

        #nquicksorts = butler.algorithms.get(key='nquicksorts')
        quicksort_id = np.random.randint(nquicksorts)
        #arrlist = butler.algorithms.get(key='arrlist')
        arr = arrlist[quicksort_id]
        #queryqueuesallqs = butler.algorithms.get(key='queryqueuesallqs')
        while queryqueuesallqs[quicksort_id] == []:
            #sumeet: if all queues empty, what?
            quicksort_id = np.random.randint(nquicksorts)

        query = queryqueuesallqs[quicksort_id].pop(0)
        #butler.algorithms.set(key='queryqueuesallqs', value=queryqueuesallqs)

        #waitingforresponse = butler.algorithms.get(key='waitingforresponse')
        waitingforresponse[quicksort_id][str(query[0])+','+str(query[1])] = query
        #butler.algorithms.set(key='waitingforresponse', value=waitingforresponse)
        return query

    #def processAnswer(self, butler, left_id=0, right_id=0, winner_id=0, quicksort_data=0):
    def processAnswer(self, left_id=0, right_id=0, winner_id=0, quicksort_data=0):
#left_id is actually left item, similarly right_id, winner_id
        global nquicksorts, n, arrlist, queryqueuesallqs, stackparametersallqs, waitingforresponse, ranking

        #utils.debug_print('In Quicksort: processAnswer')
        #utils.debug_print('left_id:'+str(left_id))
        #utils.debug_print('right_id:'+str(right_id))
        quicksort_id = quicksort_data[0]
        #arrlist = butler.algorithms.get(key='arrlist')
        #queryqueuesallqs = butler.algorithms.get(key='queryqueuesallqs')
        #stackparametersallqs = butler.algorithms.get('stackparametersallqs')
        #waitingforresponse = butler.algorithms.get('waitingforresponse')

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
            #butler.algorithms.set(key='arrlist', value=arrlist)

            #create two new stacks
            if len(smallerthanpivot) > 1:
                newstackvalue = {'l':l, 'h':l+len(smallerthanpivot), 'pivot':smallerthanpivot[-1], 'smallerthanpivot':[], 'largerthanpivot':[], 'count':0}
                #newstackkey = utils.getNewUID()
                newstackkey = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(32))
                stackparametersallqs[quicksort_id][newstackkey] = newstackvalue
                for c3 in range(len(smallerthanpivot)-1):
                    queryqueuesallqs[quicksort_id].append([smallerthanpivot[c3], smallerthanpivot[-1], [quicksort_id, newstackkey]])
            if len(largerthanpivot) > 1:
                newstackvalue = {'l': l+len(smallerthanpivot)+1, 'h':h, 'pivot':largerthanpivot[-1], 'smallerthanpivot':[], 'largerthanpivot':[], 'count':0}
                #newstackkey = utils.getNewUID()
                newstackkey = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(32))
                stackparametersallqs[quicksort_id][newstackkey] = newstackvalue
                for c3 in range(len(largerthanpivot)-1):
                    queryqueuesallqs[quicksort_id].append([largerthanpivot[c3], largerthanpivot[-1], [quicksort_id, newstackkey]])

            if stackparametersallqs[quicksort_id] == {}:
                #if stack is empty

                #1) update ranking
                #ranking = np.array(butler.algorithms.get(key='ranking'))
                ranking = ranking + arr
                #butler.algorithms.set(key='ranking', value=ranking)
                    
                #2) create a new permutation
                arr = np.random.permutation(range(n))
                arrlist[quicksort_id] = arr
                #butler.algorithms.set(key='arrlist', value=arrlist)
        
                #3) add queries to queue, and stack parameters to stack
                stackvalue = {'l':0, 'h':len(arr), 'pivot':arr[-1], 'smallerthanpivot':[], 'largerthanpivot':[], 'count':0}
                stackkey = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(32))
                #stackkey = utils.getNewUID()
                stackparametersallqs[quicksort_id] = {stackkey: stackvalue}
                for c4 in range(len(arr)-1):
                    queryqueuesallqs[quicksort_id].append([arr[c4], arr[-1], [quicksort_id, stackkey]])

        #write everything back
        #butler.algorithms.write(key='stackparametersallqs', value=stackparametersallqs)
        #butler.algorithms.set(key='queryqueuesallqs', value=queryqueuesallqs)
        #butler.algorithms.set(key='waitingforresponse', value=waitingforresponse)
        

        #utils.debug_print('new arr:'+str(arrlist))
        return True

    #def getModel(self,butler):
    #    return range(n), range(n)

def user_response(a,b):
    if a<b:
        return b
    else:
        return a

if __name__ == "__main__":
    #nusers = 100
    #queriesperuser = 50
    global nquicksorts, arrlist, queryqueuesallqs, stackparametersallqs, waitingforresponse, ranking
    nusers = 10
    queriesperuser = 50
    queryforuser = []
    for _ in range(nusers):
        queryforuser.append([])
    
    mean_time_between_user_arrival = 1.
    mean_time_taken_to_click = 0.1

    QSobj = Quicksort(n=20)

    arrival_times = np.reshape(np.cumsum(np.random.exponential(size=(nusers,1), scale = mean_time_between_user_arrival)), (nusers,1))
    clicktimes = np.cumsum(np.random.exponential(size = (nusers, queriesperuser), scale=mean_time_taken_to_click), axis=1)
    times = np.hstack((arrival_times, np.tile(arrival_times, (1,queriesperuser)) + clicktimes))
    times = [list(x) for x in times]
    while True:
        times_under_consideration = []
        for c1 in range(nusers):
            if times[c1] != []:
                times_under_consideration.append(times[c1][0])
            else:
                times_under_consideration.append(float("inf"))

        userindex = np.argmin(times_under_consideration)
        print userindex
        #pdb.set_trace()
        try:
            times[userindex].pop(0)
        except:
            break
        if len(times[userindex]) == queriesperuser:
            #this is the first arrival
            queryforuser[userindex] = QSobj.getQuery()
        elif len(times[userindex]) == 0:
            #this is his last query
            query = queryforuser[userindex]
            winner = user_response(query[0], query[1])
            QSobj.processAnswer(query[0], query[1], winner, query[2])
            queryforuser[userindex] = []
        else:
            query = queryforuser[userindex]
            winner = user_response(query[0], query[1])
            QSobj.processAnswer(query[0], query[1], winner, query[2])
            queryforuser[userindex] = QSobj.getQuery()
        print colored('User: ','red') + str(userindex)
        print colored('Queries with users: ','red') + str(queryforuser)
        print colored('Query queues for all quicksorts: ','red') #+ str(queryqueuesallqs)
        for x in queryqueuesallqs:
            print x
        print colored('Waiting for response on: ','red') + str(waitingforresponse)
        print colored('Stack: ','red') + str(stackparametersallqs)
        #pdb.set_trace()

    pdb.set_trace()
