#get the data
import pandas
data = [line.split(",") for line in open("QQQ.csv")]
data.pop(0)

#create the hashmap and store the data that will collected in a hashmap
data_hashmap = {}
for current_index in range(len(data)):
    data_hashmap[current_index] = {}
    data_hashmap[current_index]["Open"] = data[current_index][1]
    data_hashmap[current_index]["Close"] = data[current_index][4]
 
def get_parameters(given_hashmap):
    total_sum,value_count = 0,0
    #calculate the mean
    for current_index in given_hashmap:
        total_sum += given_hashmap[current_index]
        value_count += 1
    mean = float(total_sum/value_count)

    #calculate the standard deviation
    numerator,denominator = 0,value_count-1 
    for current_index in given_hashmap:
        numerator += (given_hashmap[current_index]-mean)**2
    std = (numerator/denominator)**(1/2)

    return {"mean":mean,"std":std}

PANDAS_DATA = {"daysToExp":[],"mean":[],"std":[]}
for day_return in range(0,91):
    print ("Creating data for: {} return".format(day_return))
    temp_hashmap = {}
    index = 0
    while index + day_return in data_hashmap:
        open_price = float(data_hashmap[index]["Open"])
        close_price = float(data_hashmap[index+day_return]["Close"])
        return_for_day = (close_price-open_price)/open_price
        #add the data to the hashmap
        temp_hashmap[index] = return_for_day
        index += 1
    stat_data = get_parameters(temp_hashmap)
    #Update the data that we will need to save
    PANDAS_DATA["daysToExp"].append(day_return)
    PANDAS_DATA["mean"].append(stat_data["mean"])
    PANDAS_DATA["std"].append(stat_data["std"])
    print ("{} sample logged\n".format(index))

#save everything to csv file
CSV_FILE = pandas.DataFrame(PANDAS_DATA)
CSV_FILE.to_csv("QQQ_return_data.csv",index=False)
