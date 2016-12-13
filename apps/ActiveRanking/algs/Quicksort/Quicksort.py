"""
Quicksort app implements Quicksort Active Sampling Algorithm
author: Sumeet Katariya, sumeetsk@gmail.com
last updated: 09/20/2016
"""

import numpy as np
from datetime import datetime
import dateutil.parser
import next.utils as utils
import random
import time

#def waitUntilDBClear(butler):
#    while butler.algorithms.get(key='wait'):
#        time.sleep(1e-3)
#    butler.algorithms.set(key='wait', value=True)

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
                queryqueue.append([arr[c2], pivot, [c1,stackkey,'0']])
                #each query maintains a quicksort_id, a stack index (which is stackkey in the beginning), and a time when it was sent out, which is added when it is sent. That is why the sent time is '0' for now. It is also set to '0' if the query was removed from waitingforresponse because the response did not arrive within the prescribed limit.
            queryqueuesallqs[c1] = queryqueue

        butler.algorithms.set(key='stackparametersallqs', value= stackparametersallqs)
        butler.algorithms.set(key='queryqueuesallqs', value=queryqueuesallqs)
        waitingforresponse = []
        for _ in range(nquicksorts):
            waitingforresponse.append({})
        butler.algorithms.set(key='waitingforresponse', value=waitingforresponse)

        ranking = np.zeros(n)
        butler.algorithms.set(key='ranking', value=ranking)
        #butler.algorithms.set(key='wait', value=False)

        return True

    def getQuery(self, butler, participant_uid):
        #waitUntilDBClear(butler)
        lock = butler.memory.lock('lock')
        lock.acquire()

        nquicksorts = butler.algorithms.get(key='nquicksorts')
        n = butler.algorithms.get(key='n')
        arrlist = butler.algorithms.get(key='arrlist')
        queryqueuesallqs = butler.algorithms.get(key='queryqueuesallqs')
        waitingforresponse = butler.algorithms.get(key='waitingforresponse')
        stackparametersallqs = butler.algorithms.get(key='stackparametersallqs')

        #for all quicksort_ids, check if there are any queries that have been lying around in waitingforresponse for a long time
        cur_time = datetime.now()
        for qsid in range(nquicksorts): 
            for key in waitingforresponse[qsid]:
                senttimeiniso = waitingforresponse[qsid][key][2][2]
                if senttimeiniso == '0':
                    continue #this query has been added to the queue already
                else:
                    senttime = dateutil.parser.parse(senttimeiniso)

                    timepassedsincesent = cur_time - senttime
                    timepassedsincesentinsecs = timepassedsincesent.total_seconds()
                    if timepassedsincesentinsecs > 50:
                        query = waitingforresponse[qsid][key]
                        query[2][2] = '0'
                        queryqueuesallqs[qsid].append(query)
                        #utils.debug_print('time exceeded query: ' + str(query))
                        waitingforresponse[qsid][key] = query #setting time to '0' indicates that the query has been added to the queue, avoid repeat additions.

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
                queryqueue.append([arr[c1], arr[-1], [quicksort_id, stackkey, '0']])
            queryqueuesallqs.append(queryqueue)
            waitingforresponse.append({})
            butler.algorithms.set(key='nquicksorts', value=nquicksorts)
            butler.algorithms.set(key='stackparametersallqs', value= stackparametersallqs)
            butler.algorithms.set(key='arrlist', value=arrlist)

        #if any item from the previous query is repeated, sample a new quicksort_id
        #last_query = butler.participants.get(key='last_query')
        #if last_query == None:
        #    butler.participants.set(key='last_query', value=(-1,-1))
        #    last_query = butler.participants.get(key='last_query')

        ##utils.debug_print('last_query='+str(last_query))

        #item_repeated_last_query_count = 0
        #while item_repeated_last_query_count<10:
        #    quicksort_id = np.random.randint(nquicksorts)

        #    while queryqueuesallqs[quicksort_id] == []:
        #        #current queue empty, switch to a different one
        #        quicksort_id = np.random.randint(nquicksorts)

        #    query_index = np.random.randint(len(queryqueuesallqs[quicksort_id]))
        #    potential_query = queryqueuesallqs[quicksort_id][query_index]
        #    query_tuple = (potential_query[0], potential_query[1])

        #    if not any(x in query_tuple for x in last_query): #no repetition
        #        break
        #    else:
        #        f = open('Repeats.log', 'a')
        #        f.write(str(query_tuple)+'\n')
        #        f.write('Query item repeated\n')
        #        f.close()
        #        item_repeated_last_query_count += 1

        #pop the query
        quicksort_id = np.random.randint(nquicksorts)

        while queryqueuesallqs[quicksort_id] == []:
            #current queue empty, switch to a different one
            quicksort_id = np.random.randint(nquicksorts)
        query_index = np.random.randint(len(queryqueuesallqs[quicksort_id])) #removed last_query business
        query = queryqueuesallqs[quicksort_id].pop(query_index)
        #flip with 50% chance
        if random.choice([True,False]):
            query[0],query[1] = query[1],query[0]

        #butler.participants.set(key='last_query', value=(query[0], query[1]))


        #add timestamp to query
        query[2][2] = datetime.now().isoformat()
        smallerindexitem = min(query[0], query[1])
        largerindexitem = max(query[0], query[1])
        waitingforresponse[quicksort_id][str(smallerindexitem)+','+str(largerindexitem)] = query

        f = open('Quicksort.log','a')
        f.write('In getQuery\n')
        #f.write('Quicksort_id: ' + str(quicksort_id)+'\n')
        f.write('Query being shown: ' + str(query)+'\n')

        f.write('arrlist:\n')
        for x in arrlist:
            f.write(str(x)+'\n')

        f.write('Query queues:\n')
        for l1 in queryqueuesallqs:
            for l2 in l1:
                f.write(str([l2[0],l2[1]])+', ')
            f.write('\n')

        f.write('waitingforresponse:\n')
        cd = 0
        for d in waitingforresponse:
            f.write(str(cd)+'\n')
            cd = cd+1
            if d=={}:
                continue
            for k in d.keys():
                f.write('('+k+'), ')
            f.write('\n')

        f.write('Stack:\n')
        cd = 0
        for l in stackparametersallqs:
            f.write(str(cd)+'\n')
            cd = cd+1
            for k in l.keys():
                v = l[k]
                f.write('[l:'+str(v['l'])+',h:'+str(v['h'])+',count:'+str(v['count'])+',smaller:'+str(v['smallerthanpivot'])+',larger:'+str(v['largerthanpivot'])+',pivot:'+str(v['pivot'])+']\n')

        #utils.debug_print('quicksort_id: ' + str(quicksort_id))
        #utils.debug_print('queryqueuesallqs')
        #for x in queryqueuesallqs:
        #    utils.debug_print(str(x))

        #utils.debug_print('stackparametersallqs')
        #for x in stackparametersallqs:
        #    utils.debug_print(str(x))

        #utils.debug_print('waitingforresponse')
        #for x in waitingforresponse:
        #    utils.debug_print(str(x))

        #utils.debug_print('new arr:')
        #for x in arrlist:
        #    utils.debug_print(str(x))

        butler.algorithms.set(key='waitingforresponse', value=waitingforresponse)
        butler.algorithms.set(key='queryqueuesallqs', value=queryqueuesallqs)
        butler.algorithms.set(key='stackparametersallqs', value=stackparametersallqs)
        #butler.algorithms.set(key='wait', value=False)

        f.write('\n')
        f.close()
        utils.debug_print('In Quicksort getQuery: Current Query ' + str(query))
        lock.release()
        return query

    def processAnswer(self, butler, left_id=0, right_id=0, winner_id=0, quicksort_data=0):
