import sys
import re
import os.path
import unittest

# Parses system headers from the given source code
def parseSystemHeaders(source):
    matches = re.finditer(r"^\s*#include <(.*)>", source, re.MULTILINE)
    headers = set()
    for match in matches:
        headers.add(match.group(1))
    return headers

# Parses user headers from the given source code
def parseUserHeaders(source):
    matches = re.finditer(r"^\s*#include \"(.*)\"", source, re.MULTILINE)
    headers = set()
    for match in matches:
        headers.add(match.group(1))
    return headers

# Searches in the current directory, then the list of paths,
# for the given file. Returns the first fully qualified path
# it finds, or None if no file exists
def searchIncludePath(source_file_base, cur_path, paths):
    # Search in the current directory first
    source_file = os.path.join(cur_path, source_file_base)
    if os.path.exists(source_file):
        return os.path.abspath(source_file)

    # It wasn't found in the current directory, so search the list
    source_file= None
    for path in paths:
        filename = os.path.join(path, source_file_base)
        if os.path.exists(filename):
            source_file = os.path.abspath(filename)
            break

    return source_file

# Loads a source file and parses its user headers
# Ignores any headers listed in ignores
def findUserHeaders(source_file_base, cur_path, paths, ignores=set()):
    # Search for the fully qualified path to open
    source_file = searchIncludePath(source_file_base, cur_path, paths)

    # Silently return an empty set if the file does not exist
    if source_file == None:
        return set()

    # Read the source file
    f = open(source_file, 'r')
    source = f.read()
    f.close()

    # Now set the current path to the path of the file we found
    cur_path = os.path.dirname(source_file)

    # Parse user headers, excluding ignored ones
    user_headers = parseUserHeaders(source).difference(ignores)

    # Update the ignores: ignore the ignores that
    # were passed in, as well as the headers we parsed
    new_ignores = ignores.union(user_headers)

    # Try to load each of the headers, ignoring
    # the new ignore set so we don't get stuck in a loop
    # if there are circular includes
    headers = set()
    for header in user_headers:
        # Look up the fully-qualified path and store it
        header_file = searchIncludePath(header, cur_path, paths)
        headers.add(header_file)

        # Now find the user headers in that file, and add them as well
        found_headers = findUserHeaders(header, cur_path, paths, new_ignores)
        headers.update(found_headers)

    return headers

class TestDependency(unittest.TestCase):
    """
    A test class for the dependency module
    """

    def test_parsing(self):
        # Load the file
        f = open('tests/test_parsing.cpp', 'r')
        source = f.read()
        f.close()

        # Parse the headers
        system_headers = parseSystemHeaders(source)
        user_headers = parseUserHeaders(source)

        target_system_headers = set(['iostream', 'also_included', 'also_included.h'])
        target_user_headers = set(['some_header.h', 'still_included.h'])

        self.assertEqual(system_headers, target_system_headers)
        self.assertEqual(user_headers, target_user_headers)

if __name__ == '__main__':
    unittest.main()
