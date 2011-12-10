from dependency import *
import sys
import time

# deptime entry point
def main(argv):
    if len(argv) < 3:
        sys.exit(
        """Usage: %s source-file include-path
    - source-file is the source code to search for its dependencies.
    - include-path is a semicolon-delimited list of paths
      to search for includes, in the order given.
        """ % argv[0])
    source_file = argv[1]
    include_path_list = argv[2]

    # Check that the file exists
    if not os.path.exists(source_file):
        sys.exit('Error: File %s does not exist' % source_file)

    # Split the semicolon-delimited list of paths
    include_paths = include_path_list.split(';')

    # Parse user headers of the source file recursively
    user_headers = findUserHeaders(source_file, os.curdir, include_paths)

    # Add the file to the list of user headers, because
    # we care about its timestamp as well
    user_headers.add(os.path.abspath(source_file))

    # Find the file in this list with the most recent timestamp
    latest_time = max(map(os.path.getmtime, user_headers))

    print time.ctime(latest_time)

if __name__ == '__main__':
    sys.exit(main(sys.argv))
 
