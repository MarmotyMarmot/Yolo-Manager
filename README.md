# Yolo-Manager
## Overview
Yolo-Manager is designed to help users easily manage and modify YOLO datasets. 
This tool allows users to read, verify and modify their dataset classes, as well as prepare the dataset for training.

### Start Screen
![startScreen](https://github.com/MarmotyMarmot/Yolo-Manager/assets/45321229/f95adacb-a58a-4139-829d-6b3c9dd3fc72)

### Example from COCO
![exampleFromCOCO](https://github.com/MarmotyMarmot/Yolo-Manager/assets/45321229/5c64c0e3-d5a9-45db-ae3b-46b8500328c0)

### YAML Editor
![YAMLEditor](https://github.com/MarmotyMarmot/Yolo-Manager/assets/45321229/920fd014-7b27-4d04-936d-1a5ac7c2c940)

## Features
- Image annotation
- Dataset validation
- Class modification
- Prepare dataset for training
- Use YOLOv5 model to label an image
- Copy/paste labels from image to image

## Manual
### Running the programme
1. Clone the repository.
2. Download the required libraries from requirements.txt.
3. Make sure that the .yaml file and all the .jpg/.png/.jpeg/.txt files in your dataset are in one directory.
4. Run main.py.
5. If the dataset is not selected, the programme won't allow you to press any buttons except the Read dataset button.
6. To close the programme close it conventionally or use the "Esc" keyboard shortcut.

### Choosing the dataset
1. Click on the green Read Dataset button in the upper left corner.
2. Select the directory containing your dataset.

### Image labelling
1. The programme won't allow any modifications if the checkbox Enable edition is not checked.
2. Select the class with Class spinbox.
3. While holding down the left mouse button, move the mouse to create a rectangle, when you are satisfied with the label, release the button.
4. To save the labels visible on the image, press the Save button, use the keyboard shortcut "S" or go to the next image with the Save on change checkbox checked.
5. You can iterate over images by pressing the Next/Previous buttons or using the "A", "D" keyboard shortcuts.
6. To delete the label, click on the appropriate item in the scroll area.
7. To zoom, use the +/- buttons or scroll.

### Dataset validation
1. Click on the Validate dataset button.

### Class Modification
1. Click the Modify classes button.
2. The YAML Editor window will be displayed.
3. Modify class names and their numbers.
4. Click the Overwrite button.
5. Close the YAML Editor.

### Preparing the dataset for training
1. Select the desired proportions using the Training proportions spinboxes.
2. Click the Prepare for training button and select the destination folder.
3. The destination folder should preferably be empty.

### Using the YOLOv5 model to label an image
1. Click the Select model button.
2. Select the mode, the Average option will calculate average labels between detected and existing data, Overwrite will discard old labels in favour of detected ones.

### Copying/Pasting labels from image to image
1. Click on the Copy button or use the "C" keyboard shortcut.
2. Switch to the target image.
3. Click the paste button or use the "V" keyboard shortcut.

### Keyboard shortcuts
- A - Go to the next image
- D" - Go to the previous image
- "S" - Save the visible labels
- "C" - Copy the visible labels
- "V" - Paste the visible labels
- +" - Zoom in
- "_" - Zoom out
- esc" - Close the programme

## Disclaimer
1. The programme is still being tested and perfected.
2. At the moment, it only works with YOLOv5 datasets, there are plans to adapt the code to other dataset formats.
3. The application was created on Windows 10 OS, it may not be compatible with other operating systems.

## Contributing
All contributions and feedback are welcome! If you'd like to contribute to the project, please fork the repository, make your changes and submit a pull request.

## Licence
This project is licenced under the MIT License - see the LICENSE file for details. You are free to use, modify, and distribute this project for any purpose.
