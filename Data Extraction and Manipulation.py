import pandas as pd 
import numpy as np 
import math
from bs4 import BeautifulSoup
import requests
import re
import time


#Extracting the details of each of the relevent sessions (required for data extraction)

url = "https://api.openf1.org/v1/sessions"
page = requests.get(url)
soup = BeautifulSoup(page.content, "html.parser")
    #Extracting the webpage with the session information

soup = str(soup)

content = soup.split("}")

practice_sessions = []

session_names = []
circuit_keys = []
circuit_names = []
years = []
session_keys = []
meeting_keys = []

for i in practice_sessions:
    try: 
        session_names.append(re.search(r'"session_name":"([^"]+)"', i)[1])
    except:
        print("{} has no session name".format(i))

    try:
        circuit_keys.append(re.search(r'"circuit_key":(\d+)', i)[1])
    except:
        print("{} has no circuit key".format(i)) 

    try: 
        circuit_names.append(re.search(r'"circuit_short_name":"([^"]+)"', i)[1])
    except:
        print("{} has no circuit name".format(i))

    try: 
        years.append(re.search(r'"year":(\d+)', i)[1])
    except:
        print("{} has no year".format(i))

    try: 
        session_keys.append(re.search(r'"session_key":(\d+)', i)[1])
    except:
        print("{} has no session key".format(i))

    #INcluding meetiing key data 
    try: 
        meeting_keys.append(re.search(r'"meeting_key":(\d+)', i)[1])
    except:
        print("{} has no session key".format(i))
#Extracts all of the relevent session information from the text

practice_data = pd.DataFrame({"Year": years, 
                             "Circuit": circuit_names, 
                             "Cicruit Key": circuit_keys, 
                             "Session Name":session_names, 
                              "Meeting Key": meeting_keys,
                             "Session Key":session_keys})

practice_data.to_csv("./data/practcie session data.csv", index = False, encoding = "utf-8")



#Extracting the timing data from each of the sessions

data = pd.read_csv("./data/practcie session data.csv")
data = data.drop([0,1,2,116,117,118, 12, 31, 44, 45, 49, 68, 69, 82, 104, 112, 108])
    #Removing sprint weekends 


global_dict = {}
track_data = {}
driver_nos = set()

session_keys = np.array(data.loc[:, "Session Key"])
count = 0
    #This is to count the current iteration of the for loop

for i in session_keys:
    ###Getting the Driver TIme Data
            #Gets it for each session_key
    url = "https://api.openf1.org/v1/laps?session_key={}".format(i)

    page = requests.get(url)

    soup = BeautifulSoup(page.content, "html.parser")
    
    soup = str(soup)
    
    soup = soup.split("}")
    
    non_out_laps = [i for i in soup if "true" not in i]
        #The only time T/F is mentioned is with out laps 
    
    non_out_laps = non_out_laps[:-1]
        #Removing row of "]"
    
    driver_times = {}

    ### Finding the driver lap times 
        #Stroing in dictionary driver_times
    for i in non_out_laps:
        try:
            driver_number = re.search(r'"driver_number":(\d+)', i)[1]
            driver_nos.add(driver_number)
            lap_time = float(re.search(r'"lap_duration":(\d+(\.\d+)?)', i)[1])
            
            if driver_number not in driver_times:
                driver_times[driver_number] = [lap_time]
        
            else: 
                driver_times[driver_number].append(lap_time)
    
        except:
            #print("Error at {}".format(i))
            continue

    if len(driver_times) == 0:
        print("An error occured in session {}".format(i))
        print("URL: {}".format(url))
        print()
        break
        
    time.sleep(1)
        #Preventing breaking the servers

    ###Assigning the driver_times to meeting key and session name 
        #Using count to extract the values '
    session_name = data.iloc[count]["Session Name"]
    
    track_data[session_name] = driver_times
        #Saving the driver times in track data 

    if (count + 1) % 3 == 0:
            #If all 3 practice sessions have been extracted 
        meeting_key = data.iloc[count]["Meeting Key"]
        global_dict[meeting_key] = track_data
        
        track_data = {}
            #This resets the dictionary if session name appears again
            #At this point is when you have a full track_data (w P1,P2, and P3 data)
                #-> you want to assign this to global (with the session name)
    print(count)
    count += 1

data_1 = []

for race, sessions in global_dict.items():
    for driver_no in driver_nos:
        row = {"Race": race, "Driver Number": driver_no}
        for session, driver_number in sessions.items():
            row[session] = driver_number.get(driver_no, None)
        data_1.append(row)

