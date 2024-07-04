import glob
import os
import shutil
import zipfile


def remove_folder_contents(separator):
    if os.path.exists("function.zip"):
        os.remove("function.zip")
    if os.path.exists("dist"):
        folder_files = glob.glob('dist' + separator + '*')
        for f in folder_files:
            os.remove(f)


def zip_files_with_name(name_part, zip_name):
    files_to_zip = [file for file in os.listdir() if name_part in file]
    with zipfile.ZipFile(zip_name, 'w') as zipf:
        for file in files_to_zip:
            zipf.write(file)


def copy_files_to_parent_directory(source_dir):
    parent_dir = os.path.abspath(os.path.join(source_dir, os.pardir))

    files = os.listdir(source_dir)

    for file in files:
        source_file = os.path.join(source_dir, file)

        dest_file = os.path.join(parent_dir, file)

        shutil.copy(source_file, dest_file)
