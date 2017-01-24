import subprocess as sp
import sys

def run_cmd(lst_cmd, verbose=False, silent=False):
    if silent and verbose:
        raise ValueError("Cannot specify both verbose and silent as true")

    p = sp.Popen(lst_cmd, stdin=sp.PIPE, stdout=sp.PIPE, stderr=sp.PIPE)
    tup_output = p.communicate()

    s_cmd = ' '.join(lst_cmd)
    if verbose:
        print("Command: '%s'\n" % s_cmd)
        if 0 != p.returncode:
            print("Command failed with code %d:" % p.returncode)
        else:
            print("Command succeeded! code %d" % p.returncode)
        print("Output for: " + s_cmd)
        print(tup_output[0])
    if not silent and 0 != p.returncode:
        print("Error output for: " + s_cmd)
        print(tup_output[1])

    return p.returncode
