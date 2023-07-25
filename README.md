OCIS Storage Dump Utility

This utility is designed to assist in exploring the directory structure of OCIS storage. It extracts file and folder information, including metadata and blob ID information, from msgpack files in the OCIS storage.

Additionally, the utility copies the files from OCIS storage to a specified output directory.

How To Use
Prerequisites
Python 3
Libraries: os, datetime, shutil, msgpack, json, sys, argparse

Running the Script
python3 ocis_dump.py [path_to_ocis_storage]
If no argument is provided, it will default to ~/.ocis.

The script will:

Walk through the OCIS storage directory structure.
Extract metadata from msgpack files.
Output information about the spaces (user's storage areas in OCIS), such as space type, space name, and total space size.
Output a list of files in each space, along with the parent directory, blob ID, and corresponding OCIS storage location.
Copy the files from OCIS storage to a temporary directory (default: /tmp/ocis-dump-{timestamp}).
Output Example

top is:  /home/user/.ocis

[personal/user1]
    root = /home/user/.ocis/storage/users/spaces/xx/xx/xxxxxxx/nodes/xxxx/xxxx/xxxxxxx
    treesize = 123456 bytes
    symlink_tree =
    1   ./dir1/file1.txt -> blobid=xxxxxxxxxxxxxx
    2   ./dir2/file2.jpg -> blobid=xxxxxxxxxxxxxx

Files were copied to: /tmp/ocis-dump-20230725060000
This indicates that the script has successfully extracted the data from OCIS storage and copied the files to the specified directory. The first part of the output represents the information about the space, while the second part shows the information about the files within the space.

Note
This utility only retrieves and copies files. It doesn't modify the original OCIS storage data.