df = pd.DataFrame(data_1)
df = df[["Race", "Driver Number", "Practice 1", "Practice 2", "Practice 3"]]
    #Saving the dictionary as a dataframe 


df.to_csv("./data/Corrected Time Data V2.csv", index = False, encoding = "utf-8")


###Generating Labels:
    #These were extracted from https://github.com/f1db/f1db

data =pd.read_csv("./data/Corrected Time Data V2.csv")
practice_details = pd.read_csv("./data/practcie session data.csv")

practice_details = practice_details.drop([0,1,2,116,117,118, 12, 31, 44, 45, 49, 68, 69, 82, 104, 112, 108])

quali_files = {}

for key in meet_keys:
    link = "./data/quali data/meet_{}.yml".format(key)
        #Iterating over every file
    with open(link, "r") as file:
        dat = yaml.safe_load(file)

    quali_files["meet_{}".format(key)] = dat
#I had previously saved all of the qualifying result data from the githib

def extract_result(row):
    race_id = row["Race"]
    driver_id = row["Driver Number"]

    result = list(filter(lambda entry: entry['driverNumber'] == driver_id, quali_files["meet_{}".format(race_id)]))

    try:
        result = str(result)
        print(result)
    
        position = re.search(r"'position': (\d+)", result)[1]
    
        print(position)
    
        return position

    except:
        return None
#Function to extract the result 

data["Qualifying Results"] = data.apply(extract_result, axis = 1)
#Applying the function to the  data 

data.to_csv("./data/labelled data V2.csv", index = False, encoding = "utf-8")



###Data Manipulation:
    #In this section I manipulated the data I had previously extracted 
    #Removing outliers and standardising 

data = pd.read_csv("./data/labelled data V2.csv")
data = data.dropna(subset = ["Qualifying Results"])
    #This only keeps the drivers that completed the qualifying session

def string_to_array(row):
    try:
        numpy_row = np.array(ast.literal_eval(row))
        return numpy_row

    except: 
        print(row)
        print(type(row))
        return 
#As I saved my data in a csv format I had to convert the data to an array

data["Practice 1"] = data["Practice 1"].apply(string_to_array)
data["Practice 2"] = data["Practice 2"].apply(string_to_array)
data["Practice 3"] = data["Practice 3"].apply(string_to_array)


sessions = ["Practice 1", "Practice 2", "Practice 3"]

total_session_times = {}

for i in data["Race"].unique():
        #This is how I can iterate over each of the individual race numbers 
    for session in sessions:
        #How I will select the specific session
        cut_data = data[data["Race"] == i][session]
            #Subsetting the data 

        cut_data = cut_data.dropna()
            #This will remove rows with no data
        
        if len(cut_data) == 0:
            #This is when an error has cocured and the data has not generated properly 
            total_session_times["{}_{}".format(i, session)] = None 
            continue
        
        combined_cut = np.concatenate(cut_data.values)
            #Combines all of the lap times in the subset

        total_session_times["{}_{}".format(i, session)] = combined_cut
    #This combines all of the drivers times for each session
    #So that I can generate outliers 

total_session_summary_stats = {}

for key, value in total_session_times.items():
    if value is None:
        total_session_summary_stats[key] = None
        continue
    
    total_session_summary_stats[key] = [np.mean(value), np.std(value)]
    #Generating the required statistics from these times 




def remove_extreme(row):
    race_id = row[0]
    
    try:
        mean = total_session_summary_stats["{}_{}".format(race_id, session_name)][0]
        std = total_session_summary_stats["{}_{}".format(race_id, session_name)][1]
            #If these are not found it means that there are no lap times for the specific session
            #-> if not found -> skip
    except: 
        print("No data for {} in race {}".format(session_name, race_id))
        return None
    

    if row[1] is None:
                #Skipping past those witgh no entries 
        return None

    non_out_times = []
        #This is to store the non outliers 
    
    for time in row[1]:
            #This iterates over every time value in the row 
        z_score = (time - mean) / std

        if z_score > 2:
                #When it is an outlier (only for high values)
                #2 was chosen as an arbitrary value 
                    #This should be revisited in the future 
            print("Mean: {}".format(mean))
            print(time)
            print()

        else:
                #If not an outlier -> save time 
            non_out_times.append(time)

    return np.array(non_out_times)
        #Returns the array of non outlier times 
        
    
out_removed_data = data

session_name = "Practice 1"
out_removed_data["Practice 1"] = out_removed_data[["Race", "Practice 1"]].apply(remove_extreme, axis = 1)

