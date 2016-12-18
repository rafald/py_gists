#!/usr/bin/env python3

import time
import threading
import os
import subprocess
import sys
import queue # multiprocessing.Queue
import json
from collections import defaultdict
import time
import shutil

import pyperclip
import pickle

def qualify_url(url):
    if url.startswith("http") :
        return True
    return False

def Destination(dump):
   PFX = "[download] Destination: "
   PFX_LEN = len(PFX)
   return [l[PFX_LEN:] for l in dump.split('\n') if l.startswith(PFX)]
   
def download(url, failed, history_names):
   msg = "Launching youtube-dl to download %s,%s" % (url, history_names[url] if url in history_names else None)
   print(msg)
   subprocess.run(['notify-send', '-u', 'critical', msg]) # call is nonblocking
   
   cmd = ["youtube-dl", "-t", "--restrict-filenames", "-c", url]
   if "https_proxy" in os.environ :
      cmd.append("--proxy={}".format(os.environ['https_proxy']))
   completed = subprocess.run(cmd, stdout=subprocess.PIPE, universal_newlines=True) 
   
   th_name = threading.current_thread().name
   if completed.returncode != 0:
      failed.put((url,completed.stdout))
      print ("FAILED %s! : %s" % (th_name, completed))
   else : 
      print ("FINISHED {}: {}".format(th_name, Destination(completed.stdout)) )
      history_names[url] = Destination(completed.stdout) # TODO unsafe - pass back lamdba to failed queue not a value

def fix_history(failed, history, history_failed, history_names):
   while not failed.empty():
      url,log = failed.get()
      del history[url]
      history_failed[url]=time.time()
      history_names[url]=Destination(log)

def sdefault(o):
    if isinstance(o, set):
        return list(o)
    return o.__dict__

def idefault(o):
   try:
       iterable = iter(o)
   except TypeError:
       o.__dict__
   else:
       return list(iterable)

def backup(backup_directory, *files):
   if not os.path.exists(backup_directory):
       os.makedirs(backup_directory)
   seq_no = time.time() % 21 # quasi random [0,21]
   for f in files:
      shutil.move( f, os.path.join(backup_directory,"%d_%s" % (seq_no, f)))
   
HISTORY_FILE = 'history.json' # with open(history_file, 'wb') as f:
HISTORY_FAILED_FILE = 'history_failed.json'
HISTORY_NAMES_FILE = 'history_names.json'
HR_OPTS = dict(sort_keys=True, indent=4, default=idefault)

def save(history, history_failed, history_names):
   backup("backup", HISTORY_FILE, HISTORY_FAILED_FILE, HISTORY_NAMES_FILE)
   with open(HISTORY_FILE, 'w') as hf:
       # Pickle the 'data' dictionary using the highest protocol available.
       #pickle.dump(history, f, pickle.HIGHEST_PROTOCOL)
       json.dump(history, hf, **HR_OPTS)
   with open(HISTORY_FAILED_FILE, 'w') as hff:
       #pickle.dump(history_failed, f, pickle.HIGHEST_PROTOCOL)
       json.dump(history_failed, hff, **HR_OPTS)
   with open(HISTORY_NAMES_FILE, 'w') as hnf:
       #pickle.dump(history_failed, f, pickle.HIGHEST_PROTOCOL)
       json.dump(history_names, hnf, **HR_OPTS)

def try_load():
   history = defaultdict(time.time)
   history_failed = defaultdict(time.time)
   history_names = defaultdict(list)
   
   if os.path.isfile(HISTORY_FILE) :
      with open(HISTORY_FILE, 'r') as f:
          # The protocol version used is detected automatically, so we do not
          # have to specify it.
          #history = pickle.load(f)
          history = json.load(f) #history = set(json.load(f))
   else : print("Missing history file {} (OK if this is the 1st run)".format(HISTORY_FILE,))
   if os.path.isfile(HISTORY_FAILED_FILE) :
      with open(HISTORY_FAILED_FILE, 'r') as f:
         print("loading HISTORY_FAILED_FILE")
         #history_failed = pickle.load(f)
         history_failed = json.load(f)
   if os.path.isfile(HISTORY_NAMES_FILE) :
      with open(HISTORY_NAMES_FILE, 'r') as f:
         print("loading HISTORY_NAMES_FILE")
         #history_names = pickle.load(f)
         history_names = json.load(f) 
   return (history, history_failed, history_names)
         
WATCH_IDLE_PERIOD = 1
          
def main():
   try:
      # TODO merge (history, history_failed) to DS with .add .failed .retry
      # can also sync with json repr on hd
      history, history_failed, history_names = try_load()
      import operator
      
      if len(sys.argv)>1 and sys.argv[1] == "history":
         for url, t in sorted(history.items(), key=operator.itemgetter(1) ): # list of tuples
            print(url, time.ctime(t), history_names[url] if url in history_names else None)
         exit(0)
      
      for v, k in sorted(history_failed.items(), key=operator.itemgetter(1) ): # list of tuples
         print(v, time.ctime(k), history_names[v] if v in history_names else None)
              
      failed = queue.Queue() # communication channel: Worker Thread => Main Thread 
      clp_recent_value = ""
      while True :
         fix_history(failed, history, history_failed, history_names)
         tmp_value = str(pyperclip.paste())
         if tmp_value != clp_recent_value:
             clp_recent_value = tmp_value 
             if qualify_url(clp_recent_value) or len(clp_recent_value) == 11 : # clp_recent_value = "https://www.youtube.com/watch?v=".join(clp_recent_value)
                if clp_recent_value not in history :
                   history[clp_recent_value]=time.time()
                   history_failed.pop(clp_recent_value, None) # discard
                   new_download = threading.Thread(target=lambda : download(clp_recent_value, failed, history_names))
                   new_download.start()
                   print("download thread started: %s" % (new_download.name) )
                else : print("this url is already present in history: %s - request ignored" % (clp_recent_value) )
         time.sleep(WATCH_IDLE_PERIOD)
   except KeyboardInterrupt:
      for th in threading.enumerate():
         if th != threading.current_thread():
            print( "joining %s, %s thread" % (th.ident, th.name) )
            th.join()
      fix_history(failed, history, history_failed, history_names)

   save(history, history_failed, history_names)
   print('Gracefully quitting')

if __name__ == "__main__":
    main()

# TODO save restore database of downloaded links - ??? serialize dict ?
# store failed jobs - retry after restart
