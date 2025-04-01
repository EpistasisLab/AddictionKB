# This script parses NCBI human gene data and Bgee epxression data 

my_set = set()

def processLargeTextFile(source, compare_index, separator):
    # count to see how many lines are added to the set
    count = 0
    with open(source, "r") as r:
        for line in r:
            columns = line.split(separator)
            my_set.add(columns[compare_index].replace('Ensembl:', '') )
            count += 1
    print("Length from processLargeTextFile: ", count)
    r.close()

def keepDesiredColums(row, keep_index, separator):
    columns = row.split(separator)

    output_str = []
    for index in keep_index:
        output_str.append(columns[index])

    return separator.join(output_str)

def filterLargeTextFile(source, destination, delimiter, keep_index):
    with open(source, "r") as r, open(destination, "w") as w:
        #load header row
        w.write(keepDesiredColums(r.readline(), keep_index, delimiter) + '\n')

        #load body
        count = 0
        for line in r:
            if line is not None:
                count += 1
                w.write(keepDesiredColums(line, keep_index, delimiter) + '\n')
        print("Length from filterLargeTextFile: ", count)
    r.close(), w.close()

def fileIndexFinder(source, destination, keep_set, compare_column_index, separator):
    count_rows =0
    with open(source, "r") as r, open(destination, "w") as w:
        w.write('Ensembl' + separator +  r.readline())

        for line in r:
            columns = line.split(separator)
            parsed_column = columns[compare_column_index]
            print("Parsed column before splitting or processing: ", parsed_column)

            if '|' in parsed_column:
                parsed_column_split = parsed_column.split('|')
                if len(parsed_column_split) > 2:
                    parsed_column = parsed_column_split[2].replace('Ensembl:', '')
                    #print("Parsed column: ", parsed_column)

            if parsed_column in keep_set: # remov ethe if condition if you want to follow AlzKB conventions
                count_rows +=1
                w.write(parsed_column + separator + line)
    print("Length from fileIndexFinder: ", count_rows)
    r.close()



brain_file='Path to file Homo_sapiens_expr_advanced.tsv' #https://bgee.org/?page=download&action=expr_calls#id1
gene_file='Path to file Homo_sapiens.gene_info' #https://ftp.ncbi.nlm.nih.gov/gene/DATA/GENE_INFO/Mammalia/Homo_sapiens.gene_info.gz

gene_dest_file='Path to save Homo_sapiens.gene_info_filtered'

final_out='Path to save output.tsv'

delimiter = '\t'
keep_index = [1,2,4,5,6,8,9]
compare_index = 0

processLargeTextFile(brain_file, compare_index, delimiter)

filterLargeTextFile(gene_file, gene_dest_file, delimiter, keep_index)

print("Length of my_set: ", len(my_set))

fileIndexFinder(gene_dest_file, final_out, my_set, 3,  delimiter)
