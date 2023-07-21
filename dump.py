import os
import datetime
import shutil
import subprocess
import json
import sys

def fourslashes(s):
    if s is None:
        return ''
    split_id = [s[i:i+2] for i in range(0, 8, 2)]
    split_id.append(s[8:])
    return '/'.join(split_id)

if len(sys.argv) > 1 and (sys.argv[1] == '-h' or sys.argv[1] == '--help'):
  print("""
Version 1.0
Usage:
        %s [topdir]

Topdir is the directory of ocis storage. Default is $HOME/.ocis
""" % (sys.argv[0]))
  sys.exit(0)
  
top = os.getenv('HOME') + "/.ocis"
if len(sys.argv) > 1:
  top=sys.argv[1]

print("top is: ", top)
outtop = "/tmp/ocis-dump-" + datetime.datetime.now().strftime("%Y%m%d%H%M%S")

sprefix = "storage/users/spaces"
mpkq_path = os.getenv('HOME') + "/.local/bin/mpkq.py"

for dirpath, dirnames, filenames in os.walk(os.path.join(top, sprefix)):
    if 'nodes' in dirnames:
        space_nodes_dir = dirpath      
        spaceid = dirpath.split('/')[-2] + os.path.basename(dirpath)
        root = os.path.join(space_nodes_dir, "nodes", fourslashes(spaceid))
        mpk_file = f"{root}.mpk"
        process = subprocess.Popen([mpkq_path, mpk_file], stdout=subprocess.PIPE)
        out, err = process.communicate()
        mpk_content = json.loads(out.decode())

        space_name = mpk_content.get('user.ocis.space.name', 'N/A')
        space_type = mpk_content.get('user.ocis.space.type', 'N/A')

        print(f"\n[{space_type}/{space_name}]")
        print(f"\troot = {root}")
        print(f"\ttreesize = {mpk_content.get('user.ocis.treesize', 'N/A')} bytes")
        print("\tsymlink_tree =")

        files_and_parents = {}

        nodes_dir = os.path.join(dirpath, "nodes")
        for dirpath2, dirnames2, filenames2 in os.walk(nodes_dir):
            for filename in filenames2:
                if filename.endswith(".mpk"):
                    mpk_file2 = os.path.join(dirpath2, filename)
                    process2 = subprocess.Popen([mpkq_path, mpk_file2], stdout=subprocess.PIPE)
                    out2, err2 = process2.communicate()
                    mpk_content2 = json.loads(out2.decode())

                    parentid = mpk_content2.get('user.ocis.parentid')
                    blobid = mpk_content2.get('user.ocis.blobid', 'N/A')
                    name = mpk_content2.get('user.ocis.name', 'N/A')

                    if blobid != 'N/A':
                        if parentid == spaceid:
                            files_and_parents[name] = (".", blobid)
                        elif parentid is not None and parentid != spaceid:
                            parent_path = os.path.join(space_nodes_dir, "nodes", fourslashes(parentid))
                            mpk_file3 = f"{parent_path}.mpk"
                            process3 = subprocess.Popen([mpkq_path, mpk_file3], stdout=subprocess.PIPE)
                            out3, err3 = process3.communicate()
                            mpk_content3 = json.loads(out3.decode())
                            parent_name = mpk_content3.get('user.ocis.name', 'N/A')
                            files_and_parents[name] = (f"./{parent_name}", blobid)

        for i, (name, (parent_path, blobid)) in enumerate(files_and_parents.items(), start=1):
            blob_path = os.path.join(space_nodes_dir, "blobs", fourslashes(blobid))
            if os.path.exists(blob_path):
                if space_type == "personal" and "_" in space_name:
                    space_name = space_name.split("_")[1] # remove prefix from the personal space_name
                tmp_path = os.path.join(outtop, space_type, space_name, parent_path, name)
                os.makedirs(os.path.dirname(tmp_path), exist_ok=True)
                shutil.copy2(blob_path, tmp_path)
                print(f"\t{i}\t{parent_path}/{name} -> blobid={blobid}")
            else:
                print(f"WARNING: Blob file {blob_path} does not exist.")

print(f"\nFiles were copied to: {outtop}")

