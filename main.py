import os
import re
import json
from datetime import datetime
from PIL import Image
import piexif
import shutil


def update_exif_datetime(image_path, new_datetime, edit = True):
    """
    Updates the EXIF data for "DateTimeOriginal" and "DateTimeDigitized" 
    with the provided new_datetime in YYYY:MM:DD HH:MM:SS format.

    Args:
      image_path: Path to the image file.
      new_datetime: New date and time in YYYY:MM:DD HH:MM:SS format.
    """
    modified = False
    try:
        exif_dict = piexif.load(image_path)

        try:
            dateTime = exif_dict["0th"].get(piexif.ImageIFD.DateTime)
            # print(f"dateTime : {dateTime}")
            if dateTime is None and edit:
                exif_dict["0th"][piexif.ImageIFD.DateTime] = new_datetime
                modified = True
        except Exception as error:
            print(f"DateTime field not available")

        try:
            dateTimeDigitized = exif_dict["Exif"].get(
                piexif.ExifIFD.DateTimeDigitized)
            # print(f"dateTimeDigitized : {dateTimeDigitized}")
            if dateTimeDigitized is None and edit:
                exif_dict["Exif"][piexif.ExifIFD.DateTimeDigitized] = new_datetime
                modified = True
        except Exception as error:
            print(f"DateTimeDigitized field not available")

        # Update DateTimeOriginal and DateTimeDigitized tags
        # exif_dict["0th"][piexif.ImageIFD.DateTime] = new_datetime
        # exif_dict["Exif"][piexif.ExifIFD.DateTimeDigitized] = new_datetime

        # Save the updated EXIF data
        exif_bytes = piexif.dump(exif_dict)
        piexif.insert(exif_bytes, image_path)

        # print(f"EXIF data updated for {image_path}")
    except Exception as e:
        print(f"Error updating EXIF data: {e}")

    return modified


def convert_time_stamp(given_datetime):
    try:
        original_date = datetime.strptime(
            given_datetime, "%b %d, %Y, %H:%M:%S %p %Z")
    except ValueError as error:
        original_date = datetime.strptime(
            given_datetime, "%d %b %Y, %H:%M:%S %Z")

    return original_date


def move_file(file_name, source_dir, destination_dir):

    if not os.path.exists(destination_dir):
        os.makedirs(destination_dir)

    try:
        if not os.path.exists(destination_dir+file_name):
            # Move the file to the destination directory
            shutil.move(source_dir, destination_dir)
            # print(f'File moved successfully to {destination_dir}')
        else:
            print(f"File already exists. {file_name}")
    except Exception as error:
        print(f"Error while moving file. {str(error)}")


def main(folder):
    # Get the list of all files and directories    
    dir_path = f"./{folder}"
    dir_list = os.listdir(dir_path)
    print(f"{len(dir_list)} Files and directories in {dir_path}")

    for i in range(0, len(dir_list)):

        try:
            image_path = dir_path + "/" + dir_list[i]
            # print(f"image path {image_path}")

            if ".json" in image_path:
                continue

            #check delicacy
            pattern = r"\(\d+\)"
            duplicate_match = re.search(pattern, dir_list[i])

            if duplicate_match:
              new_string = re.sub(pattern, "", dir_list[i])
              if os.path.exists(f"./{folder}/{new_string}"):
                  move_file(dir_list[i], image_path, f"./{folder}/duplicate")
                  continue

            json_obj = open(f"./{folder}/" +
                            dir_list[i] + '.json')
            json_data = json.load(json_obj)

            json_datetime = json_data['photoTakenTime'].get("formatted")
            if 'â€¯' in json_datetime:
                json_datetime = json_datetime.replace('â€¯', ' ')

            original_date = convert_time_stamp(json_datetime)

            desired_format = "%Y:%m:%d %H:%M:%S"
            new_datetime = original_date.strftime(desired_format)

            json_obj.close()

            modified = update_exif_datetime(image_path, new_datetime)

            # if modified :
            #     move_file(dir_list[i], image_path, f"./{folder}/re_upload")

            print(f"file processed successfully. {modified} {dir_list[i]}")

        except FileNotFoundError as error:
            print(f"meta data file not found: {str(error)}")
            if update_exif_datetime(image_path,"", False) == False:
              move_file(dir_list[i], image_path, f"./{folder}/undefined")
        except Exception as error:
            print(f"error: {str(error)}")


main("Photos_from_2023")
