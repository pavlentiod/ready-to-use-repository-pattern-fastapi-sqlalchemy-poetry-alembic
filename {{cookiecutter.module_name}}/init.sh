#!/bin/sh

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

