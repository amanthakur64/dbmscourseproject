import streamlit as st
import streamlit_lottie
import requests
from streamlit_lottie import st_lottie
import time
from PIL import Image
import pandas as pd
from io import StringIO
from itertools import combinations


st.set_page_config(page_title="Data Engineering Course Project", page_icon="computer",layout="centered")

def load_animation(url):
    r=requests.get(url)
    return r.json()

lottie_code= load_animation("https://assets7.lottiefiles.com/packages/lf20_7k8jk8vi.json")

# HEADER
st.subheader("This is our Data Engineering Course Project")
st.title("Auto Normalization of an RDBMS")


with st.container():
    st.write("---")
    left_column,right_column = st.columns(2)
    with left_column:
        st.header("How it Works")
        st.write('''We have implemented an end to end framework which takes a csv file, the attributes and the functional dependencies corresponding to that csv dataframe.
Once we obtain the data from the user we use the concepts learnt in our course Data Engineering/Database Management System to normalize the tables to 3NF using various techniques such as minimal cover,candidate keys resolution etc.

From the given set of functional dependencies we find out the candidate keys from which we can also get the set of prime and non prime attributes.Using the method of minimal cover and dependency preserving and the properties of each normal form we find out the conflicting functional dependencies and split into multiple tables as requires.We have continued this process since the resulting tables all have achieved 3NF.

We also have displayed the splitted tables in our frontend.

Risk Involved-We have tried to find out the functional dependencies given a dataframe only.This is risky as it leads to only finding out the potential functional dependencies.But we iterated through each entry of the database given to us and also used the concept learnt in the course to filter out the non redundant functional dependencies. ''')
    with right_column:
        st.write('##')
        st_lottie(lottie_code,height=300,width=400,quality='high',key="tree")


st.write("---")

with st.container():

    left_column,right_column = st.columns(2)
    with left_column:
        st.header("Uploads")
        st.write("Below are two file uploaders to upload your dataset and functional dependencies.")
        st.write("---")


    with right_column:
        lottie_code= load_animation("https://assets5.lottiefiles.com/packages/lf20_bewdaxyv.json")
        st_lottie(lottie_code,height=200,width=400,quality='high',key="survey")



uploaded_file = st.file_uploader("Please upload a csv file of your database",type=['csv'],key="csv")
if uploaded_file is not None:
  df = pd.read_csv(uploaded_file)
  st.write(df)
  number_of_columns = len(df.columns)
  alphabet_list = [chr(i) for i in range(65,65+number_of_columns)]


uploaded_file2 = st.file_uploader("Please upload a text file of the functional dependencies in the format: A->B \n C->D", type="txt",key="txt")  

st.write("---")

ok2 = st.button("See results")
if ok2:



# uploaded_file = st.file_uploader("Please upload a txt file containing the functional dependencies and attributes in the format of: A->B")
# if uploaded_file is not None:
#     # To read file as bytes:
#     stringio = StringIO(uploaded_file.getvalue().decode("utf-8"))

