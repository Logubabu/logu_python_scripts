import os

def get_file_names(directory):
    file_names = []
    serial_no = 1
    for root, dirs, files in os.walk(directory):
        for file in files:
            file_names.append(f"{serial_no:03}.   {os.path.join(file)}")
            serial_no += 1
    return file_names

def save_to_txt(file_names, output_file):
    with open(output_file, 'w') as f:
        for file_name in file_names:
            f.write(file_name + '\n')

if __name__ == "__main__":
    directory = "D:/278-Babu-Pavithra(Wedding) Selected Files/Part 2"
    # output_file = input("Enter the name of the output file: ")

    file_names = get_file_names(directory)
    save_to_txt(file_names, "part 2.txt")

    print(f"All file names with serial numbers have been saved to part 1 successfully.")
