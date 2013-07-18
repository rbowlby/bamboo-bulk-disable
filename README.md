bamboo-bulk-disable
===================

Disable bamboo builds in bulk based on last build date.

Examples:  
 
Disable all builds that haven't completed in more than 90 days:

	bamboo-bulk-disable.py --host localhost --port 3306 --user bamboo_admin --password password --database bamboo --age 90

List and do not disable builds more than 90 days without a build:

	bamboo-bulk-disable.py -H localhost -P 3306 -u bamboo_admin -p password -d bamboo -a 90 --list
