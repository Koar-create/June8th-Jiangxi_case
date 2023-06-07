import os

def remove_duplicates(input_file, output_file):
    lines_seen = set()
    with open(output_file, 'w') as out_file:
        with open(input_file, 'r') as in_file:
            for line in in_file:
                if line not in lines_seen:
                    out_file.write(line)
                    lines_seen.add(line)

input_file = os.path.join(os.getcwd(), 'fnl_matthew.txt')
output_file = os.path.join(os.getcwd(), '1_fnl_matthew.txt')
remove_duplicates(input_file, output_file)