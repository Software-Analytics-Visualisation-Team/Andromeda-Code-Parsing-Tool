import os
import sys
import shutil

from rdf_creation import get_rdf
from supported_language import SupportedLanguage, supported_languages

INPUT_FOLDER_PATH = os.path.abspath('./input/')

def get_files_for_language(directory_or_zip_path: str, language: SupportedLanguage) -> list[str]:
    """Returns a list of the file paths of files of language [language] in the archive or directory.

    Args:
        path (str): Path to the archive to be extracted or directory to be scanned.
        language (SupportedLanguage): Language to filter files.

    Returns:
        list[str]: List of file paths extracted from the archive or directory.
    """
    # Initialize files list
    files = []
    
    # Remove old input folder
    if os.path.exists(INPUT_FOLDER_PATH):
        shutil.rmtree(INPUT_FOLDER_PATH)
    # Check if the path is correct:
    if not os.path.exists(directory_or_zip_path):
        raise Exception(f"Provided path does not exist: {directory_or_zip_path}")
    # Check if path is a directory
    elif os.path.isdir(directory_or_zip_path):
        # Copy the files from the directory to INPUT_FOLDER_PATH
        shutil.copytree(directory_or_zip_path, INPUT_FOLDER_PATH)
    else:
        # Path is a file, assume it's a zip file and extract it
        shutil.unpack_archive(directory_or_zip_path, INPUT_FOLDER_PATH, "zip")
    
    # Walk through the directory structure
    for root, dirs, filenames in os.walk(INPUT_FOLDER_PATH):
        for filename in filenames:
            # Check if file extension matches the language
            if filename.split('.')[-1] in language.file_extensions:
                # Create a File object and add it to the list
                file_path = os.path.join(root, filename)
                files.append(file_path)
    
    return files

def main(argv):
    """Function that should be executed first.

    Args:
        argv (list[type]]): List of the provided CLI arguments.
    """

    if len(argv) != 3:
        raise Exception(f"Bad CLI arguments were provided. Usage: {argv[0]} <input_directory_or_zip_path> <output_file_path>")
    
    input_directory_or_zip_path, output_file_path = argv[1:3]

    # List of rdfs for each language.
    rdfs = []

    for language in supported_languages:
        # Retrieve files for the chosen language
        files = get_files_for_language(input_directory_or_zip_path, language)
        
        # Check that files were found.
        if not files:
            print(f"No files found for {language.name}.")
            continue

        # Generate RDF specified by retrieved files in the given language
        rdf = get_rdf(INPUT_FOLDER_PATH, files, language)
        rdfs.append(rdf) 

    # Check that rdfs were generated.
    if not rdfs:
        # Ths is very scuffed, but it will do for now. rdflib does not support empty graphs that contains the SEON line at the top.
        with open(output_file_path, 'w') as f:
            f.write(
"""<?xml version="1.0" encoding="utf-8"?>
<rdf:RDF
   xmlns:SEON_code="http://se-on.org/ontologies/domain-specific/2012/02/code.owl#"
   xmlns:ns1="http://definitions.moonshot.sep/_#"
   xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
>
</rdf:RDF>""")
        return

    # Merge all the rdfs into one.
    combined_rdf = rdfs[0]
    for i in range(1, len(rdfs)):
        combined_rdf += rdfs[i]
        
    # Export RDF.
    combined_rdf.serialize(destination=output_file_path, format='xml')

if __name__ == "__main__":
    print("Running OWL-creation tool.")
    main(sys.argv)
