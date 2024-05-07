#!/bin/bash

# Navigate to the resources directory
echo "Start packaging for Lambda functions"
cd ../bedrock_rag_opensearch/resources

# Create a temporary directory for storing installed packages
mkdir temp_libs

# Loop through each sub-folder in the resources directory
for folder in */; 
do
    # Check if the folder name contains 'function'
    if [[ "$folder" == *"function"* ]]; then
        # Enter the sub-folder
        cd "$folder"
        folder_name=${folder%/}
        if [ -f requirements.txt ]; then
            echo "Installing packages for $folder"
            pip install -r requirements.txt --target="../temp_libs"
            cp -a . ../temp_libs
            cd ../temp_libs
            echo "Zipping the resources folder..."
            zip -r "${folder_name}.zip" *
            mv "${folder_name}.zip" ../
            cd ..
        fi
    fi
 
    echo "Emptying the temp folder"
    rm -rf temp_libs/*
done

echo "Cleaning up temporary files..."
rm -rf temp_libs/


