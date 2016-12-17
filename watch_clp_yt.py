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
       
def main():
   try:
      hr_opts = dict(sort_keys=True, indent=4, default=idefault)
      
      history = set()
      history_failed = set()
      history_file = 'history.json' # with open(history_file, 'wb') as f:
      history_failed_file = 'history_failed.json'
      if os.path.isfile(history_file) :
         with open(history_file, 'r') as f:
             # The protocol version used is detected automatically, so we do not
             # have to specify it.
             #history = pickle.load(f)
             history = set(json.load(f))
      if os.path.isfile(history_failed_file) :
         with open(history_failed_file, 'r') as f:
            #history_failed = pickle.load(f)
            history_failed = set(json.load(f))
            #outfile = options.outfile or sys.stdout
            json.dump(history_failed, sys.stdout, **hr_opts)
            sys.stdout.write('\n')
             
      else : print("Missing history file {} (OK if this is the 1st run)".format(history_file))
              
      failed = queue.Queue() # Worker Thread => Main Thread communication channel
      clp_recent_value = ""
      pause = 1
      url_predicate = qualify_url
      while True :
         fix_history(failed, history, history_failed)
         tmp_value = str(pyperclip.paste())
         if tmp_value != clp_recent_value:
             #print("new value in clippboard: ", tmp_value)
             clp_recent_value = tmp_value # http://www.pornhub.com/view_video.php?viewkey=ph5703ff3a2c289
             if url_predicate(clp_recent_value) or len(clp_recent_value) == 11 : # clp_recent_value = "https://www.youtube.com/watch?v=".join(clp_recent_value)
                if clp_recent_value not in history :
                   history.add(clp_recent_value)
                   history_failed.discard(clp_recent_value)
                   new_download = threading.Thread(target=lambda : download(clp_recent_value, failed))
                   new_download.start()
                   print("download thread started: %s %s" % (new_download.ident, new_download.name) )
                else : print("this url is already present in history: %s - request ignored" % (clp_recent_value) )
         time.sleep(pause)
   except KeyboardInterrupt:
      for th in threading.enumerate():
         if th != threading.current_thread():
            print( "joining %s, %s thread" % (th.ident, th.name) )
            th.join()
      fix_history(failed, history, history_failed)
            
   with open(history_file, 'w') as hf:
       # Pickle the 'data' dictionary using the highest protocol available.
       #pickle.dump(history, f, pickle.HIGHEST_PROTOCOL)
       json.dump(history, hf, **hr_opts)
   with open(history_failed_file, 'w') as hff:
       # Pickle the 'data' dictionary using the highest protocol available.
       #pickle.dump(history_failed, f, pickle.HIGHEST_PROTOCOL)
       json.dump(history_failed, hff, **hr_opts)
       
   print('Gracefully quitting')

if __name__ == "__main__":
    main()

# TODO save restore database of downloaded links - ??? serialize dict ?
# store failed jobs - retry after restart
