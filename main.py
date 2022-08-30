import requests
import pandas as pd

#Import the names of surgeons from the CSV file
#CSV file should have Contact ID,First,Last Name,Work State/Province as the 4 columns on top
df = pd.read_csv('data/no_npi_double_part2.csv')

#Create new dataframe to save name and npi
column_names = ["ContactID", "Firstname", "Lastname", "NPI", "Specialty", "Gender"]
df_npi = pd.DataFrame(columns=column_names)

for i, row in df.iterrows():
    contact_id = row[0] #Saleforce ID

    fname = row[1].split()[0] #First name
    #fname = fname.split()[0] #Saves just first name, excludes middle initial/names
    print("!!!!!", fname)

    lname = row[2] #Last name
    st = row[3] # State code 2-digit

    NPI_EndPoint = "https://npiregistry.cms.hhs.gov/api/?"

    parameters = {
        "first_name": fname,
        "last_name": lname,
        "version": 2.1,
    }
    response = requests.get(url=NPI_EndPoint, params=parameters)
    data = response.json()

    try:
        result_count = data["result_count"]
    except KeyError as keyerror:
        print("Trouble finding results")
        print(keyerror)
        continue


    if result_count == 0:
        print(f"**No NPI available for {fname} {lname}")

    item = 0
    while item < result_count:
        try:
            specialty1 = data["results"][item]["taxonomies"][0]["desc"]
            specialty2 = data["results"][item]["taxonomies"][1]["desc"]
        except IndexError as i_error:
            print(i_error)
        else:
            if specialty1 == "Neurological Surgery" or specialty2 == "Neurological Surgery":
                first_name = data["results"][item]["basic"]["first_name"].capitalize()
                last_name = data["results"][item]["basic"]["last_name"].capitalize()
                gender = data["results"][item]["basic"]["gender"]

                if gender == 'M':
                    gender = "Male"
                elif gender == 'F':
                    gender = "Female"

                state = data["results"][item]["addresses"][0]["state"]
                subspecialty = data["results"][item]["taxonomies"][0]["desc"]
                npi_number = data["results"][item]["number"]
                #print(f"{first_name}, {last_name}, {gender}, {state}, {subspecialty}")
                new_row = {'ContactID': contact_id,
                           'Firstname': first_name,
                           'Lastname': last_name,
                           'NPI': npi_number, #need to pull out of json still
                           'Specialty': subspecialty,
                           'Gender': gender,
                           }
                df_npi = df_npi.append(new_row, ignore_index=True)
            else:
                print(data["results"][item]["basic"]["first_name"].capitalize(), data["results"][item]["basic"]["last_name"].capitalize(), data["results"][item]["taxonomies"][0]["desc"])
                pass
                #print(f"Not a match for item {item}")
                #print(data["results"][item]["taxonomies"][0]["desc"])
        item += 1

df_npi.to_csv('data/npi_list.csv')
