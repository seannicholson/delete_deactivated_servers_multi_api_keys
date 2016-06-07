###############################################################################
# Import statements
# This script requires the following Python modules
# json, base64, requests, datetime, sys, argparse, pytz, iso8601, os, os.path
# use PIP import for these if you are encountering errors for pytz, requests,
# iso8601
#   > pip install requests, pytz, iso8601
#

import json, base64, requests, datetime, sys, argparse, pytz, iso8601
import os, os.path

from config import apiurl, deactivate_num_days, deleteServerGroupName, api_keys_path

###############################################################################


###############################################################################
# Variables
# Please edit these values in the config.auth.  You can find these information
# from HALO "[Site Administration] -> [API Keys]" page


api_request_url = apiurl
user_credential_b64 = ''
headers = {}
deleteServerGroupName = deleteServerGroupName
api_key_loop_counter = 0
PATH = api_keys_path

if not (deleteServerGroupName):
    print "NO GROUP TO DELETE SERVERS FROM CONFIGRED!"
    print "Please configure deactivated servers group in config.py"
    print "deleteServerGroupName= \" \""
    print "Exiting..."
    sys.exit(1)

###############################################################################


###############################################################################
# Define Methods

# Calls get_access_token and takes returned token value to Create
# request headers
def get_headers():
    # Create headers
    reply = get_access_token(api_request_url, "/oauth/access_token?grant_type=client_credentials",
                             {"Authorization": user_credential_b64})
    reply_clean = reply.encode('utf-8')
    headers = {"Content-type": "application/json", "Authorization": "Bearer " + reply_clean}
    #print headers
    return headers

# Request Bearer token and return access_token
def get_access_token(url, query_string, headers):
    reply = requests.post(url + query_string, headers=headers)
    return reply.json()["access_token"]

# Uses requests PUT command to send json to move group via API call
def delete_server(host_id):
    status_code = str("404")
    retry_loop_counter = 0
    deleteurl = apiurl + "/v1/servers/" + host_id
    #print ("URL: %s") % moveurl
    #print ("Request Body: %s" % data)

    # Loop to attempt server move PUT request
    # will retry 4 times to move server if status_code not 204
    while (retry_loop_counter < 3):
        reply = requests.delete( deleteurl, headers=headers)
        status_code = str(reply.status_code)
        #print ("Result of group move: %s" % status_code)
        retry_loop_counter += 1
        if status_code == "204":
            # Arbitrary number to exit loop
            retry_loop_counter = 5
            return True
        else:
            print "Failed to delete server...Retry attempt %d" % retry_loop_counter

def get_deactivated_server_list():
    deactivatedServersURL = api_request_url + "/v1/servers?state=deactivated&group_name=" + deleteServerGroupName
    reply = requests.request("GET", deactivatedServersURL, data=None, headers=headers)
    return reply

def delete_deactivated_servers():
    global deleteServerGroupID
    servers_deleted = 0
    servers_ignored = 0

    # How many days should a server be offline before being deleted?
    deactivate_days = deactivate_num_days

    # Get list of deactivated servers
    reply = get_deactivated_server_list()

    # Loop through deactivated servers list
    # and delete if move criteria met
    for server in reply.json()["servers"]:
        server_id = server['id']
        server_hostname = server['hostname']
        print server['hostname']
        # Create aware datetime object for last time seen
        lastseen = iso8601.parse_date(server['last_state_change'])

        # Create aware datetime object for current time
        utc = pytz.timezone('UTC')
        utcnow = datetime.datetime.utcnow()
        utcnow_aware = utc.fromutc(utcnow)

        # Calculate time diff in days
        # After 1 day, last_state_change rounds off to days
        time_diff = utcnow_aware - lastseen
        diff_days = int(time_diff.days)

        # Delete a server if in the desired deactivated server group and if
        # diff_days is greater than deactivate_days
        if (server['group_name'] == deleteServerGroupName) and (diff_days > deactivate_days) and server_id:
            print "Deleting server %s." % server_hostname
            data  = delete_server(server['id'])
            if data:
                print "Server %s deleted successfully." % server_hostname
                servers_deleted += 1
        else:
            print "Unable to delete server."
            if not server_id:
                print "Server: %s (id %s) does not exist.\n" % (server_hostname, server_id)
            elif diff_days <= deactivate_days:
                print "Server %s not deleted, deactivated only for %s days.\n" % (server_hostname, diff_days)
                servers_ignored += 1

    #Print summary of script actions
    print "\n****** Script Summary API Key #%d ******" % api_key_loop_counter
    if (api_key_description):
        print "API Key Descritpion: %s" % api_key_description
    print "Servers deleted: %d" % servers_deleted
    print "Servers ignored, less than specified days deactivated: %d " % servers_ignored
    current_date_time = datetime.datetime.utcnow()
    print "Script completed: %s UTC" % current_date_time
    print "***************************************"
###############################################################################
# end of function definitions, begin inline code

#---MAIN---------------------------------------------------------------------
# Reads in api_keys.txt file and loops through all available Keys
# and runs get_headers and move_deactivated_servers for each provided
# base64 keypair

if os.path.isfile(PATH) and os.access(PATH, os.R_OK):
    print "api_keys.txt file exists and is readable"
    global api_key_description
    with open('api_keys.txt') as f:
        content = f.readlines()
        f.close()
        for apiKey in content:
            #print apiKey
            user_credential_b64 = "Basic " + base64.b64encode(apiKey[:41])
            api_key_description = apiKey[42:]
            #print user_credential_b64
            api_key_loop_counter += 1
            headers=get_headers()
            delete_deactivated_servers()
else:
    print "api_keys.txt file either file is missing or is not readable"
