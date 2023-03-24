# MacOS Environment Variables Editor
A simple editor to edit, add, and remove environment variables in MacOS.

## Installation
1. Make sure you have Streamlit installed. If not, run `pip install streamlit`.
2. run `streamlit run main.py`

## How To Use

### Tables
The top select box shows options for different files that can be edited. MacOS loads environment variables from multiple different places. If you want to add an environment variable, the safest places to do so are in `.zshrc` and `.bash_profile`.

There are three tables below the selectbox. Exports are paths that are added to the PATH variable. 
The syntax in a bash file is `export PATH=$PATH:/path/to/thing`, and this is how all environment variables are added to PATH in macos.

Aliases are shell aliases that are set. An example is `alias python=python3.11`. Aliases allow the shell to access a command with a different name.

Sources are files that are sourced. An example is `source ~/.bash_profile`. This is how the shell loads other files, and many of these files are used to set environment variables. The environment variables from source are not displayed in this program.

### Adding, Editing, and Removing
To add a new environment variable, click the "Add" button. This will add a new row to the table. Type in the name and press the save button in the edit column.

To edit a row, click the "Edit" button. This will turn the text into a text input that allows you to edit the text. Press the save button to save the changes.

To delete a row, press the delete button. This will comment out the export, alias, or source in the file. This way no data is destroyed, and if you need to restore the variable, you can go into the file and uncomment it.