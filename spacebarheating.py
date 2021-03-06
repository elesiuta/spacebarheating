#!/usr/bin/env python3
# spacebarheating inspired by https://xkcd.com/1172/
# never thought I'd have an actual use case for this, but here I am
# fixes the lcd on my laptop which displays vertical lines when the temperature is cold
# https://github.com/elesiuta/spacebarheating

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import importlib
import multiprocessing
import os
import signal
import subprocess
import sys
import threading
import time

import keyboard

PIDFILE = os.path.join(os.path.expanduser("~"), ".config", "spacebarheating.pid")
VERSION = "10.17.1"


def heater():
    """a very basic stress test"""
    signal.signal(signal.SIGTERM, lambda *args: sys.exit(0))
    while multiprocessing.parent_process().is_alive() and (os.name == "nt" or keyboard.is_pressed("space")):
        for i in range(1, 1000):
            _ = 1/i**0.5
    sys.exit(0)


def timed_heater(_):
    """a simpler heater, runs for 10 seconds then exits, no 'spacebar' required"""
    start_time = time.time()
    while time.time() < start_time + 10:
        for i in range(1, 1000):
            _ = 1/i**0.5


def heater_hook(key_event: keyboard.KeyboardEvent) -> None:
    """hook to start and cleanup heaters"""
    if key_event.event_type == keyboard.KEY_DOWN:
        # make sure key is held for 2.5 seconds before starting
        for i in range(5):
            time.sleep(0.5)
            if keyboard.is_pressed("space"):
                continue
            return
        # stress cpu
        processes: list[multiprocessing.Process] = []
        for i in range(multiprocessing.cpu_count()):
            processes.append(multiprocessing.Process(name="spacebarheater", target=heater, daemon=True))
            processes[-1].start()
        while keyboard.is_pressed("space"):
            time.sleep(0.1)
        # cleanup
        for process in processes:
            process.terminate()
            process.join()
            process.close()
    return


def start() -> int:
    """main function (registers hooks and waits)"""
    assert not os.path.exists(PIDFILE)
    os.makedirs(os.path.dirname(PIDFILE), exist_ok=True)
    with open(PIDFILE, "w") as f:
        f.write(str(os.getpid()) + "\n")
    forever = threading.Event()
    signal.signal(signal.SIGINT, lambda *args: forever.set())
    signal.signal(signal.SIGTERM, lambda *args: forever.set())
    keyboard.hook_key("space", heater_hook)
    forever.wait()
    keyboard.unhook_key("space")
    os.remove(PIDFILE)
    return 0


def stop() -> int:
    """terminate running instance and make sure pidfile was removed"""
    try:
        with open(PIDFILE, "r") as f:
            pid = int(f.read().strip())
        os.kill(pid, signal.SIGINT)
        time.sleep(0.1)
        os.kill(pid, signal.SIGTERM)
        time.sleep(0.1)
        os.kill(pid, signal.SIGKILL)
        assert not os.path.exists(PIDFILE)
        print("stopped spacebarheating")
    except FileNotFoundError:
        print(f"pidfile {PIDFILE} does not exist.\nspacebarheating is not currently running?", file=sys.stderr)
        return 1
    except ProcessLookupError:
        print(f"pidfile {PIDFILE} still exists but spacebarheating does not appear to be running, removing pidfile")
        os.remove(PIDFILE)
    except AssertionError:
        print(f"Error: pidfile {PIDFILE} still exists after attempting to stop process, process hanging or pid recycled?", file=sys.stderr)
        return 1
    except OSError:
        if os.name == "nt" and os.path.exists(PIDFILE):
            print("stopping spacebarheating...")
            os.remove(PIDFILE)
        else:
            print("I AM ERROR.", file=sys.stderr)
    return 0


def cli() -> int:
    """command line interface and initialization"""
    # help/usage message for any invalid flags
    if len(sys.argv) <= 1 or sys.argv[1] not in ["start", "stop", "restart", "once", "version"]:
        print("usage: spacebarheating start|stop|restart|once|version\n\n"
              "This software comes with ABSOLUTELY NO WARRANTY. This is free software, and\n"
              "you are welcome to redistribute it. See the MIT License for details.")
        return 2
    # run once for 10 seconds and exit (before testing keyboard hooks so root not required either)
    if sys.argv[1] == "once":
        with multiprocessing.Pool(processes=multiprocessing.cpu_count()) as pool:
            _ = pool.map(timed_heater, range(multiprocessing.cpu_count()))
        return 0
    # test keyboard hooks (needs root on linux)
    try:
        keyboard.hook_key("space", lambda x: None)
        keyboard.unhook_key("space")
    except Exception as e:
        print(type(e).__name__ + str(e.args), file=sys.stderr)
        if os.name == "posix" and os.getuid() != 0:
            print("Attempting to re-run spacebarheating as root, requesting root privileges")
            if importlib.util.find_spec("spacebarheating"):
                args = ["sudo", "-E", "python3", "-m", "spacebarheating", sys.argv[1]]
            else:
                args = ["sudo", "-E", sys.executable] + sys.argv
            os.execvp("sudo", args)
        else:
            print("Error: could not register keyboard hooks", file=sys.stderr)
            return 1
    # command line interface
    if sys.argv[1] == "restart":
        stop()
    if sys.argv[1] in ["start", "restart"]:
        if os.path.exists(PIDFILE):
            print(f"pidfile {PIDFILE} already exists.\nspacebarheating is currently running?", file=sys.stderr)
            return 1
    elif sys.argv[1] == "stop":
        return stop()
    else:
        print(VERSION)
        return 0
    # detach from terminal and start
    print("starting spacebarheating")
    if os.name == "posix":
        if os.isatty(0):
            if importlib.util.find_spec("spacebarheating"):
                args = ["bash", "-c", "sudo -E nohup python3 -m spacebarheating %s > /dev/null 2>&1 &" % sys.argv[1]]
            else:
                args = ["bash", "-c", "sudo -E nohup %s %s > /dev/null 2>&1 &" % (sys.executable, " ".join(sys.argv))]
            os.execvp("bash", args)
    elif os.name == "nt":
        if "pythonw" not in sys.executable and "python.exe" in sys.executable:
            subprocess.Popen([sys.executable.replace("python.exe", "pythonw.exe"), "-m", "spacebarheating", sys.argv[1]])
            return 0
    else:
        raise Exception("Unsupported Platform")
    return start()


if __name__ == "__main__":
    sys.exit(cli())
