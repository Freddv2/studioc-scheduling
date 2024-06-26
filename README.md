# Studio C Student-Teacher Assignment Tool

## Prerequisites
1. **Python**: Make sure Python is installed on your system. You can download it from the [official Python website](https://www.python.org/downloads/).
2. **Libraries**: The scripts require certain Python libraries like Pandas. You can install them using the following command in the terminal or command prompt:
   ```bash
   pip install pandas colorama pyfiglet
   ```

## How to Use
1. **Download the Scripts**: Make sure all four Python scripts (`students_cleanup.py`, `teachers_cleanup.py`, `formatter.py`, `main.py`) are in the same folder on your computer.
2. **Prepare the Input Files**: You'll need two CSV files: one with student information and the other with teacher information. Place them in the same folder as the scripts.
3. **Open the Terminal or Command Prompt**: On Windows, you can search for "cmd" in the Start menu. On Mac, you can find the Terminal in Applications > Utilities.
4. **Navigate to the Folder**: Use the `cd` command to navigate to the folder containing the scripts. For example:
   ```bash
   cd path/to/your/folder
   ```
   Replace `path/to/your/folder` with the actual path to the folder containing the scripts.
5. **Run the Command**: Copy and paste the following command into the terminal, replacing the filenames with your actual file names:
   ```bash
   python students_cleanup.py --input students_input.csv --output students.csv && python teachers_cleanup.py --input teachers_input.csv --output teachers.csv && python main.py --students_file students.csv --teachers_file teachers.csv
   ```

## Troubleshooting
- If you encounter any errors related to permissions, you might need to run the command prompt or terminal as an administrator.
- If Python is not recognized as a command, make sure that Python is installed correctly and that the path to the Python executable is included in your system's PATH environment variable.
