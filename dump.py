# Importing the necessary modules
import os
import datetime
import shutil
import msgpack
import json
import sys
import argparse

# A function to split a string into parts and join with slashes
def fourslashes(s):
    if s is None:
        return ''
    if isinstance(s, bytes):
        s = s.decode()
    split_id = [s[i:i+2] for i in range(0, 8, 2)]
    split_id.append(s[8:])
    return '/'.join(split_id)

# Create the argument parser
parser = argparse.ArgumentParser(description='Version 1.0\nTopdir is the directory of ocis storage. Default is $HOME/.ocis')

# Add an argument to the parser - topdir
parser.add_argument('topdir', nargs='?', default=os.getenv('HOME') + "/.ocis",
                    help='The directory of ocis storage')

# Parse the command-line arguments
args = parser.parse_args()

# Store the provided top directory in the variable 'top'
top = args.topdir
print("top is: ", top)

# Define the top directory for the output
outtop = "/tmp/ocis-dump-" + datetime.datetime.now().strftime("%Y%m%d%H%M%S")

# Define the storage prefix
sprefix = "storage/users/spaces"

# Walk through the directory structure starting from 'top'
for dirpath, dirnames, filenames in os.walk(os.path.join(top, sprefix)):
    if 'nodes' in dirnames:
        # Get the directory for space nodes
        space_nodes_dir = dirpath      
        # Construct the spaceid from the directory path
        spaceid = dirpath.split('/')[-2] + os.path.basename(dirpath)
        # Construct the root path
        root = os.path.join(space_nodes_dir, "nodes", fourslashes(spaceid))
        # Construct the path to the msgpack file
        mpk_file = f"{root}.mpk"
        # Open and read the msgpack file
        with open(mpk_file, 'rb') as f:
            mpk_content = msgpack.unpack(f, raw=False)

        # Extract space name and type from the msgpack content
        space_name = mpk_content.get('user.ocis.space.name', 'N/A')
        space_type = mpk_content.get('user.ocis.space.type', 'N/A')
        # Decode if the extracted values are bytes
        if isinstance(space_name, bytes):
            space_name = space_name.decode()
        if isinstance(space_type, bytes):
            space_type = space_type.decode()

        # Print the space info
        print(f"\n[{space_type}/{space_name}]")
        print(f"\troot = {root}")
        print(f"\ttreesize = {mpk_content.get('user.ocis.treesize', 'N/A')} bytes")
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
                    # Open and read the msgpack file
                    with open(mpk_file2, 'rb') as f:
                        mpk_content2 = msgpack.unpack(f, raw=False)

                    # Extract parentid, blobid, and name from the msgpack content
                    parentid = mpk_content2.get('user.ocis.parentid')
                    blobid = mpk_content2.get('user.ocis.blobid', 'N/A')
                    name = mpk_content2.get('user.ocis.name', 'N/A')
                    # Decode if the extracted values are bytes
                    if isinstance(parentid, bytes):
                        parentid = parentid.decode()
                    if isinstance(blobid, bytes):
                        blobid = blobid.decode()
                    if isinstance(name, bytes):
                        name = name.decode()

                    # Check if blobid is available
                    if blobid != 'N/A':
                        # Check if parent is space
                        if parentid == spaceid:
                            files_and_parents[name] = (".", blobid)
                        elif parentid is not None and parentid != spaceid:
                            # Construct the path to the parent
                            parent_path = os.path.join(space_nodes_dir, "nodes", fourslashes(parentid))
                            # Construct the path to the parent's msgpack file
                            mpk_file3 = f"{parent_path}.mpk"
                            # Open and read the parent's msgpack file
                            with open(mpk_file3, 'rb') as f:
                                mpk_content3 = msgpack.unpack(f, raw=False)
                            # Extract the parent's name from the msgpack content
                            parent_name = mpk_content3.get('user.ocis.name', 'N/A')
                            # Decode if the extracted value is bytes
                            if isinstance(parent_name, bytes):
                                parent_name = parent_name.decode()
                            files_and_parents[name] = (f"./{parent_name}", blobid)

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
                # Create the directories if they do not exist
                os.makedirs(os.path.dirname(tmp_path), exist_ok=True)
                # Copy the blob to the temporary file
                shutil.copy2(blob_path, tmp_path)
                print(f"\t{i}\t{parent_path}/{name} -> blobid={blobid}")
            else:
                # Print a warning if the blob does not exist
                print(f"WARNING: Blob file {blob_path} does not exist.")

# Print the location of the copied files
print(f"\nFiles were copied to: {outtop}")
