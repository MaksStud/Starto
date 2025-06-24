# Run programs in groups

## Inventory
This program allows you to create groups of programs and launch all the programs in the group simultaneously at the touch of a button. Ideal for automating your work: for example, you can create a Work group with your favorite browser, code editor, and messenger and run everything together.

## Features
* Create and edit program groups
* Add any program from your computer to the group
* Launch all programs in the selected group with one button
* Easy and intuitive interface

## Technologies
* **Python** (backend)
* **SQLite** (saving groups and programs)
* **PyWebview** (graphical interface)
* **HTML / CSS / JS** (frontend)

## Installation

1. Mount the repository:

``` bash
git clone https://github.com/MaksStud/Starto.git
```
``` bash
cd project-name
```

2. Install the dependencies:
```bash
pip install -r requirements.txt
```

3. Run the program:
```bash
python main.py
```

Or build the `.exe' via **PyInstaller**:
```bash
pyinstaller --name "Starto" --onefile --noconsole --icon=list.ico --add-data "pages;pages" --add-data "db.py;." --add-data "settings.py;." --add-data "StartoProgramData.sqlite3;." main.py
```

Or download a ready-made assembly
* [Starto.exe for Windows](https://github.com/MaksStud/Starto/releases/download/v1.0.1/Starto.exe)

## How to use

1. Create a new group
2. Add programs to the group (selecting `.exe' files)
3. Click the **Start Group** button - all programs from the group will open

## Example of use.

* **Workgroup**: VSCode, Chrome, Telegram
* **Game group**: Steam, Discord, MSI Afterburner
