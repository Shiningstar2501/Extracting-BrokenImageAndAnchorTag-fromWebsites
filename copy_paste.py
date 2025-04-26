def append_file(source_files):
    try :
        with open ("_a_tag_issue.txt", 'w') as dest :
            for files in  source_files :
                try:
                    with open (files , 'r') as src:
                        content = src.read

                        dest.write(f"-------Starting the {files}----")
                        dest.write(content)
                        dest.write(f"--------Ending--------------")
                    print(f"Appended {files}")
                except FileNotFoundError:
                    print(f"WARNING --- {files} not found. Skipping")
    except  Exception as e:
        print(f"An error occured while opening the destination file")



## Driver code 
source_file = []
