#!/usr/bin/python

''' 
Block if User-Agent requests are too high in X seconds
''' 

import time
import os
import sys
import argparse
import re
from datetime import datetime
from pathlib import Path

debug = None
ua_count = {}   # count
ua_time = {}    # time

def log(message,level="INFO"):
    if (level == 'DEBUG' and debug is True) or (level!='DEBUG'):
        ymd = datetime.today().strftime('%Y-%m-%d')
        hms = datetime.today().strftime('%H:%M:%S')
        print("%s | %s | %s | %s" % (ymd, hms, level, message) )

def block(ua):
    ua_safe = ua.replace('/','\/').replace('(','\(').replace(')','\)') 
    out = '# %s\n' % (datetime.today().strftime('%Y-%m-%d %H:%M:%S'))
    out = out + 'if (req.http.User-Agent ~ "%s") { error 429 "Calm down."; }\n\n' % ua_safe

    with open(args.output) as f:
        if ua_safe in f.read():
            log("UA already exists in %s, ua: %s" % (args.output, ua_safe), 'WARNING')
        else:
            log("BLOCK: %s" % ua_safe)

            f = open(args.output, "a+")
            f.write(out)
            f.close()

def follow(thefile):
    thefile.seek(0, os.SEEK_END)
    while True:
        line = thefile.readline()        # sleep if file hasn't been updated
        if not line:
            time.sleep(0.1)
            continue

        yield line.rstrip()

def get_ua(line):
    found = None
    m = re.search('\d+ \d+ "(.+?)" "(.+?)"', line)
    if m:
        try:
            found = m.group(2)    
        except:
            found = None
    return found


if __name__ == '__main__':
    args = argparse.ArgumentParser    
    parser = argparse.ArgumentParser(description='Follow log file and block excessive User-Agent in specified time')
    parser.add_argument('log_file', help='LOG file')
    parser.add_argument('--allowed', metavar='req', type=int, default=20, help='allowed count one User-Agent (default 20 requests)', required=False)
    parser.add_argument('--period', metavar='sec', type=int, default=10, help='block if requests occurs in given period (default 10 seconds)', required=False)
    parser.add_argument('--output', metavar='file', default='/tmp/blocked-ua.vcl', help='output file contains detected blocked user agents (default /tmp/blocked-ua.vcl)')
    parser.add_argument('-v', action='store_true', help='verbose mode', required=False)
    args = parser.parse_args()
    debug = args.v

    try:
        logfile = open(args.log_file,"r")
    except Exception as e:
        log(e, 'ERROR')
        sys.exit(1)

    # touch output file
    f = Path(args.output)
    f.touch(exist_ok=True)

    # tailf log file and search User-Agent
    loglines = follow(logfile)
    for line in loglines:
        ua = get_ua(line)
        if ua in ua_count:

            if ua_count[ua] % args.allowed == 0:
                diff_time = int(time.time() - ua_time[ua])

                if diff_time < args.period :
                    block(ua)
                else:
                    log("ALLOW ua=%s, diff_time=%s" % (ua, diff_time),'DEBUG')
                
                # reset timer
                ua_time[ua] = time.time()
                ua_count[ua] = 1

            # increase counter
            ua_count[ua] = ua_count[ua] + 1


        else:
            if ua is not None:
                ua_count[ua] = 1
                ua_time[ua] = time.time()   # start


