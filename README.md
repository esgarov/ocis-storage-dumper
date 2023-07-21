# OCIS Storage Dumper

OCIS Storage Dumper is a Python script to traverse an ownCloud Infinite Scale (OCIS) storage system's directory structure, extract metadata from `.mpk` files and copy the blob files associated with these metadata to a separate directory.

## Prerequisites

Ensure you have Python 3.6+ installed on your system.

## Usage

To use this script, run the following command:

bash
python ocis_storage_dumper.py [topdir]

Here topdir is the directory of OCIS storage. By default, it points to $HOME/.ocis.

The script generates a temporary directory in /tmp/ocis-dump-<timestamp>, where the extracted blob files will be placed.
##Features

    Walks through the directory structure of an OCIS storage.
    Extracts metadata from .mpk files.
    Copies blob files associated with the metadata to a separate directory.

##Output

The script will print information about each OCIS storage space, including the space's name, type, root directory, tree size, and a symlink tree. Files are copied to the output directory, and their locations are printed to the console.

For each file, the script will attempt to resolve the file's parent directory and print a blobid for reference. If the blob file cannot be found, a warning will be printed.
##Disclaimer

Please use this script responsibly and ensure you have necessary permissions to access and modify the directories in question.
