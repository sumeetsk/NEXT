import next.utils as utils
import yaml

from next.database_client.DatabaseAPI import DatabaseAPI
db = DatabaseAPI()
from next.logging_client.LoggerAPI import LoggerAPI
ell = LoggerAPI()

class ResourceManager:
    """
    resource_manager
    Author: Lalit Jain, Kevin Jamieson, Chris Fernandez

    The resource_manager module provides an interface for the api to communicate with experiment, app, particiant and other resources that are being managed through DatabaseAPI and PermStore.

    Usage: ::\n
        from next.api.resource_manager import ResourceManager
        rm = ResourceManager()

        rm.get_app_ids()

        rm.get_app_about('DuelingBanditsPureExploration')

        rm.get_app_alg_ids('PoolBasedTripletMDS')

        rm.get_app_exp_uids('PoolBasedTripletMDS')

        rm.get_app_exp_uid_start_date('P2938RFHAFHAQ3')

        rm.get_experiment('b5242319c78df48f4ff31e78de5857')

        rm.get_algs_for_exp_uid('b5242319c78df48f4ff31e78de5857')
    """

    def get_app_ids(self):
        """
        Returns a list of all implemented app_id's

        Inputs: ::\n
            None

        Outputs: ::\n
            (list of strings) app_id_list : list containing all app_id's that are fully operational in the system

        Usage: ::\n
            rm.get_app_ids()
        """
        return utils.get_supported_apps()

    def get_app_about(self,app_id, apps_dir='apps/'):
        """
        Returns a string description of the app defined by app_id (good for a blurb on a website perhaps)

        Inputs: ::\n
            (string) app_id : app identifier

        Outputs: ::\n
            (string) description : desciption of the app for readability by humans

        Usage: ::\n
            rm.get_app_about('DuelingBanditsPureExploration')
        """
        filename = apps_dir + '{0}/{0}.yaml'.format(app_id)
        info = yaml.load(open(filename, 'rb'))
        return info['initExp']['description']

    def get_app_alg_ids(self,app_id, app_dir='apps/'):
        """
        Returns a list of all implemented alg_id's for a particular app_id

        Inputs: ::\n
            (string) app_id : app identifier

        Outputs: ::\n
            (list of strings) alg_id_list : list containing all alg_id's that are fully operational in the system under the app

        Usage: ::\n
            rm.get_app_alg_ids('PoolBasedTripletMDS')
        """
        filename = app_dir + '{0}/{0}.yaml'.format(app_id)
        exp = yaml.load(open(filename, 'rb'))
        args = exp['initExp']['values']['args']['values']
        return args['alg_list']['values']['values']['alg_id']['values']

    def get_app_exp_uids(self,app_id):
        """
        Returns a dictionary of lists of exp_uid's indexed by app_id

        Inputs: ::\n
            (string) app_id : app identifier

        Outputs: ::\n
            (dict) experiment : dictionary containing pertinent information to the experiment

        Usage: ::\n
            rm.get_app_exp_uids('PoolBasedTripletMDS')
        """
        docs,didSucceed,message = db.get_docs_with_filter(app_id+':experiments',{})
        
        exp_uids = []
        for doc in docs:
            exp_uids.append(str(doc['exp_uid']))

        return exp_uids

    def get_app_exp_uid_start_date(self,exp_uid):
        """
        Returns date in a string when experiment was initiazlied

        Inputs: ::\n
            (string) exp_uid : unique experiment identifier

        Outputs: ::\n
            (datetime) start_date : start date in datetime format

        Usage: ::\n
            rm.get_app_exp_uid_start_date('PoolBasedTripletMDS')
        """
        start_date,didSucceed,message = db.get('experiments_admin',exp_uid,'start_date')

        return start_date

    def get_experiment(self,exp_uid):
        """
        Gets an experiment from an exp_uid. Returns none if the exp_uid is not found.

        Inputs: ::\n
        	(string) exp_uid : unique experiment identifier

        Outputs: ::\n
        	(dict) experiment : dictionary containing pertinent information to the experiment

        Usage: ::\n
        	experiment = rm.get_experiment('b5242319c78df48f4ff31e78de5857')
        """

        app_id = self.get_app_id(exp_uid)

        if app_id == None:
            return None

        docs, didSucceed, message = db.get_docs_with_filter(app_id+':experiments',{'exp_uid':exp_uid})

        if len(docs)>0:
            return docs[0]
        else:
            return None

    def get_app_id(self,exp_uid):
        """
        Gets an app_id from an exp_uid. Returns none if the exp_uid is not found.
        This should be coming from cache so it should be very fast

        Inputs: ::\n
        	exp_uid

        Outputs: ::\n
        	(string) app_id

        Usage: ::\n
        	app_id = rm.get_app_id('b5242319c78df48f4ff31e78de5857')
        """
        app_id,didSucceed,message = db.get('experiments_admin',exp_uid,'app_id')
        return app_id


    def get_algs_doc_for_exp_uid(self,exp_uid):
        """
        Returns the algorithm docs used in exp_uid

        Inputs: ::\n
            (string) exp_uid : unique experiment identifier

        Outputs: ::\n
            (list of dicts) alg_list : list of dicts describing algs implemented in exp_uid with fields:
                (string) alg_id : the alg_id of the algorithm
                (string) alg_label : the unique identiifer of the algorithm, also used in plots

        Usage: ::\n
            alg_list = rm.get_algs_doc_for_exp_uid('b5242319c78df48f4ff31e78de5857')
        """
        app_id = self.get_app_id(exp_uid)
        full_alg_list,didSucceed,message = db.get_docs_with_filter(app_id+':algorithms',{'exp_uid':exp_uid})
        return full_alg_list

    def get_algs_for_exp_uid(self,exp_uid):
        """
        Returns a list of algs' data used in exp_uid

        Inputs: ::\n
            (string) exp_uid : unique experiment identifier

        Outputs: ::\n
            (list of dicts) alg_list : list of dicts describing algs implemented in exp_uid with fields:
                (string) alg_id : the alg_id of the algorithm
                (string) alg_label : the unique identiifer of the algorithm, also used in plots

        Usage: ::\n
            alg_list = rm.get_algs_for_exp_uid('b5242319c78df48f4ff31e78de5857')
        """
        app_id = self.get_app_id(exp_uid)
        args,didSucceed,message = db.get(app_id+':experiments',exp_uid,'args') 
        alg_list = []
        for alg in args['alg_list']:
            tmp = {}
            tmp['alg_id'] = alg['alg_id']
            tmp['alg_label'] = alg['alg_label']
            alg_list.append(tmp)

        return alg_list

    def get_git_hash_for_exp_uid(self,exp_uid):
        """
        Returns git_hash of when exp_uid was initialized

        Inputs: ::\n
            (string) exp_uid : unique experiment identifier

        Outputs: ::\n
            (string) git_hash : the alg_id of the algorithm

        """
        app_id = self.get_app_id(exp_uid)
        git_hash,didSucceed,message = db.get(app_id+':experiments',exp_uid,'git_hash')

        return git_hash

    def get_participant_uids(self,exp_uid):
        """
        Given an exp_uid, returns list of participant_uid's involved with experiment

        Inputs: ::\n
            (string) exp_uid

        Outputs: ::\n
            (list) participant_uids

        Usage: ::\n
            participant_uids = resource_manager.get_participant_uids(exp_uid)
        """
        app_id = self.get_app_id(exp_uid)
        participants,didSucceed,message = db.get_docs_with_filter(app_id+':participants',{'exp_uid':exp_uid})
        participant_uid_list = []
        for participant in participants:
            participant_uid = participant['participant_uid']
            participant_uid_list.append(participant_uid)

        return participant_uid_list

    def get_participant_data(self,participant_uid, exp_uid):
        """
        Given a participant_id and an exp_uid, returns the associated set of responses.

        Inputs: ::\n
        	(string) participant_uid, (string) exp_uid

        Outputs: ::\n
        	(list) responses

        Usage: ::\n
        	responses = resource_manager.get_participant_data(participant_uid,exp_uid)
        """
        app_id = self.get_app_id(exp_uid)
        queries,didSucceed,message = db.get_docs_with_filter(app_id+':queries',{'participant_uid':participant_uid})
        return queries


    def get_experiment_logs(self,exp_uid):
        """
        Given an exp_uid, returns all logs associated with the experiment.

        Inputs: ::\n
            (string) exp_uid

        Outputs: ::\n
            (list) logs

        Usage: ::\n
            responses = resource_manager.get_experiment_logs(exp_uid)
        """

        app_id = self.get_app_id(exp_uid)

        log_types = ['APP-EXCEPTION','ALG-DURATION','ALG-EVALUATION']

        all_logs = []
        for log_type in log_types:
            logs,didSucceed,message = ell.get_logs_with_filter(app_id+':'+log_type,{'exp_uid':exp_uid})
            all_logs.extend(logs)

        return all_logs

    def get_experiment_logs_of_type(self,exp_uid,log_type):
        """
        Given an exp_uid, returns all logs associated with the experiment.

        Inputs: ::\n
            (string) exp_uid, (string) log_type

        Outputs: ::\n
            (list) logs

        Usage: ::\n
            responses = resource_manager.get_experiment_logs(exp_uid,'APP-EXCEPTION')
        """

        app_id = self.get_app_id(exp_uid)

        log_types = ['APP-CALL','APP-RESPONSE','APP-EXCEPTION','ALG-DURATION','ALG-EVALUATION']
        logs,didSucceed,message = ell.get_logs_with_filter(app_id+':'+log_type,{'exp_uid':exp_uid})

        return logs



