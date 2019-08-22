#!/usr/bin/env python3
"""
Python script to unzip DSpace objects, Bag them, Tar them, and generate Md5s.
"""

import argparse
import bagit
import hashlib
import io
import tarfile
import defusedxml.ElementTree as ET
from os import listdir, path, remove
from shutil import rmtree
from time import strftime
from zipfile import ZipFile


def unzip_all(**kwargs):
    """ Unzip the aip.zip, if necessary and unzip the DSpace items it contains """
    aip_fol = kwargs['mainfol']
    if len(kwargs) == 2:
        zip_file = kwargs['mainzip']
        zip_ref = ZipFile(zip_file, 'r')
        zip_ref.extractall(path.dirname(aip_fol))
        zip_ref.close()
    elif len(kwargs) != 2 and len(kwargs) != 1:
        print("Error. Incorrect number of arguments.")
        return
    for z in listdir(aip_fol):
        if path.splitext(z)[-1] == ".zip":
            zip_path = path.join(aip_fol, z)
            out_folder = path.splitext(zip_path)[0]
            zip_ref2 = ZipFile(zip_path, 'r')
            zip_ref2.extractall(out_folder)
            remove(zip_path)
    return


def bag_item(item_dir):
    """ Create an APTrust compliant Bag and insert the aptrust-info.txt file """
    today = strftime("%Y-%m-%d")
    metsfile = path.join(item_dir, "mets.xml")
    description = "n/a"
    with open(metsfile, 'rb') as mets:
        mtree = ET.parse(mets)
        mroot = mtree.getroot()
        for child in mroot.iter():
            if 'mets' in child.tag and 'OBJID' in child.attrib:
                item_id = child.attrib['OBJID']
            if 'mods' in child.tag:
                if 'tableOfContents' in child.tag and child.text is not None:
                    description = child.text
                elif 'note' in child.tag and child.text is not None:
                    description = child.text
                elif 'abstract' in child.tag and child.text is not None:
                    description = child.text
    internal_id = "http://hdl.handle.net/" + item_id.split(':')[1]
    group_id = "vtechworks"
    bag = bagit.make_bag(item_dir, {
        'Source-Organization': 'Virginia Tech University Libraries',
        'Bagging-Date': today,
        'Bag-Count': '1 of 1',
        'Internal-Sender-Description': description,
        'Internal-Sender-Identifier': internal_id,
        'Bag-Group-Identifier': group_id
    }, checksums=["md5", "sha256"])
    apt_title = f"vt.{item_id.split(':')[1].split('/')[0]}_{item_id.split(':')[1].split('/')[1]}"
    apt_info = open(path.join(item_dir, "aptrust-info.txt"), 'w')
    apt_info.write(f"Title: {apt_title}\n")
    apt_info.write(f"Access: Institution\n")
    apt_info.close()
    return [bag, apt_title]


def tar_item(obj_path, tarname):
    outfile = path.join(path.dirname(obj_path), tarname + ".tar")
    with tarfile.open(outfile, 'w:') as newtar:
        newtar.add(obj_path, arcname=path.basename(obj_path))
    newtar.close()
    return outfile


def md5sum(infile):
    chunksize = io.DEFAULT_BUFFER_SIZE
    hash_md5 = hashlib.md5()
    with open(infile, "rb") as md5file:
        for chunk in iter(lambda: md5file.read(chunksize), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def main(aip_exp):
    if path.splitext(aip_exp)[-1] == ".zip":
        main_folder = path.splitext(aip_exp)[0]
        unzip_all(mainfol=main_folder, mainzip=aip_exp)
    elif path.isdir(aip_exp):
        main_folder = aip_exp
        unzip_all(mainfol=main_folder)
    else:
        print(f"Error. Input {aip_exp} is neither a .zip file nor a directory.\n Quitting...")
        return
    successful = 0
    validbags = 0
    timenow = strftime("%m%d_%H%M%S")
    hashlist = open(path.join(main_folder, f"Md5Sums-{timenow}.csv"), 'w')
    for i in listdir(main_folder):
        item_path = path.join(main_folder, i)
        if path.isdir(item_path):
            bag_results = bag_item(item_path)
            if bag_results[0].is_valid():
                validbags += 1
            tar_file = tar_item(item_path, bag_results[1])
            if path.exists(tar_file):
                rmtree(item_path)
            tar_hash = md5sum(tar_file)
            print(f"{path.basename(tar_file)} {tar_hash}")
            hashlist.write(f"{path.basename(tar_file)},{tar_hash}\n")
            successful += 1
    hashlist.close()
    print(f"Created {successful} Tar files from {validbags} valid Bag files.")
    return successful


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="""
                                Unzip, Bag, and Checksum DSpace 'AIP Export'.
                                Input is a DSpace 'AIP Export'.
                                Output is a directory of tarred and bagged
                                items and a CSV of Md5 checksum hashes for
                                the items.
                                """)
    parser.add_argument("dspace_aip", type=str, help="Path to DSpace AIP Export")
    args = parser.parse_args()
    aip_input = args.dspace_aip
    if path.exists(aip_input):
        no_items = main(aip_input)
        print(f"Bagged, Tarred, and Hashed {no_items} items.")
    else:
        print("Error. DSpace AIP export file or folder not found.")
