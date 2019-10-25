#!/usr/bin/env python3

import sys

if sys.version_info < (3,0):
    print('ERROR: UhOh365 runs on Python 3.  Run as "./UhOh365.py" or "python3 UhOh365.py" !')
    sys.exit(1)

import argparse
import queue
import random
import string
import threading
import time
import requests


email_queue = queue.Queue()
print_queue = queue.Queue()
args = None
domain_is_o365 = {}
domain_is_o365_lock = threading.Lock()
ssl_verify = False

def parse_args():
    parser = argparse.ArgumentParser(description="This script uses the autodiscover json API of office365 to enumerate valid o365 email accounts. This does not require any login attempts unlike other enumeration methods and therefore is very stealthy.")
    parser.add_argument("file", type=argparse.FileType('r'), help="Input file containing one email per line")
    parser.add_argument("-v", "--verbose", help="Display each result as valid/invalid. By default only displays valid", action="store_true")
    parser.add_argument("-t", "--threads", help="Number of threads to run with. Default is 20", type=int, default=20)
    parser.add_argument("-o", "--output", help="Output file for valid emails only", type=argparse.FileType('w'))

    return parser.parse_args()

def thread_worker(args):
    user_agent = 'Microsoft Office/16.0 (Windows NT 10.0; Microsoft Outlook 16.0.12026; Pro)'
    headers = {'User-Agent': user_agent, 'Accept': 'application/json'}
    while not email_queue.empty():
        try:
            email = email_queue.get()
            domain = email.split("@")[1]
            if domain not in domain_is_o365.keys():
                with domain_is_o365_lock:
                    if domain not in domain_is_o365.keys():
                        junk_user = ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(20))
                        r = requests.get('https://outlook.office365.com/autodiscover/autodiscover.json/v1.0/{}@{}?Protocol=Autodiscoverv1'.format(junk_user, domain), headers=headers, verify=ssl_verify, allow_redirects=False)
                        if 'outlook.office365.com' in r.text:
                            domain_is_o365[domain] = True
                        else:
                            if args.verbose:
                                print("It doesn't look like '{}' uses o365".format(domain))
                            domain_is_o365[domain] = False
            r = requests.get('https://outlook.office365.com/autodiscover/autodiscover.json/v1.0/{}?Protocol=Autodiscoverv1'.format(email), headers=headers, verify=ssl_verify, allow_redirects=False)
            if r.status_code == 200:
                print("VALID: ", email)
                if args.output is not None:
                    print_queue.put(email)
            elif r.status_code == 302:
                if domain_is_o365[domain] and 'outlook.office365.com' not in r.text:
                    print("VALID: ", email)
                    if args.output is not None:
                        print_queue.put(email)
            else:
                if args.verbose:
                    print("INVALID: ", email)
        except Exception as e:
            print("ERROR: ", e)

def print_worker(args):
    if args.output is not None:
        while True:
            toPrint = print_queue.get()
            if toPrint == 'done':
                return
            args.output.write(toPrint + "\n")


def main():
    print("-----------------------------------------------------------")
    print("|                 UhOh365 Email Validation                 |")
    print("|                                                          |")
    print("|                      By Chris King                       |")
    print("|                        @raikiasec                        |")
    print("-----------------------------------------------------------")
    requests.packages.urllib3.disable_warnings()
    args = parse_args()
    with args.file as emailFile:
        for line in emailFile:
            if '@' in line:
                email_queue.put(line.strip())

    threads = []
    start = time.perf_counter()
    for i in range(args.threads):
        t = threading.Thread(target=thread_worker, args=(args,))
        t.daemon = True
        t.start()
        threads.append(t)

    print_thread = threading.Thread(target=print_worker, args=(args,))
    print_thread.daemon = True
    print_thread.start()

    for t in threads:
        t.join()
    print_queue.put('done')

    print_thread.join()

    print("Done!  Total execution time: ", time.perf_counter() - start, " seconds")

if __name__ == "__main__":
    main()
