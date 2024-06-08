import os.path
import shutil

from random import shuffle

from tools import directory_checkout, find_string_part_in_list


def get_images_and_labels(directory: str):
    all_files = os.listdir(directory)
    image_files = [file for file in all_files if
                   file.endswith('.png') or file.endswith('.jpg') or file.endswith('.jpeg')]
    label_files = [file for file in all_files if file.endswith('.txt')]
    return image_files, label_files


def dataset_checkout(dataset_path: str):
    image_files, label_files = get_images_and_labels(dataset_path)

    verify_flag = True
    invalid_files = []
    if len(label_files) == 0:
        print('Nothing to verify')
    else:
        images_without_extension = [file[:file.index(".")] for file in image_files]
        for file in label_files:
            with open(f"{dataset_path}/{file}", "r") as label_reader:
                label_contents = label_reader.readlines()

            for line in label_contents:
                # verification of labels FOR YOLOv5, NOT UNIVERSAL,
                # CHANGE IF DATASET VERIFIER WILL BE IMPLEMENTED
                line_as_list = line.replace("\n", "").split(" ")
                if len(line_as_list) != 5:
                    verify_flag = False
                    invalid_files.append(file)

                for number in line_as_list:
                    try:
                        float(number)
                    except ValueError:
                        try:
                            int(number)
                        except ValueError:
                            verify_flag = False
                            invalid_files.append(file)

            without_extension = file[:file.index(".")]
            if without_extension not in images_without_extension:
                verify_flag = False
                invalid_files.append(file)

    return verify_flag, invalid_files


def get_available_classes_and_yaml(dataset_path: str):
    yaml_path = None
    available_classes = dict()
    yaml_file = [file for file in os.listdir(dataset_path) if file.endswith('.yaml')]
    _, label_files = get_images_and_labels(dataset_path)

    if len(yaml_file) > 1:
        print('More than one .yaml file found')
    elif len(yaml_file) == 0:
        print("No .yaml file found")
        max_class_number = 0
        for label_file in label_files:
            with open(f"{dataset_path}/{label_file}", "r") as label_reader:
                labels = label_reader.readlines()
                for label in labels:
                    if int(label.split(" ")[0]) > max_class_number:
                        max_class_number = int(label.split(" ")[0])

        for class_number in range(max_class_number):
            available_classes.update({f"{class_number}": f"{class_number}"})
        return None, available_classes

    else:
        yaml_path = yaml_file[0]

    return yaml_path, available_classes


def prepare_dataset_for_training(dataset_path: str, training_directory: str, yaml_path: str, train_prop):
    """Dividing the dataset according to the desired proportions and copying it into the selected directory"""
    image_files, _ = get_images_and_labels(dataset_path)

    # Get the relative paths saved in the yaml file
    with open(f"{dataset_path}/{yaml_path}", "r") as yaml_reader:
        yaml_contents = yaml_reader.readlines()
    _, train_path_line = find_string_part_in_list("train:", yaml_contents)
    _, val_path_line = find_string_part_in_list("val:", yaml_contents)
    train_images_path = train_path_line[train_path_line.index(":") + 1:train_path_line.index("#")].strip()
    val_images_path = val_path_line[val_path_line.index(":") + 1:val_path_line.index("#")].strip()

    train_labels_path = train_images_path.replace("images", "labels")
    val_labels_path = val_images_path.replace("images", "labels")

    train_images_full_path = os.path.join(training_directory, str(train_images_path))
    train_labels_full_path = os.path.join(training_directory, str(train_labels_path))
    val_images_full_path = os.path.join(training_directory, str(val_images_path))
    val_labels_full_path = os.path.join(training_directory, str(val_labels_path))

    try:
        directory_checkout(training_directory)
        directory_checkout(os.path.join(training_directory, "images"))
        directory_checkout(os.path.join(training_directory, "labels"))
        directory_checkout(train_images_full_path)
        directory_checkout(train_labels_full_path)
        directory_checkout(val_images_full_path)
        directory_checkout(val_labels_full_path)
    except PermissionError:
        print("FIX THE PERMISSION ERROR!")

    number_of_train_images = int(train_prop * len(image_files))

    shuffle(image_files)

    train_images = image_files[:number_of_train_images]
    val_images = image_files[number_of_train_images:]

    for train_image in train_images:
        shutil.copy(os.path.join(dataset_path, str(train_image)),
                    os.path.join(train_images_full_path, str(train_image)))

        labels_name = f"{train_image[:train_image.index('.')]}.txt"
        labels_path = os.path.join(dataset_path, labels_name)

        if os.path.exists(labels_path):
            shutil.copy(labels_path, os.path.join(train_labels_full_path, labels_name))

    for val_image in val_images:
        shutil.copy(os.path.join(dataset_path, str(val_image)),
                    os.path.join(val_images_full_path, str(val_image)))

        labels_name = f"{val_image[:val_image.index('.')]}.txt"
        labels_path = os.path.join(dataset_path, labels_name)

        if os.path.exists(labels_path):
            shutil.copy(labels_path, os.path.join(val_labels_full_path, labels_name))
