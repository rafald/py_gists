#!/usr/bin/env python3

import time
import threading
import os
import subprocess
import sys
import queue # multiprocessing.Queue
import json
from collections import defaultdict
import shutil

import signal
import pyperclip
#import pickle
import operator

def cprint(*args):
   print("[{}]".format(threading.current_thread().name), *args)
########################################################################
def _qualify_url(url):
   if url.startswith("http") :
      return True
   return False

def _download(url, url_name, feedback):
   msg = "Launching youtube-dl to download %s | %s" % (url, "<name not yet discovered>" if url_name is None else url_name)
   cprint(msg)
   subprocess.run(['notify-send', '-u', 'critical', msg]) # call is nonblocking
   
   cmd = ["youtube-dl", "-t", "--restrict-filenames", "-c", url]
   if "https_proxy" in os.environ :
      cmd.append("--proxy={}".format(os.environ['https_proxy']))
   completed = subprocess.run(cmd, stdout=subprocess.PIPE, universal_newlines=True) 
   feedback.put( (url,completed) ) # now main thread processes concurently, can display before next cprintf()
   
   th_name = threading.current_thread().name
   if completed.returncode != 0:
      cprint ("FAILED %s! : %s" % (th_name, completed))
   else : 
      cprint ("{} finished".format(th_name) )
def _yt_preprocess(clp_recent_value):
   if len(clp_recent_value) == 11: 
      clp_recent_value = "https://www.youtube.com/watch?v=" + clp_recent_value
   return clp_recent_value

# INTERFACE
class YTDownloader:
   def DestinationNames(self, log):
      PFX = "[download] Destination: "
      PFX_LEN = len(PFX)
      return [l[PFX_LEN:] for l in log.split('\n') if l.startswith(PFX)]
      
   def probe_processing(self, maybe_url, history, history_failed, history_names, feedback):
      maybe_url = _yt_preprocess(maybe_url)
      if maybe_url not in history :
         history_failed.pop(maybe_url, None) # discard
         if _qualify_url(maybe_url):
            history[maybe_url]=time.time()
            new_download = threading.Thread(target=lambda : _download(maybe_url, 
               history_names[maybe_url] if maybe_url in history_names else None, 
               feedback))
            new_download.start()
            cprint("download thread started: %s" % (new_download.name) )
      else : cprint("this TASK_STRING is already present in processing history: %s - request ignored" % (maybe_url) )
########################################################################
      
def fix_history(proc, feedback, history, history_failed, history_names):
   update = False
   while not feedback.empty():
      url, completed = feedback.get() 
      dest_names = proc.DestinationNames(completed.stdout)
      if len(dest_names) :
         history_names[url] = dest_names
      else: cprint("WARN: Could not parse: {}".format(completed.stdout))
      if completed.returncode != 0:
         history_failed[url] = history[url]
         del history[url]
      else:
         cprint ("FINISHED with {} {}".format(history_names.get(url), url) )
      update = True
   worker_active_count = threading.active_count() - 1 # exclude main thread
   if update:
      if worker_active_count:
         cprint( "[%d] Running %d worker thread(s)" % (os.getpid(), worker_active_count) )
      else:
         cprint( "[%d] No worker threads (IDLE)" % (os.getpid()))
      

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
   else : cprint("Missing history file {} (OK if this is the 1st run)".format(HISTORY_FILE,))
   if os.path.isfile(HISTORY_FAILED_FILE) :
      with open(HISTORY_FAILED_FILE, 'r') as f:
         cprint("loading HISTORY_FAILED_FILE")
         #history_failed = pickle.load(f)
         history_failed = json.load(f)
   if os.path.isfile(HISTORY_NAMES_FILE) :
      with open(HISTORY_NAMES_FILE, 'r') as f:
         cprint("loading HISTORY_NAMES_FILE")
         #history_names = pickle.load(f)
         history_names = json.load(f) 
   return (history, history_failed, history_names)

WATCH_IDLE_PERIOD = 1
def main():
   proc = YTDownloader()
   try:
      # TODO merge (history, history_failed) to DS with .add .failed .retry
      # can also sync with json repr on hd
      history, history_failed, history_names = try_load()
      signal.signal( signal.SIGHUP, lambda sig, frm: save(history, history_failed, history_names) )
      
      if len(sys.argv)>1 :
         if sys.argv[1].startswith("hi"):
            for url, t in sorted(history.items(), key=operator.itemgetter(1) ): # list of tuples
               cprint(url, time.ctime(t), history_names[url] if url in history_names else None)
            exit(0)
         elif sys.argv[1].startswith("cl"):
            for k in list(history_failed.keys()):
               if history_names.get(k) is None:
                  cprint("removing {}".format(k))
                  del history_failed[k]
      cprint( "pid is {}".format(os.getpid()) )
      
      for v, k in sorted(history_failed.items(), key=operator.itemgetter(1) ): # list of tuples
         cprint(v, time.ctime(k), history_names[v] if v in history_names else None)
              
      feedback = queue.Queue() # communication channel: Worker Thread => Main Thread 
      clp_recent_value = None
      while True :
         fix_history(proc,feedback, history, history_failed, history_names)
         tmp_value = str(pyperclip.paste()) # not tmp_value is None 
         if tmp_value != clp_recent_value:
            clp_recent_value = tmp_value 
            #TODO factory_from_string but then fix_history must receive specific correct object 
            proc.probe_processing(clp_recent_value, history, history_failed, history_names, feedback)
         time.sleep(WATCH_IDLE_PERIOD)
   except KeyboardInterrupt:
      for th in threading.enumerate():
         if th != threading.current_thread():
            cprint( "joining %s, %s thread" % (th.ident, th.name) )
            th.join()
      fix_history(proc,feedback, history, history_failed, history_names)

   save(history, history_failed, history_names)
   cprint('Gracefully quitting')

if __name__ == "__main__":
    main()
