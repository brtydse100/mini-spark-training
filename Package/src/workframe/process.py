"""Suspended Windows process startup, before any redirector can spawn children."""
import os
import subprocess
import sys


class SuspendedProcess:
    def __init__(self, arguments):
        import msvcrt
        import win32api
        import win32con
        import win32process
        startup = win32process.STARTUPINFO()
        startup.dwFlags = win32con.STARTF_USESTDHANDLES
        handles = []
        current = win32api.GetCurrentProcess()
        try:
            with open(os.devnull, "rb") as stdin:
                for attribute, stream in (("hStdInput", stdin), ("hStdOutput", sys.stdout), ("hStdError", sys.stderr)):
                    raw = msvcrt.get_osfhandle(stream.fileno())
                    duplicate = win32api.DuplicateHandle(current, raw, current, 0, True, win32con.DUPLICATE_SAME_ACCESS)
                    handles.append(duplicate)
                    setattr(startup, attribute, duplicate)
                self.handle, self.thread, self.pid, _ = win32process.CreateProcess(
                    None, subprocess.list2cmdline(arguments), None, None, True,
                    win32con.CREATE_SUSPENDED, None, None, startup)
        finally:
            for handle in handles:
                handle.Close()

    def resume(self):
        import win32process
        win32process.ResumeThread(self.thread)
        self.thread.Close()
        self.thread = None

    def poll(self):
        import win32event
        import win32process
        if win32event.WaitForSingleObject(self.handle, 0) == win32event.WAIT_TIMEOUT:
            return None
        return win32process.GetExitCodeProcess(self.handle)

    def wait(self, timeout=10):
        import win32event
        if win32event.WaitForSingleObject(self.handle, int(timeout * 1000)) == win32event.WAIT_TIMEOUT:
            raise TimeoutError("Child process did not exit")
        return self.poll()

    def kill(self):
        import win32api
        win32api.TerminateProcess(self.handle, 1)

    def close(self):
        if self.thread is not None:
            self.thread.Close()
            self.thread = None
        self.handle.Close()
