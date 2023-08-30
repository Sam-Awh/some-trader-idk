import time
import os
from client.streamscript.run_streams import Streams
from trader import PyreTrader
import multiprocessing
from colorama import init as colorama_init
from colorama import Fore
from colorama import Style
# import imp
# import ctypes
# import _thread
# import win32api

colorama_init()

# # --------------------------------------------
# # Just something i copypasted off of stackoverflow to
# # patch the stupid fortran error.
# basepath = imp.find_module('numpy')[1]
# ctypes.CDLL(os.path.join(basepath, 'core', 'libmmd.dll'))
# ctypes.CDLL(os.path.join(basepath, 'core', 'libifcoremd.dll'))

# # Now set our handler for CTRL_C_EVENT. Other control event 
# # types will chain to the next handler.
# def handler(dwCtrlType, hook_sigint=thread.interrupt_main):
#     if dwCtrlType == 0: # CTRL_C_EVENT
#         hook_sigint()
#         return 1 # don't chain to the next handler
#     return 0 # chain to the next handler

# win32api.SetConsoleCtrlHandler(handler, 1)
# # --------------------------------------------
# pls ignore this i tried fixing the stoobid fortran error but im too dumb for that.

if __name__ == "__main__":
    trigger = True
    try:
        while trigger == True:
            data_stream_process = multiprocessing.Process(target=Streams().run)
            trader_process = multiprocessing.Process(target=PyreTrader.run_trader)

            data_stream_process.start()
            time.sleep(1)
            trader_process.start()

            data_stream_process.join()
            trader_process.join()
            time.sleep(600) # delay per trade.

    except KeyboardInterrupt:
        print(f"{Fore.LIGHTRED_EX}Stopping datastream...{Style.RESET_ALL}")
        trigger = False
        file_path = "client/streamscript/streams/STREAM_ethusdt.csv"
        os.remove(file_path)
        time.sleep(2)
        print(f"{Fore.LIGHTRED_EX}Shutting down...{Style.RESET_ALL}")
        time.sleep(2)
        exit()
    except Exception as e:
        print(f"{Fore.LIGHTRED_EX}Exception in the main process.{Style.RESET_ALL}")
        print(e)

# ~ sam cooked this to fix threading issues by centralizing all function calls.
