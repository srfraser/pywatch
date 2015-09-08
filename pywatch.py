#!/usr/bin/python

"""
pywatch: Implement 'watch' in python, with numerical diffs
"""

import os
import sys
from subprocess import check_output
import time
from datetime import datetime
from collections import defaultdict
import re

def ansicolored(string, colour):
    """
    Show a colour output in the absence of termcolor
    """
    colormap = {
        'pink': '\033[95m',
        'blue': '\033[94m',
        'green': '\033[92m',
        'yellow': '\033[93m',
        'red': '\033[91m',
        'end': '\033[0m',
    }
    return colormap.get(colour, '') + string + colormap.get('end')

try:
    from termcolor import colored
except ImportError as exception:
    def colored(string, colour):
        return ansicolored(string, colour)


# command line options for:
# interval
# use colour
# + - insertion

cache = defaultdict(list)

def linefilter(data):
    """
    Strip all numbers out of the line
    use that as an index in a dict() to a list of numbers
    if len(numbers) doesn't add up, assume new entry
    if dict entry doesn't exist, assume new entry

    if exists and length matches, then see what the previous numbers were

    if the same, reinsert number
    if higher, insert +<green>diff</green>
    if lower, insert -<red>diff</red>
    store replacement previous values
    """


    # recognise ipv4 address and skip ( three times . )
    # recognise ipv4:port tuple
    # captures should include at most one '.'

    num_re = re.compile(r'([^\d])([ :])([-\.\d]+)')

    return_lines = list()

    for line in data.split('\n'):
        numbers = list()
        original_numbers = list()
        index = str()

        for field in num_re.split(line):
            try:
                flf = float(field)
                # .format placeholder for later re-insertion
                index += "{}"
                numbers.append(flf)
                # Show the original number later if it hasn't changed
                # avoids float conversion issues
                original_numbers.append(field)
            except:
                index += field

        new_numbers = list()

        # if we've not seen it before, or it's got a different set of values
        if index not in cache or len(numbers) != len(cache[index]):
            cache[index] = numbers
            new_numbers = original_numbers
        else:
            for old, new, raw in zip(cache[index], numbers, original_numbers):
                if new == old:
                    new_numbers.append(raw)
                elif new > old:
                    new_numbers.append(colored("+{}".format(new-old), 'green'))
                else:
                    new_numbers.append(colored("-{}".format(old-new), 'red'))
            cache[index] = numbers

        return_lines.append(index.format(*new_numbers))

    return "\n".join(return_lines)



def main():
    cmd = " ".join(sys.argv[1:])
    interval = 2

    while True:
        os.system("clear")
        print("Every {interval}s: {fcmd} at {now}".format(
            interval=interval,
            fcmd=" ".join(cmd),
            now=datetime.now()))
        cmd_output = check_output(cmd, shell=True)
        print(linefilter(cmd_output))
        time.sleep(interval)

if __name__ == '__main__':
    main()
