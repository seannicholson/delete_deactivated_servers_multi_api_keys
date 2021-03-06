# delete_deactivated_servers_multi_api_keys

This Python script will delete deactivated servers contained in the
specified Halo Group in the scope of the API Key specified based on
number of days the server has been in a deactivated state.

This will help cloud forward customers with highly elastic environments
keep their active server groups clean. Also this will allow for the issues
per group reports to contain information for only active or recently
deactivated servers and prevent reporting on systems that are no longer
online or active.

This script was made to work in tandem with
move_deactivated_servers_multi_api_keys
https://github.com/seannicholson/move_deactivated_servers_multiple_api_keys

IMPORTANT:
This script was built for Python 2.7.11 or later and requires an OpenSSL
version compatible with TLS1.2 or newer
Check python OpenSSL version

  >python
  then run "import ssl"
  then run "ssl.OPENSSL_VERSION"

Should show something similar to:
'OpenSSL 1.0.2g  1 Mar 2016'


Python Module Prerequisites:
This script requires the following Python modules:
json, base64, datetime, sys, argparse, pytz, requests, iso8601
Use PIP to install these if you are encountering errors for missing modules
for pytz, requests, iso8601, os, os.path
> pip install requests, pytz, iso8601

The script takes advantage of the new server field last_state_change and
is intended to be run from cron on a restricted-access tools server or
bastion box once daily.  Since last_state_change is only expressed in whole
days after a server has been offline for more than 24 hours, there is little
advantage to running it more often.

You will need a config.py file that includes the deactivated server group name
specified. -- see the sample file.

In the config.py is a api_key_path variable that specifies the location of
your api_keys.txt file, if the file is not stored with this script (the
default setting already configured), you will need to enter the full path
to the file in the config.py file.

You will need to create a file named api_keys.txt that contains your API Key ID
and API Key Secret using this format
> apikeyID:apikeySecret

You can specify a API Key descriptor by putting a space after the API Key and a
string descriptor using the following format
> apikeyID:apikeySecret api_key_description_string

The keypair must have full access (read-write), and as always, you will want to
protect the security of this file.

By default, servers that have been deactivated for more than 7 days and are
in the specified group will be deleted by the script. To change this, modify
the value of deactivate_num_days in the config.py file.
