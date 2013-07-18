#!/usr/bin/env python
'''
Disables Bamboo plans that have not been "built" in N days. Verified to work on
4.4.5.
'''

import sys
import MySQLdb
import argparse


# display help on arg error
class DefaultHelpParser(argparse.ArgumentParser):
  def error(self, message):
    sys.stderr.write('error: %s\n' % message)
    self.print_help()
    sys.exit(2)

def get_args():

    desc = '''
    Disables Bamboo plans that have not been "built" in N days.
    '''

    example = '''
    Examples:

        bamboo_disabler.py --host localhost --port 3306 --user bamboo_admin --password password --database bamboo --age 30
        bamboo_disabler.py -H localhost -P 3306 -u bamboo_admin -p password -d bamboo -a 30
        bamboo_disabler.py -u bamboo_admin -d bamboo -a 30
        '''

    parser = DefaultHelpParser( description = desc, epilog = example,
        formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument('-H', '--host',
                        dest    = 'host',
                        default = 'localhost',
                        metavar = '',
                        help    = 'Hostname of bamboo mysql server')
    parser.add_argument('-P', '--port',
                        dest = 'port',
                        default = 3306,
                        metavar = '',
                        help = 'mysql port number (default: 3306)')
    parser.add_argument('-u', '--user',
                        dest    = 'user',
                        required = True,
                        metavar = '',
                        help    = 'Authorized mysql user for bamboo database (required).')
    parser.add_argument('-p', '--password',
                        dest    = 'password',
                        default = None,
                        metavar = '',
                        help    = 'Password to authenticate using (omit to be prompted)')
    parser.add_argument('-d', '--database',
                        dest    = 'database',
                        default = 'bamboo',
                        metavar = '',
                        help    = 'mysql bamboo database name (default: bamboo)')
    parser.add_argument('-a', '--age',
                        dest    = 'age',
                        required = True,
                        type = int,
                        metavar = '',
                        help    = 'Disable plans more than N days (age) since last run.')
    parser.add_argument('-l', '--list',
                        action = 'store_true',
                        help    = 'List only, does not disable results.')


    args = parser.parse_args()
    return args

if __name__ == '__main__':
    args = get_args()

    con = MySQLdb.connect(args.host, args.user, args.password, args.database)

    with con:
        cursor = con.cursor()

        # null means never ran? ignoring those to be safe
        query = ''' SELECT DATEDIFF( NOW(), r.BUILD_COMPLETED_DATE) AS 'AGE', r.BUILD_KEY FROM BUILDRESULTSUMMARY r
        inner join BUILD b on r.BUILD_KEY = b.FULL_KEY and b.SUSPENDED_FROM_BUILDING = False
        WHERE r.BUILD_COMPLETED_DATE IS NOT NULL '''

        cursor.execute(query)

        build_age = {}

        # dict with age of most recent build
        for age, build_key in cursor:
            last_age = build_age.get(build_key)
            if not last_age or last_age > age:
                build_age[build_key] = age

        disable_query = "UPDATE BUILD SET SUSPENDED_FROM_BUILDING=true WHERE FULL_KEY = '{}'"
        for build_key, age in build_age.iteritems():
            if age > args.age:
                if args.list:
                    print("Build: {}, Age: {}".format(build_key, age))
                else:
                    cursor.execute(disable_query.format(build_key))
                    print("Build: {}, Age: {} has been disabled.".format(build_key, age))


