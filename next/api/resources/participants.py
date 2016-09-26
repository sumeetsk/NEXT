"""
next_backend Participant Resource 
author: Christopher Fernandez, Lalit Jain
Resource for accessing all participant data related to a resource
"""

'''
example use:
get a tripletMDS query:
curl -X GET http://localhost:8001/api/experiment/[exp_uid]/participants
'''
from flask import Flask, send_file, request
from flask_restful import Resource, reqparse

import json
from io import BytesIO 
import zipfile

import next.utils
import next.api.api_util as api_util
from next.api.api_util import APIArgument
from next.api.resource_manager import ResourceManager

resource_manager = ResourceManager()

# Request parser. Checks that necessary dictionary keys are available in a given resource.
# We rely on learningLib functions to ensure that all necessary arguments are available and parsed. 
post_parser = reqparse.RequestParser(argument_class=APIArgument)

# Custom errors for GET and POST verbs on experiment resource
meta_error = {
    'ExpDoesNotExistError': {
        'message': "No experiment with the specified experiment ID exists.",
        'code': 400,
        'status':'FAIL'
    },
}

meta_success = {
    'code': 200,
    'status': 'OK'
}

# Participants resource class
class Participants(Resource):
    def get(self, exp_uid):
        """
        .. http:get:: /experiment/<exp_uid>/participants

        Get all participant response data associated with a given exp_uid.

        **Example request**:

        .. sourcecode:: http

        GET /experiment/<exp_uid>/participants HTTP/1.1
        Host: next_backend.next.discovery.wisc.edu

        **Example response**:

        .. sourcecode:: http
        
        HTTP/1.1 200 OK
        Vary: Accept
        Content-Type: application/json

        {
        	participant_responses: [participant_responses]
        	status: {
        		code: 200,
        		status: OK,
       		},
        }
        
        :>json all_participant_responses: list of all participant_responses

        :statuscode 200: Participants responses successfully returned
        :statuscode 400: Participants responses failed to be generated
    	"""
        zip_true = False
        if request.args.get('zip'):
            try:
                zip_true = eval(request.args.get('zip'))
            except:
                pass
            
        # Get all participants for exp_uid from resource_manager
        participant_uids = resource_manager.get_participant_uids(exp_uid)
        participant_responses = {}

        # Iterate through list of all participants for specified exp_uid
        for participant in participant_uids:
            response = resource_manager.get_participant_data(participant,
                                                             exp_uid)
            # Append participant query responses to list
            participant_responses[participant] = response

        all_responses = {'participant_responses': participant_responses}
        if zip_true:
            zip_responses = BytesIO()
            with zipfile.ZipFile(zip_responses, 'w') as zf:
                zf.writestr('participants.json', json.dumps(all_responses))
            zip_responses.seek(0)
        
            return send_file(zip_responses,
                             attachment_filename='participants.zip',
                             as_attachment='True')
        else:
            return api_util.attach_meta(all_responses, meta_success), 200
