import os

def rename_files_in_folder(folder_path):
    substrings_to_remove = [
        "www.TamilPrintTV.COM - Tamilprint - ",
        "www.TamilPrintTV.com - TamilPrint - ",
        "Moviesda.Mobi_-_",
        "Moviesda.Mobi - ",
    ]

    try:
        # Iterate through all files in the folder
        for filename in os.listdir(folder_path):

            # Replace each substring in the filename
            for substring in substrings_to_remove:
                new_name = filename.replace(substring, "")

            # Only rename if the new name is different
            if new_name != filename:
                old_filepath = os.path.join(folder_path, filename)
                new_filepath = os.path.join(folder_path, new_name)
                os.rename(old_filepath, new_filepath)
                print(f"File '{filename}' renamed to '{new_name}'.")
            else:
                print(f"File '{filename}' does not need renaming.")

    except FileNotFoundError:
        print(f"Error: Folder '{folder_path}' not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    folder_path = "D:/Movies"
    rename_files_in_folder(folder_path)
