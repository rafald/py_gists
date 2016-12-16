#!/usr/bin/env python3

import time
import threading
import os
import subprocess
import sys
import queue # multiprocessing.Queue
import pyperclip

def qualify_url(url):
    if url.startswith("http") :
        return True
    return False

def download(clipboard_content, failed):
   url = str(clipboard_content) # typecast ?
   if lenght(url) == 11 :
      url = "https://www.youtube.com/watch?v=".join(url)

   print ("Launching youtube-dl to download %s" % (url) )
   with open(os.devnull, "w") as fnull:
      completed_process = subprocess.run(["youtube-dl", "--proxy=127.0.0.1:8123", "-t", "--restrict-filenames", "-c", url], stdout = fnull, stderr = fnull) # 
      if completed_process.returncode != 0 :
         print("FAILED: {}, error code: {}".format(url, completed_process))
         failed.put(clipboard_content) 
      else : print ("FINISHED: %s" % (url) )
    
def main():
   try:
      history = set()
      failed = queue.Queue() # Worker Thread => Main Thread communication channel
      clp_recent_value = ""
      pause = 1
      url_predicate = qualify_url
      while True :
         while not failed.empty():
            history.remove(failed.get())
         tmp_value = pyperclip.paste()
         if tmp_value != clp_recent_value:
             #print("new value in clippboard: ", tmp_value)
             clp_recent_value = tmp_value
             if url_predicate(clp_recent_value) :
                if clp_recent_value not in history :
                   history.add(clp_recent_value)
                   new_download = threading.Thread(target=lambda : download(clp_recent_value, failed))
                   new_download.start()
                   print("download thread started: %s %s" % (new_download.ident, new_download.name) )
                else : print("this url is already present in history: %s" % (clp_recent_value) )
         time.sleep(pause)
   except KeyboardInterrupt:
      for th in threading.enumerate():
         if th != threading.current_thread():
            print( "joining %s, %s thread" % (th.ident, th.name) )
            th.join()

if __name__ == "__main__":
    main()

# TODO save restore database of downloaded links - ??? serialize dict ?
