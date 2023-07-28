# Importing the necessary modules
import os
import datetime
import shutil
import msgpack
import sys
import argparse

# A function to split a string into parts and join with slashes
def fourslashes(s):
    if s is None:
        return ''
    s = decode_if_bytes(s)
    split_id = [s[i:i+2] for i in range(0, 8, 2)]
    split_id.append(s[8:])
    return '/'.join(split_id)

def decode_if_bytes(s):
    if isinstance(s, bytes):
        return s.decode("utf-8")
    else:
        return s

# Create the argument parser
parser = argparse.ArgumentParser(description='Version 2.0\nTopdir is the directory of ocis storage. Default is $HOME/.ocis')

# Add an argument to the parser - topdir
parser.add_argument('topdir', nargs='?', default=os.getenv('HOME') + "/.ocis",
                    help='The directory of ocis storage')

# Add the new list argument
parser.add_argument('-l', '--list', action='store_true', help='List files without copying')

# Add the user argument
parser.add_argument('-u', '--user', help='Filter by username')

# Parse the command-line arguments
args = parser.parse_args()

# Store the provided top directory in the variable 'top'
top = args.topdir

# Define the top directory for the output
outtop = "/tmp/ocis-dump-" + datetime.datetime.now().strftime("%Y%m%d%H%M%S")

# Define the storage prefix
sprefix = "storage/users/spaces"

storage_dir = os.path.join(top, "storage")
if not os.path.isdir(storage_dir):
    print(f"'storage' folder not found in {top}")
    sys.exit(1)

print("top is: ", top)

def load_mpk_decoded(file):
    try:
        with open(file, 'rb') as f:
            mpk_content = msgpack.unpack(f, raw=True)
        return mpk_content
    except ValueError:
        print(f"Unpack failed for file: {file}")
        return None

user_exists = False

# Walk through the directory structure starting from 'top'
for dirpath, dirnames, filenames in os.walk(os.path.join(top, sprefix)):
    if 'nodes' in dirnames:
        # Get the directory for space nodes
        space_nodes_dir = dirpath
        # Construct the spaceid from the directory path
        spaceid = dirpath.split('/')[-2] + os.path.basename(dirpath)
        # Construct the root path
        root = os.path.join(space_nodes_dir, "nodes", fourslashes(spaceid))

        mpk_file = f"{root}.mpk"
        mpk_content = load_mpk_decoded(mpk_file)
        if mpk_content is not None:

            # Extract space name and type from the msgpack content
            space_name = mpk_content.get(b'user.ocis.space.name', b'N/A').decode('utf-8')
            space_type = mpk_content.get(b'user.ocis.space.type', b'N/A').decode('utf-8')

            if args.user and args.user.lower() not in space_name.lower():
                continue

            user_exists = True

            # Print the space info
            print(f"\n[{space_type}/{space_name}]")
            print(f"\troot = {root}")
            print(f"\ttreesize = {mpk_content.get(b'user.ocis.treesize', b'N/A')} bytes")
            print("\tsymlink_tree =")

            # Initialize a dictionary to store files and parents
            files_and_parents = {}

            # Go through the nodes
            nodes_dir = os.path.join(dirpath, "nodes")
            for dirpath2, dirnames2, filenames2 in os.walk(nodes_dir):
                for filename in filenames2:
                    if filename.endswith(".mpk"):
                        # Construct the path to the msgpack file
                        mpk_file2 = os.path.join(dirpath2, filename)
                        mpk_content2 = load_mpk_decoded(mpk_file2)
                        
                        # Extract parentid, blobid, and name from the msgpack content
                        parentid = mpk_content2.get(b'user.ocis.parentid')
                        blobid = mpk_content2.get(b'user.ocis.blobid', b'N/A')
                        name = mpk_content2.get(b'user.ocis.name', b'N/A')

                        # Check if blobid is available
                        if blobid != b'N/A':
                            # Check if parent is space
                            if parentid == spaceid:
                                files_and_parents[name.decode('utf-8')] = (".", blobid)
                            elif parentid is not None and parentid != spaceid:
                                # Construct the path to the parent
                                parent_path = os.path.join(space_nodes_dir, "nodes", fourslashes(parentid))
                                # Construct the path to the parent's msgpack file
                                mpk_file3 = f"{parent_path}.mpk"
                                mpk_content3 = load_mpk_decoded(mpk_file3)
                                # Extract the parent's name from the msgpack content
                                parent_name = mpk_content3.get(b'user.ocis.name', b'N/A').decode('utf-8')
                                files_and_parents[name.decode('utf-8')] = (f"./{parent_name}", blobid)

            # Copy the files to the output directory
            for i, (name, (parent_path, blobid)) in enumerate(files_and_parents.items(), start=1):
                # Construct the path to the blob
                blob_path = os.path.join(space_nodes_dir, "blobs", fourslashes(blobid))
                if os.path.exists(blob_path):
                    # Remove prefix from the personal space name
                    if space_type == "personal" and "_" in space_name:
                        space_name = space_name.split("_")[1]
                    # Construct the path to the temporary file
                    tmp_path = os.path.join(outtop, space_type, space_name, parent_path, name)
                    # Print file without copying if 'list' argument is provided
                    if args.list:
                        print(f"\t{i}\t{parent_path}/{name} -> blobid={blobid}")
                    else:
                        # Create the directories if they do not exist
                        os.makedirs(os.path.dirname(tmp_path), exist_ok=True)
                        # Copy the blob to the temporary file
                        shutil.copy2(blob_path, tmp_path)
                        print(f"\t{i}\t{parent_path}/{name} -> blobid={blobid}")
                else:
                    # Print a warning if the blob does not exist
                    print(f"WARNING: Blob file {blob_path} does not exist.")

# Print the location of the copied files
if not args.list:
    print(f"\nFiles were copied to: {outtop}")

if args.user and not user_exists:
    print(f"No user found with the username: {args.user}")
