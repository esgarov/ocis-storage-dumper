## OCIS Storage Dump Utility

This script is used to extract files from an OCIS instance, such as a user's personal or project space. The script walks through the OCIS storage structure, finds all the blob files associated with each user, and copies them into a specified directory. It can also be used to simply list the files without actually copying them.

## Requirements

- Python 3
- msgpack module (use `pip install msgpack` to install)

## Usage

python3 dump.py [topdir] [-l/--list] [-u/--user=USERNAME]
topdir: The directory of ocis storage. Default is $HOME/.ocis.
-l/--list: List files without copying.
-u/--user USERNAME: Filter by username.

Examples

To extract all files from the OCIS storage and save to /tmp/ocis-dump-[timestamp]:
python3 dump.py

To list all files in the OCIS storage without copying:
python3 dump.py -l

To extract all files from a particular user's spaces:
python3 dump.py -u=john_doe

Limitations

This script is designed to work with the specific structure of OCIS. If the OCIS storage structure is modified or a different storage backend is used, the script may not work as expected.

Please note that it only copies files that are available as blobs in the OCIS storage. Any files that are not yet fully uploaded or are stored in a different format cannot be copied.

Contribution

Contributions are welcome! Please feel free to submit a Pull Request.
