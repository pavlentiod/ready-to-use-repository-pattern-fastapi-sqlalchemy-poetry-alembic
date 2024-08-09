#!/bin/sh

# Move all files from the current directory to the parent directory
mv * ..

# Remove the directory named after the project name (assumes cookiecutter syntax is replaced)
rm -rfv ../"{{ cookiecutter.module_name }}"
# Function to prompt for entities
get_entities() {
    echo "Enter entity names separated by space: "
    read -r entities
}

# Function to run the Python script with the entities
run_python_script() {
    python create_entities.py $entities
}

# Main script execution
get_entities
run_python_script

pip install poetry

cd basicpythonproject/src || exit

poetry install

