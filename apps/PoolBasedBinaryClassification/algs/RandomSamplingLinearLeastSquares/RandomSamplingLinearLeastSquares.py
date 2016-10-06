import time
import numpy.random
import next.utils as utils

class RandomSamplingLinearLeastSquares:
    def initExp(self, butler, n, d, failure_probability):
        # Save the number of targets, dimension, and failure_probability to algorithm storage
        butler.algorithms.set(key='n',value= n)
        butler.algorithms.set(key='delta',value= failure_probability)
        butler.algorithms.set(key='d',value= d)
        
        # Initialize the weight to an empty list of 0's
        butler.algorithms.set(key='weights',value=[0]*(d+1))
        butler.algorithms.set(key='num_reported_answers', value=0)
        return True

    def getQuery(self, butler, participant_uid):
        # Retrieve the number of targets and return the index of one at random
        n = butler.algorithms.get(key='n')
        idx = numpy.random.choice(n)
        return idx

    def processAnswer(self, butler, target_index, target_label):
        # S maintains a list of labelled items. Appending to S will create it.
        butler.algorithms.append(key='S',value=(target_index,target_label))
        # Increment the number of reported answers by one.
        num_reported_answers = butler.algorithms.increment(key='num_reported_answers')

        # Run a model update job after every d answers
        d = butler.algorithms.get(key='d')
        if num_reported_answers % int(d) == 0:
            butler.job('full_embedding_update', {}, time_limit=30)
        return True


    def getModel(self, butler):
        # The model is simply the vector of weights and a record of the number of reported answers.
        utils.debug_print(butler.algorithms.get(key=['weights','num_reported_answers']))
        return butler.algorithms.get(key=['weights','num_reported_answers'])


    def full_embedding_update(self, butler, args):
        # Main function to update the model.
        labelled_items = butler.algorithms.get(key='S')
        # Get the list of targets.
        targets = butler.targets.get_targetset(butler.exp_uid)
        # Extract the features form each target and then append a bias feature.
        target_features = [targets[i]['meta']['features'] for i in range(len(targets))]
        for feature_vector in target_features:
            feature_vector.append(1.)
        # Build a list of feature vectors and associated labels.
        X = []
        y = []
        for index, label in labelled_items:
            X.append(target_features[index])
            y.append(label)
        # Convert to numpy arrays and use lstsquares to find the weights.
        X = numpy.array(X)
        y = numpy.array(y)
        weights = numpy.linalg.lstsq(X,y)[0]
        # Save the weights under the key weights.
        butler.algorithms.set(key='weights',value=weights.tolist())
