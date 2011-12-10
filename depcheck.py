from dependency import *
import sys

# depcheck entry point
def main(argv):
    if len(argv) < 3:
        sys.exit('Usage: %s source-file include-path' % argv[0])
    source_file = argv[1]
    include_path_list = argv[2]

    # Check that the file exists
    if not os.path.exists(source_file):
        sys.exit('Error: File %s does not exist' % source_file)

    # Split the semicolon-delimited list of paths
    include_paths = include_path_list.split(';')

    # Parse user headers of the source file recursively
    user_headers = findUserHeaders(source_file, os.curdir, include_paths)

    for header in user_headers:
        print header
    

if __name__ == '__main__':
	sys.exit(main(sys.argv))
