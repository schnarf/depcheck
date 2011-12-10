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

    def test_search(self):
        test_dir = 'tests/search_include_paths'
        # Search for 1.h which is in the base path and all the other paths
        base_dir = test_dir
        base_file = '1.h'
        paths = [os.path.join(test_dir, 'c'),
            os.path.join(test_dir, 'a'),
            os.path.join(test_dir, 'b')]
        full_path = searchIncludePath(base_file, base_dir, paths)
        expected_path = os.path.abspath('tests/search_include_paths/1.h')
        self.assertEqual(full_path, expected_path)

        # Search for 2.h which is in all paths but the base path
        base_file = '2.h'
        expected_path = os.path.abspath('tests/search_include_paths/c/2.h')
        full_path = searchIncludePath(base_file, base_dir, paths)
        self.assertEqual(full_path, expected_path)

        # Search for 3.h which is only in "b"
        base_file = '3.h'
        expected_path = os.path.abspath('tests/search_include_paths/b/3.h')
        full_path = searchIncludePath(base_file, base_dir, paths)
        self.assertEqual(full_path, expected_path)

        # Remove "b" from the paths, and then search for 3.h
        # We expect not to find it
        paths.pop()
        full_path = searchIncludePath(base_file, base_dir, paths)
        self.assertEqual(full_path, None)

if __name__ == '__main__':
    unittest.main()
