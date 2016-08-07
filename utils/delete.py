#!/usr/bin/env/python3
import sys

def delete_all_libraries(args, galaxy_instance=None):
    # Get all parameters

    gi = galaxy_instance

    # Ask confirmation to delete all libraries
    input_delete = input("Are you sure to delete ALL your Galaxy libraries? (y)es or (no) ")
    if input_delete != "yes" and input_delete != "y":
        print(input_delete)
        print("Wise choice...bye!")
        sys.exit(0)

    libraries_not_deleted = [lib
                             for lib in gi.libraries.get_libraries()
                             if lib['deleted'] is False]
    if len(libraries_not_deleted) == 0:
        print("No libraries...lucky you? :)")
        return

    for libs in libraries_not_deleted:
        gi.libraries.delete_library(libs['id'])
        print("{0} deleted".format(libs['name']))

if __name__ == "__main__":
    print("Please see the option to call this script from the main program. Quiting...")
    sys.exit(-1)
