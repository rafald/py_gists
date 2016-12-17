#!/usr/bin/env python3

import time
import threading
import os
import subprocess
import sys
import queue # multiprocessing.Queue
import json

import pyperclip
import pickle

def qualify_url(url):
    if url.startswith("http") :
        return True
    return False

def Destination(dump):
   return [l for l in dump.split('\n') if l.startswith("[download] Destination:")]
   
def download(url, failed):
   print ("Launching youtube-dl to download %s" % (url) )
   cmd = ["youtube-dl", "-t", "--restrict-filenames", "-c", url]
   if "https_proxy" in os.environ :
      cmd.append("--proxy={}".format(os.environ['https_proxy']))
   completed = subprocess.run(cmd, stdout=subprocess.PIPE, universal_newlines=True) 
   if completed.returncode != 0:
      failed.put(url)
      print ("FAILED!: %s" % (completed))
   else : print ("FINISHED: {}".format(Destination(completed.stdout)) )

def fix_history(failed, history, history_failed):
   while not failed.empty():
      url = failed.get()
      history.remove(url)
      history_failed.add(url)

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

HISTORY_FILE = 'history.json' # with open(history_file, 'wb') as f:
HISTORY_FAILED_FILE = 'history_failed.json'
HR_OPTS = dict(sort_keys=True, indent=4, default=idefault)

def save(history, history_failed):
   with open(HISTORY_FILE, 'w') as hf:
       # Pickle the 'data' dictionary using the highest protocol available.
       #pickle.dump(history, f, pickle.HIGHEST_PROTOCOL)
       json.dump(history, hf, **HR_OPTS)
   with open(HISTORY_FAILED_FILE, 'w') as hff:
       # Pickle the 'data' dictionary using the highest protocol available.
       #pickle.dump(history_failed, f, pickle.HIGHEST_PROTOCOL)
       json.dump(history_failed, hff, **HR_OPTS)

def try_load(history, history_failed):
   if os.path.isfile(HISTORY_FILE) :
      with open(HISTORY_FILE, 'r') as f:
          # The protocol version used is detected automatically, so we do not
          # have to specify it.
          #history = pickle.load(f)
          history = set(json.load(f))
   else : print("Missing history file {} (OK if this is the 1st run)".format(HISTORY_FILE,))
   if os.path.isfile(HISTORY_FAILED_FILE) :
      with open(HISTORY_FAILED_FILE, 'r') as f:
         #history_failed = pickle.load(f)
         history_failed = set(json.load(f))
         #outfile = options.outfile or sys.stdout
         json.dump(HISTORY_FAILED_FILE, sys.stdout, **HR_OPTS)
         sys.stdout.write('\n')
         
WATCH_IDLE_PERIOD = 1
          
def main():
   try:
      # TODO merge to DS with .add .failed .retry
      history = set()
      history_failed = set()
      
      try_load(history, history_failed)
              
      failed = queue.Queue() # communication channel: Worker Thread => Main Thread 
      clp_recent_value = ""
      while True :
         fix_history(failed, history, history_failed)
         tmp_value = str(pyperclip.paste())
         if tmp_value != clp_recent_value:
             clp_recent_value = tmp_value 
             if qualify_url(clp_recent_value) or len(clp_recent_value) == 11 : # clp_recent_value = "https://www.youtube.com/watch?v=".join(clp_recent_value)
                if clp_recent_value not in history :
                   history.add(clp_recent_value)
                   history_failed.discard(clp_recent_value)
                   new_download = threading.Thread(target=lambda : download(clp_recent_value, failed))
                   new_download.start()
                   print("download thread started: %s %s" % (new_download.ident, new_download.name) )
                else : print("this url is already present in history: %s - request ignored" % (clp_recent_value) )
         time.sleep(WATCH_IDLE_PERIOD)
   except KeyboardInterrupt:
      for th in threading.enumerate():
         if th != threading.current_thread():
            print( "joining %s, %s thread" % (th.ident, th.name) )
            th.join()
      fix_history(failed, history, history_failed)
      
   save(history, history_failed)    
   print('Gracefully quitting')

if __name__ == "__main__":
    main()

# TODO save restore database of downloaded links - ??? serialize dict ?
# store failed jobs - retry after restart