session_name = "Practice 2"
out_removed_data["Practice 2"] = out_removed_data[["Race", "Practice 2"]].apply(remove_extreme, axis = 1)

session_name = "Practice 3"
out_removed_data["Practice 3"] = out_removed_data[["Race", "Practice 3"]].apply(remove_extreme, axis = 1)

#Making a function to remove outliers,a nd applying it 
        

###Standardising the timing data 

sessions = ["Practice 1", "Practice 2", "Practice 3"]

out_removed_session_times = {}

for i in out_removed_data["Race"].unique(): 
    for session in sessions:
        
        cut_data = out_removed_data[out_removed_data["Race"] == i][session]
        cut_data = cut_data.dropna()
        
        
        if len(cut_data) == 0:
            #This is when an error has cocured and the data has not generated properly 
            out_removed_session_times["{}_{}".format(i, session)] = None 
            continue
        
        combined_cut = np.concatenate(cut_data.values)
            #Combines all of the lap times in the subset

        out_removed_session_times["{}_{}".format(i, session)] = combined_cut

out_removed_summary_stats = {}

for key, value in out_removed_session_times.items():
    if value is None:
        out_removed_summary_stats[key] = None
        continue
    
    out_removed_summary_stats[key] = [np.mean(value), np.std(value)]


def standardise(row):
    race_id = row[0]

    try:
        mean = out_removed_summary_stats["{}_{}".format(race_id, session_name)][0]
        std = out_removed_summary_stats["{}_{}".format(race_id, session_name)][1]
            #If these are not found it means that there are no lap times for the specific session
            #-> if not found -> skip
    except: 
        print("No data for {} in race {}".format(session_name, race_id))
        return None

    stan_times = []

    if row[1] is None:
        return None
    
    for time in row[1]:
        stan_value = (time - mean) / std
        stan_times.append(stan_value)

    return np.array(stan_times)
    
stan_data = out_removed_data.copy()

session_name = "Practice 1"
stan_data["Practice 1"] = stan_data[["Race", "Practice 1"]].apply(standardise, axis = 1)

session_name = "Practice 2"
stan_data["Practice 2"] = stan_data[["Race", "Practice 2"]].apply(standardise, axis = 1)

session_name = "Practice 3"
stan_data["Practice 3"] = stan_data[["Race", "Practice 3"]].apply(standardise, axis = 1)
    #Applying the standardisation function

stan_data.to_pickle("./data/Stan Data.pkl")
    #pkl used to prevent file formatting issues 


### Summary statistics model
    #As an alternative baseline, I decided to use data based on summary statistics (not the specific lap times) for each session for each driver

data = pd.read_pickle("./data/Outlier_Removed_Data_V2.pkl")
data = data.drop(columns = ["Driver Number"])

data = data.to_dict("index")

summary_data = {}
count = 0

for row in data.values():
    summary_values = {}
            #This is to store each of the summary statistics 
            #This will then be added to dictionary with key as index (count), added as a value 
    
    for session in ["Practice 1", "Practice 2", "Practice 3"]:
        #This will iterate through each of the sessions 

        session_times = row.get(session)
            #Saves the session times for every session

        if session_times is None:
            #If the session has no data for that driver 
            min_time = -1
            sd = -1
            mean_time = -1
            laps_completed = 0
                #I am saving these as -1 so I can mask them in my model
                #Not 0 as this would compete with my 0 in laps completed 

        elif len(session_times) == 0:
            min_time = -1
            sd = -1
            mean_time = -1
            laps_completed = 0
            

        else:
            min_time = min(session_times)
            mean_time = np.mean(np.array(session_times))
            sd = np.std(np.array(session_times))
            laps_completed = len(session_times)
            

        summary_values["{}Min".format(session)] = min_time
        summary_values["{}Mean".format(session)] = mean_time
        summary_values["{}SD".format(session)] = sd
        summary_values["{}NoLaps".format(session)] = laps_completed
    
    summary_values["Position"] = row.get("Qualifying Results")
    
    summary_data[count] = summary_values 
        #Appending the values to the global dictionary
        #Using the counter as an index 
        #After data has been recorded for all three 

        
    count += 1
        #This count will update where all the values are stored 
        #Act as an index 
#Creates a dictionary that stores all of the summary stats

summary_df = pd.DataFrame.from_dict(summary_data, orient = "index")
    #Converted to a dataframe 

summary_df.to_pickle("./data/Summary Data.pkl")