#left_id is actually left item, similarly right_id, winner_id
        #waitUntilDBClear(butler)
        lock = butler.memory.lock('lock')
        lock.acquire()
        
        quicksort_id = quicksort_data[0]
        f = open('Quicksort.log','a')
        bugfile = open('Bugs.log', 'a')

        f.write('In processAnswer\n')
        f.write(str([quicksort_id, left_id, right_id, winner_id]) + '\n')
        utils.debug_print('In Quicksort processAnswer: Winner id ' + str([quicksort_id, left_id, right_id, winner_id]))

        nquicksorts = butler.algorithms.get(key='nquicksorts')
        n = butler.algorithms.get(key='n')
        arrlist = butler.algorithms.get(key='arrlist')
        queryqueuesallqs = butler.algorithms.get(key='queryqueuesallqs')
        stackparametersallqs = butler.algorithms.get(key='stackparametersallqs')
        waitingforresponse = butler.algorithms.get(key='waitingforresponse')

        arr = np.array(arrlist[quicksort_id])

        stackkey = quicksort_data[1]

        stacks = stackparametersallqs[quicksort_id] #dictionary of stacks for current quicksort_id

        smallerindexitem = min(left_id, right_id)
        largerindexitem = max(left_id, right_id)
        try:
            query = waitingforresponse[quicksort_id][str(smallerindexitem)+','+str(largerindexitem)]
        except KeyError:
            #this means that the query response has been received from a different user maybe, and this response should be ignored. This shouldn't happen too often.
            f.write('Query not found\n\n')
            bugfile.write(str([quicksort_id, left_id, right_id, winner_id]) + '\n')
            bugfile.write('Query not found\n\n')
            #utils.debug_print('Query not found')
            f.write('\n')
            f.close()
            bugfile.close()
            lock.release()
            #butler.algorithms.set(key='wait', value=False)
            return True
        
        del waitingforresponse[quicksort_id][str(smallerindexitem)+','+str(largerindexitem)]
        #if waitingforresponse is empty, it means there might be queries that have not been sent out to users so far.

        #if this query was added to the queue again to be resent because the first response wasn't received soon, delete it from the queue - the response has been received.
        for q in queryqueuesallqs[quicksort_id]:
            if ((q[0]==left_id and q[1]==right_id) or (q[0]==right_id and q[1]==left_id)):
                queryqueuesallqs[quicksort_id].remove(q)
                break

        curquerystackvalue = stacks[stackkey]
        if winner_id==left_id:
            loser = right_id
        else:
            loser = left_id

        #second check to make sure this response hasn't been recorded already. Check that the non-pivot id is not in the smallerthanpivot or largerthanpivot list
        nonpivot_id = (left_id==curquerystackvalue['pivot'])*right_id + (right_id==curquerystackvalue['pivot'])*left_id
        if nonpivot_id in curquerystackvalue['smallerthanpivot'] or nonpivot_id in curquerystackvalue['largerthanpivot']:
            bugfile.write(str([quicksort_id, left_id, right_id, winner_id]) + '\n')
            bugfile.write(str(curquerystackvalue)+'\n')
            bugfile.write('Response for this query has already been recorded\n\n')
            f.write('Response for this query has already been recorded\n\n')
            f.write('\n')
            f.close()
            bugfile.close()
            lock.release()
            #butler.algorithms.set(key='wait', value=False)
            return True


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
                    queryqueuesallqs[quicksort_id].append([smallerthanpivot[c3], smallerthanpivot[-1], [quicksort_id, newstackkey, '0']])
            if len(largerthanpivot) > 1:
                newstackvalue = {'l': l+len(smallerthanpivot)+1, 'h':h, 'pivot':largerthanpivot[-1], 'smallerthanpivot':[], 'largerthanpivot':[], 'count':0}
                newstackkey = utils.getNewUID()
                stackparametersallqs[quicksort_id][newstackkey] = newstackvalue
                for c3 in range(len(largerthanpivot)-1):
                    queryqueuesallqs[quicksort_id].append([largerthanpivot[c3], largerthanpivot[-1], [quicksort_id, newstackkey, '0']])

            if stackparametersallqs[quicksort_id] == {}:
                #if stack is empty

                #1) update ranking
                ranking = np.array(butler.algorithms.get(key='ranking'))
                ranking = ranking + arr
                g = open('QSranking.log','a')
                g.write(str(arr)+'\n')
                g.close()
                butler.algorithms.set(key='ranking', value=ranking)
                f.write('ranking = '+str(ranking)+'\n')
                    
                #2) create a new permutation
                arr = np.random.permutation(range(n))
                arrlist[quicksort_id] = arr
                butler.algorithms.set(key='arrlist', value=arrlist)
        
                #3) add queries to queue, and stack parameters to stack
                stackvalue = {'l':0, 'h':len(arr), 'pivot':arr[-1], 'smallerthanpivot':[], 'largerthanpivot':[], 'count':0}
                stackkey = utils.getNewUID()
                stackparametersallqs[quicksort_id] = {stackkey: stackvalue}
                for c4 in range(len(arr)-1):
                    queryqueuesallqs[quicksort_id].append([arr[c4], arr[-1], [quicksort_id, stackkey, '0']])

        #write everything back
        butler.algorithms.set(key='stackparametersallqs', value=stackparametersallqs)
        butler.algorithms.set(key='queryqueuesallqs', value=queryqueuesallqs)
        butler.algorithms.set(key='waitingforresponse', value=waitingforresponse)
        #butler.algorithms.set(key='wait', value=False)

        f.write('arrlist:\n')
        for x in arrlist:
            f.write(str(x)+'\n')

        f.write('Query queues:\n')
        for l1 in queryqueuesallqs:
            for l2 in l1:
                f.write(str([l2[0],l2[1]])+', ')
            f.write('\n')

        f.write('waitingforresponse:\n')
        cd = 0
        for d in waitingforresponse:
            f.write(str(cd)+'\n')
            cd = cd+1
            if d=={}:
                continue
            for k in d.keys():
                f.write('('+k+'), ')
            f.write('\n')

        f.write('Stack:\n')
        cd = 0
        for l in stackparametersallqs:
            f.write(str(cd)+'\n')
            cd = cd+1
            for k in l.keys():
                v = l[k]
                f.write('[l:'+str(v['l'])+',h:'+str(v['h'])+',count:'+str(v['count'])+',smaller:'+str(v['smallerthanpivot'])+',larger:'+str(v['largerthanpivot'])+',pivot:'+str(v['pivot'])+']\n')
        
        f.write('\n')
        f.close()
        bugfile.close()

        f = open('Queries.log','a')
        f.write('QS ' + str([quicksort_data[0],left_id,right_id,winner_id])+'\n')
        f.close()

        f = open('QuicksortArraysAnalysis.log', 'a')
        f.write(str([quicksort_id, left_id, right_id, winner_id]) + '\n')
        f.write('arrlist:\n')
        for x in arrlist:
            f.write(str(x)+'\n')
        f.write('\n')
        f.close()
        lock.release()
        return True

    def getModel(self,butler):
        return range(5), range(5)