#     # To read file as string:
#     string_data = stringio.read()
#     st.write(string_data)
#     print(string_data) 

    st.write("---")


    post_synthesis = dict()
    canonical_list = []
    domkniecia = {}
    key_attributes = set()
    non_key_attributes = set()
    minimal_keys = set()
    super_keys = set()
    closure_string = ""
    base_min = []
    destroy_2PN = []
    destroy_3PN = []

    def combo(attributes):
        length = len(attributes)
        temp = []
        for i in range(length):
            if i == 0:
                for j in attributes:
                    temp.append(j)
            else:
                combs = combinations(attributes, i+1)
                for combo in combs:
                    combo = sorted(combo)
                    temp.append(','.join(combo))
        sorted_alphabetically = sorted(temp)
        sorted_len_alpha = sorted(sorted_alphabetically,key=len)
        return sorted_len_alpha


    # a function that returns a SET that is the complement of the given closure
    def closer(combination, relations):
        closing_set = set(combination)
        basic_length = len(closing_set)
        for relation in relations:
            set_attr = set(relation[0].split(","))
            if set_attr.issubset(closing_set):
                add = relation[1]
                closing_set.add(add)
                if len(closing_set) != basic_length:
                    return closer(closing_set, relations)
        return_set = sorted(closing_set)
        return return_set

    # function remembering all closures and determining all keys without division into min. candidate key and superkeys

    def keys_gen(attributes, relations):
        all_combinations = combo(attributes)
        all_closures = []
        all_keys = []
        for combination in all_combinations:
            to_close = combination.split(",")
            closure = closer(to_close, relations)
            # save all closures
            all_closures.append(closure)
            # recording of all keys (without division into minimum candidate keys and superkeys)
            if(len(closure) == len(attributes)):
                all_keys.append(combination)
        return all_keys

    # a function that determines the set of minimal candidate keys and superkeys from the set of all keys
    def extract_minimal(all_keys_set):
        global minimal_keys
        global super_keys
        temp_all = set(all_keys_set)
        i = 0
        for y in all_keys_set:
            i = i + 1
            for x in all_keys_set[i:]:
                subset_candidat = set(y.split(","))
                master_set = set(x.split(","))
                if(subset_candidat.issubset(master_set) and subset_candidat != master_set):
                    all_keys_set.remove(x)
        minimal_keys = sorted(set(all_keys_set))
        super_keys = sorted(sorted(temp_all.difference(minimal_keys)),key=len)

    # function to print all closures
    def list_closure(attributes, relations):
        # set of all closures

        global minimal_keys
        global super_keys
        global closure_string
        all_combinations = combo(attributes)
        print("[CLOSURES]")
        for combination in all_combinations:
            temp_attr = combination.split(',')
            closure = closer(temp_attr, canonical_list)
            closure_string = closure_string + "".join(closure)
            print('{' + combination.replace(",",", ") + '}+ = {' + ", ".join(closure).strip() + "}" , end="")
            if(combination in minimal_keys):
                print("          <----- MINIMUM CANDIDATE KEY")
            elif(combination in super_keys):
                print("          <----- SUPER KEY")
            else:
                print("")
            # check if closure is a key
        return key_attributes

    # a function that generates a string that is a combination of all closures - needed to verify whether the attribute can be removed

    def generate_closure_string(attributes, relations):
        closure_str = ""
        all_combinations = combo(attributes)
        for combination in all_combinations:
            temp_attr = combination.split(',')
            closure = closer(temp_attr, relations)
            closure_str= closure_str + "".join(closure)
        return closure_str

    # function to remove redundant attributes from the left side

    def delete(input_list):
        global canonical_list
        global attributes
        global base_min
        global closure_string
        default_relations = list(input_list)
        for x in input_list:
            defaultLeft = x[0].split(",")
            if(len(defaultLeft) > 1):
                for i in range(len(defaultLeft)):
                    if(len(x[0]) == 1):
                        break
                    defaultLeft = x[0].split(",")
                    defaultLeft.pop(i)
                    new_relation = [",".join(defaultLeft),x[1]]
                    temp_list = list(default_relations)
                    temp_list.remove(x)
                    temp_list.append(new_relation)
                    # I check if the attributes on the left side of the closure are the same after deleting, if so, it means that you can remove the attributes and try to remove the next one (recursively)
                    
                    if(closure_string == generate_closure_string(attributes, temp_list)):
                        for x in temp_list:
                            print(x[0] + " -> " + x[1])
                        base_min = list(temp_list)
                        return delete(temp_list)
            base_min = list(default_relations)
    # a function that removes redundant functional compounds - I try to remove each one in turn, if it does not affect the closures in any way, I remove

    def del_relations():
        global attributes
        global base_min
        global closure_string
        temp_relations = list(base_min)
        for x in base_min:
            if x in temp_relations:
                temp_relations.remove(x)
                generated_closure = generate_closure_string(attributes,temp_relations)
                if(closure_string == generated_closure):
                    base_min.remove(x)
                temp_relations = list(base_min)

    # auxiliary function for determining the minimum base
    def minimal_base(canonical_relations):
        global base_min
        global canonical_list
        # remove attributes from the left
        delete(canonical_relations)
        # usuwanie zbędnych zależności
        del_relations()
        # removing unnecessary dependencies
        b_set = set(tuple(x) for x in base_min)
        canonical_list = [list(x) for x in b_set if x[0] != x[1]]
        if(canonical_list):
            for x in sorted(sorted(canonical_list), key=len):
                print(x[0] + " -> " + x[1])
        else:
            print("brak")

    # padding for 2PN
    def closer2PN(subset):
        global destroy_2PN
        global non_key_attributes
        global base_min
        # given proper subset of key
        closing_set = set(subset)
        for relation in base_min:
            # left side of relation
            left_set = set(relation[0].split(","))

    # if the left side is a subset of the key i.e. it is its proper subset and the right side is not a key attribute then the dependency breaks 2PN
            if(left_set.issubset(closing_set) and relation[1] in non_key_attributes and left_set != closing_set):
                destroy_2PN.append(relation)

    # send each minimal key of the relation and check if the left side is a subset of the key, then if the right side is a non-key attribute

    def is2PN():
        global base_min
        global minimal_keys
        global destroy_2PN
        for key in minimal_keys:
            subsets = combo(key.split(","))
            for subset in subsets:
                closer2PN(subset.split(","))
        b_set = set(tuple(x) for x in destroy_2PN)
        destroy_2PN = [list(x) for x in b_set if x[0] != x[1]]
        if(destroy_2PN):
            return False
        else:
            return True

    # test for 3PN using the negation of the alternative ~(p or q or r)
    def is3PN():
        global base_min
        global key_attributes
        global super_keys
        global destroy_3PN
        for relation in base_min:
            left = relation[0].split(",")
            if (relation[1] not in left) and (relation[1] not in key_attributes) and (left not in super_keys):
                destroy_3PN.append(relation)
        b_set = set(tuple(x) for x in destroy_3PN)
        destroy_3PN = [list(x) for x in b_set if x[0] != x[1]]
        if(destroy_3PN):
            return False
        else:
            return True

    # function for determining and listing key and non-key attributes
    def attributes_specification():
        global minimal_keys
        global super_keys
        global non_key_attributes
        global key_attributes
        key_attrs = set()
        non_key_attrs = set()
        for x in minimal_keys:
            x = x.split(",")
            for y in x:
                key_attrs.add(y)
        key_attributes = sorted(key_attrs)
        print("Key attributes: ",end="")
        if(not len(key_attrs)):
            print("lack")
        else:
            print(", ".join(sorted(key_attrs)))
        non_key_attrs = sorted(attributes.difference(key_attrs))
        print("Non-key attributes: ",end="")
        if(not len(non_key_attrs)):
            print("lack")
        else:
            print(", ".join(sorted(non_key_attrs)))
        non_key_attributes = non_key_attrs

    # the function does not check if there is a scheme containing any of the keys and does not combine any of the keys - at the moment it only divides
    # schemes are stored in the dictionary as 'U': 'F', the right side is a set
    def synthesis_closure(uni_and_func):
        global post_synthesis
        final_closure = []
        final_relations = []
        keys = []
        move_relations = []
        for x in uni_and_func:
            closure = set(x.split(","))
            relations = set()
            # input dependency with the same attribute on the left
            for y in uni_and_func.values():
                # step over them and add to the closure
                for z in y:
                    if z[0] == x:
                        closure.add(z[1])
                        relation = z[0] + " -> " + z[1]
                        relations.add(relation)
            # print(post_synthesis)
            # add callbacks
            for y in uni_and_func.values():
                for z in y:
                    if z[1] == x:
                        if(set(z[0].split(",")).issubset(closure)):
                            relation = z[0] + ' -> '+ z[1]
                            relations.add(relation)
            # IMPORTANT CONTROL BECAUSE IT WAS OVERWRITING SOMETIMES
            if(",".join(sorted(closure)) in post_synthesis.keys()):
                move_relations = post_synthesis[",".join(sorted(closure))]
                move_relations = set(move_relations)
                for x in move_relations:
                    relations.add(x)
            post_synthesis[",".join(sorted(closure))] = relations
            #
            if(move_relations):
                post_synthesis[",".join(sorted(closure))] = relations
            # print(post_synthesis)

    # the function checks if there are schemes that are included in each other and if you need to add a scheme with U = key F = none
    def synthesis_final():
        global post_synthesis
        global minimal_keys
        key_in = False
        # print(post_synthesis)
        # check if the key is a member of any schema, if not add it
        for x in minimal_keys:
            x = set(x.split(","))
            for y in post_synthesis.keys():
                y = set(y.split(","))
                if(x.issubset(y)):
                    key_in = True
        if(not key_in):
            rand_key = minimal_keys[0]
            post_synthesis[rand_key] = "lack"
        # print(post_synthesis)
        # check if one schema is a subset of another
        for x in post_synthesis.keys():
            x_subset = set(x.split(","))
            for y in post_synthesis.keys():
                y_subset = set(y.split(","))
                if x_subset.issubset(y_subset) and x_subset != y_subset:
                    move_relations = post_synthesis[x]
                    post_synthesis[x] = ''
                    for z in move_relations:
                        post_synthesis[y].add(z)
                    break
        # print(post_synthesis)


    # print decomposition
    def synthesis(canonical_list,df):
        temp=[]
        # df = pd.read_csv("input.csv")
        global post_synthesis
        uni_and_func = dict()
        left_closures = set()
        for x in canonical_list:
            left_closures.add(x[0])
            uni_and_func[x[0]] = list()
        for x in canonical_list:
            if x[0] in uni_and_func.keys():
                uni_and_func[x[0]].append(x)
        synthesis_closure(uni_and_func)
        synthesis_final()
        i = 0
        for x in post_synthesis:
            if post_synthesis[x] != '':
                #print the table using create_table function
                attributes_table_list =  x.split(",")
                index = [ord(i)-65 for i in attributes_table_list]
                temp.append(create_table(df, index))
                temp.append("R" + str(i) + " = " + "(" + " U" + str(i) + " = " + "{" + x + "}, F" + str(i) + " = " + str(post_synthesis[x]) + " )")
                i = i + 1
        return temp

    #Import the module which have tabulate function
    from tabulate import tabulate

    def create_table(df, index):
        #print the table and beautify it
        #get the list of the attributes from the index
        attributes_total = list(df.columns)
        table_attributes = [attributes_total[i] for i in index]
        df = df[table_attributes]
        #remove the duplicate rows and make the table
        df = df.drop_duplicates()
        #remove the index column
        df = df.reset_index(drop=True)
        return(tabulate(df,headers=table_attributes,tablefmt="grid"))



    relation_set = set()
    attributes = set()
    post_synthesis = dict()
    canonical_list = []
    domkniecia = {}
    key_attributes = set()
    non_key_attributes = set()
    minimal_keys = set()
    super_keys = set()
    closure_string = ""
    base_min = []
    destroy_2PN = []
    destroy_3PN = []



    #read the csv file

    #get the number of columns 
    number_of_columns = len(df.columns)
    alphabet_list = [chr(i) for i in range(65,65+number_of_columns)]

    print("The attributes are: " + ", ".join(alphabet_list))

    print("Action: ")
    print("1 - entering attributes and relationships manually")
    print("2 - loading attributes and relationships from the file")
    print("Type any other character to exit")
    option = '1'

    if(option == '1'):
        print("Enter the attributes in one line, separating only with a comma.")
        print("Enter each functional dependency on a separate line. After entering all of them, also on a separate line, enter END to continue.")
        # load attributes
        # input_attributes = input("Attributes: ").split(",")
        attributes = set(alphabet_list)
        # load functional dependencies

        print("When entering functional dependencies, keep the format: attributes/y -> attributes/y, i.e. A,B -> D,C")
        print("Functional dependencies: ")
        # line = ""
        # while(line != "END"):
        #     line = input()
        #     if(line != "END"):
        #         relation_set.add(line)
        #read the inputs from the text file


        #read the text file
    
                


      
        if uploaded_file2 is not None:
            stringio = StringIO(uploaded_file2.getvalue().decode("utf-8"))

        # To read file as string:
        string_data = stringio.read()
        st.write(string_data)
        print(string_data)
        
        buffer = []
        for line in string_data:
            buffer.append(line)
        for i in range(len(buffer)):
            new_line = ""
            if buffer[i] == ">":
                # print("hi")
                new_line = buffer[i-2] + buffer[i-1] + buffer[i] + buffer[i+1]
                relation_set.add(new_line)
            # if(line != "END"):
            #     new_line = ""
            #     for op in range(len(line)):
            #         if(line[op] == '-'):
            #             print("here")
            #             print(line)
            #             print(op, line[op-1], line[op+2])
            #             new_line = new_line + line[op-1]+'->'+line[op+2]

            #     relation_set.add(new_line)

        # with open("dbmstest.txt") as f:
        #     for line in f:
        #         if(line != "END"):
        #             line = line.rstrip()
        #             relation_set.add(line)

        #print the relations
        # print("Relations: ")
        # for x in relation_set:
        #     print(x)


        
    elif(option == '2'):
        print("Select basic tests by entering a number from 01-10 (with a leading zero).")
        print("If you want to load your own test from a file, create a file in the folder with basic tests and name it and fill it in with the visible convention.")
        test_number = input("test number:")
        # support for reading from file
        path = "testy/test-" + test_number + ".txt"
        test = open(path, "r")
        attributesLine = test.readline().split(',')
        # reads the attributes into the file - remove any duplicates immediately
        for x in attributesLine:
            attributes.add(x.strip())
        # loads functional dependencies into the set - remove any duplicates immediately
        for x in test:
            x = x.rstrip()
            relation_set.add(x)
    else:
        pass


    st.header("Normalized Databases are:")
    st.write('Below are the Normalized Databases')    
    # end setup #
    # attributes and functional dependencies are already loaded, the next step is to check the correctness of the loaded data, if the verification of inclusions F in U and U in F is not successful, the program will fail
    print("--------------------------------------------------------------------------------------------------------------------------------")
    print("[ANALYSIS - START]")
    print("Attributes: " + ','.join(sorted(attributes)))
    print("Functional dependencies: ")
    for x in sorted(relation_set):
        print(x)

    relations_dict = {}
    canonical_base = {}


    # load the dependency into the dictionary, left is the key - right is the set, then
    #A,B -> C
    #A,B -> D
    # in the dictionary this will be the key A,B: ['C','D'] (as set) on the right
    for relation in relation_set:
        left = relation.rsplit('-')[0].strip()
        del_repeat = sorted(set(left.split(",")))
        left = ",".join(del_repeat)
        canonical_base[left] = set()

    for relation in relation_set:
        left = relation.rsplit('-')[0].strip()
        right = relation.rsplit('>')[1].strip()

        del_repeat = sorted(set(left.split(",")))
        left = ",".join(del_repeat)

        relations_dict[left] = right

        # exploding e.g. A -> B,C into A -> B; A -> C

        rightAttributes = right.split(",")
        for i in rightAttributes:
            canonical_base[left].add(i.strip())

    # after loading everything into the dictionary, I am sure that I don't have duplicates anymore, I can go to the list and from it to the canonical form
    canonical_list = []
    for i in canonical_base:
        right_values = canonical_base[i]
        for j in right_values:
            canonical_list.append([i, j])

    print("")
    print("[VERIFICATION]")
    fun_F = set()
    # here can be on the left e.g. A,B,C,D -> E therefore split()
    for x in canonical_base:
        attr_in_F = x.split(",")
        for y in attr_in_F:
            fun_F.add(y)

    for x in canonical_base.values():
        attr_in_F = x
        for y in attr_in_F:
            fun_F.add(y)

    print("Attributes with U: " + ", ".join(sorted(attributes)))
    print("Attributes from F: " + ", ".join(sorted(fun_F)))

    # VERIFYING THE CORRECTNESS OF INPUT DATA
    if(attributes.issubset(fun_F) == False):
        print("There is at least one attribute in U that is not in F. Adds a trivial dependency.")
        for x in attributes:
            if x not in fun_F:
                print(x + " -> " + x)
        print("--------------------------------------------------------------------------------------------------------------------------------")
    if (fun_F.issubset(attributes) == False):
        print("There is at least one attribute in F that is not in U. Verification failed.")
        print("--------------------------------------------------------------------------------------------------------------------------------")
    else:
        print("The attributes in F and U match. Verification successful.")
        print("")
        # remember all keys - no division
        all_keys = keys_gen(attributes, canonical_list)
        # extract minimal candidate keys
        extract_minimal(all_keys)
        # print closures
        key_attributes = sorted(list_closure(attributes, canonical_base))
        # list attributes broken down into key and non-key
        print("")
        print("[DETERMINATION OF ATTRIBUTES]")
        attributes_specification()
        print("")
        print("[MINIMUM BASE]")
        minimal_base(canonical_list)
        print("")
        print("[TEST ON 2PN]")
        if(not is2PN()):
            print("""The relation is not in 2 normal form.
    For a relation to be in 2PN, it is necessary that each non-key attribute is fully functionally dependent on each key of that relation.
    In the given scheme, there is more pleasantly one partial functional dependency that violates 2PN.
    These dependencies are:""")
            for x in destroy_2PN:
                print(x[0] + " -> " + x[1])
        else:
            print("The relation is in 2 normal form.")
        if(not is3PN()):
            print("")
            print("For a relation to be in 3PN, it is necessary that, in addition to being in 2PN, each of its functional dependencies X -> Y has one of the following properties:")
            print("""
    (1) the relationship is trivial (Y is contained in X) or
    (2) X is a superkey or
    (3) Y is a key attribute
                """)
            print("[TEST ON 3PN]")
            print("The relation is not in 3 normal form. Dependencies that do not meet any of the above conditions are: ")
            for x in destroy_3PN:
                print(x[0] + " -> " + x[1])
            print("")
            print("[DECOMPOSITION BY SYNTHESIS]")

            
            for i in synthesis(canonical_list, df):
                print(i)
        

            for i in synthesis(canonical_list, df):
                st.text(i)
                st.write("---")
        

            print("--------------------------------------------------------------------------------------------------------------------------------")
        else:
            print("The relation is in 3 normal form.")
            print("--------------------------------------------------------------------------------------------------------------------------------")

