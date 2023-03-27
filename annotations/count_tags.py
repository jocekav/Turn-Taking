import os
from datetime import datetime
import pandas as pd
import numpy as np
from collections import Counter
import csv
import matplotlib.pyplot as plt


fn = 1
df = pd.DataFrame()
time_stamps = []
labels = []
durs = []
total_dur = 0
for (root,dirs,files) in os.walk('/Users/jocekav/Documents/GitHub/Turn-Taking/annotations/markdown', topdown=True):
        for file in files:
            if file.endswith('.md'):
                with open(('/Users/jocekav/Documents/GitHub/Turn-Taking/annotations/markdown/' + file), 'r') as f:
                    line = f.readline()
                    total_length = line[-8:].replace('(','').replace(')','').strip()
                    prev_time = '00:00'
                    t1 = datetime.strptime(prev_time, "%M:%S")
                    t2 = datetime.strptime(total_length, "%M:%S")
                    diff = t2 - t1
                    print(total_length)
                    total_dur += diff.total_seconds()
                    # time_stamps.append(total_length)
                    line = f.readline()
                    while line:
                        if '#' in line:
                            turn_type = 'other'
                            if 'note' in line.casefold():
                                turn_type = 'note'
                            if 'struct' in line.casefold():
                                turn_type = 'struct'
                            if 'pass add' in line.casefold():
                                turn_type = 'pass add'
                            if 'pass new' in line.casefold():
                                turn_type = 'pass new'
                            if 'layer add' in line.casefold():
                                turn_type = 'layer add'
                            if 'layer new' in line.casefold():
                                turn_type = 'layer new'
                            if 'support' in line.casefold():
                                turn_type = 'support'
                            if 'call' in line.casefold():
                                turn_type = 'call'
                            if 'response' in line.casefold():
                                turn_type = 'response'
                            if 'interrupt' in line.casefold() or 'interupt' in line.casefold():
                                turn_type = 'interrupt'
                            if 'iso' in line.casefold():
                                turn_type = 'iso'
                            if 'simultaneous' in line.casefold():
                                turn_type = 'simult'
                            if 'duplicate' in line.casefold():
                                turn_type = 'duplicate'
                            print(turn_type)
                            # if turn_type is 'note' or turn_type is 'other':
                            #     print('skip')
                            # else:
                            time = line[4:9]
                            print(time)
                            time_stamps.append(time)
                            t1 = datetime.strptime(prev_time, "%M:%S")
                            t2 = datetime.strptime(time, "%M:%S")
                            diff = t2 - t1
                            print(diff.total_seconds())
                            durs.append(diff.total_seconds())
                            prev_time = time
                            labels.append(turn_type)
                        line = f.readline()
                # df[("timestamp" + str(fn))] = time_stamps
                # df[("dur" + str(fn))] = durs
                # df[("type" + str(fn))] = labels
                # time_stamps = []
                # durs = []
                # labels = []
                f.close()

for (root,dirs,files) in os.walk('/Users/jocekav/Documents/GitHub/Turn-Taking/annotations/csv-custom', topdown=True):
        for file in files:
            if file.endswith('.csv'):
                time_stamps = []
                with open(('/Users/jocekav/Documents/GitHub/Turn-Taking/annotations/csv-custom/' + file), 'r') as f:
                        csv_reader = csv.DictReader(f)
                        dict_csv = dict(list(csv_reader)[0])
                        columns = list(dict_csv.keys())
                        # print(columns)
                        total_length = (dict_csv['Length']).strip()
                        prev_time = '00:00'
                        t1 = datetime.strptime(prev_time, "%M:%S")
                        t2 = datetime.strptime(total_length, "%M:%S")
                        diff = t2 - t1
                        print(total_length)
                        total_dur += diff.total_seconds()
                        for col in columns[4:]:
                            turn_type = 'other'
                            if 'note' in line.casefold():
                                turn_type = 'note'
                            if 'struct' in line.casefold():
                                turn_type = 'struct'
                            if 'pass add' in line.casefold():
                                turn_type = 'pass add'
                            if 'pass new' in line.casefold():
                                turn_type = 'pass new'
                            if 'layer add' in line.casefold():
                                turn_type = 'layer add'
                            if 'layer new' in line.casefold():
                                turn_type = 'layer new'
                            if 'support' in line.casefold():
                                turn_type = 'support'
                            if 'call' in line.casefold():
                                turn_type = 'call'
                            if 'response' in line.casefold():
                                turn_type = 'response'
                            if 'interrupt' in line.casefold() or 'interupt' in line.casefold():
                                turn_type = 'interrupt'
                            if 'iso' in line.casefold():
                                turn_type = 'iso'
                            if 'simultaneous' in line.casefold():
                                turn_type = 'simult'
                            if 'duplicate' in line.casefold():
                                turn_type = 'duplicate'
                            print(turn_type)
                            # if turn_type is 'note' or turn_type is 'other':
                            #     print('skip')
                            # else:
                            labels.append(turn_type)
                            print(col)
                            time_stamps.append(col)
                            t1 = datetime.strptime(prev_time, "%M:%S")
                            t2 = datetime.strptime(col, "%M:%S")
                            diff = t2 - t1
                            print(diff.total_seconds())
                            durs.append(diff.total_seconds())
                            prev_time = col
                            line = dict_csv[col]

# print(len(durs))
mean = np.average(durs)
print("Avg dur: " + str(mean))
std = np.std(durs)
print("Std dur: " + str(std))


type_count = Counter(labels)
print("Type frequency: " + str(type_count))
print("Total seconds: " + str(total_dur))

# plt.boxplot(durs, showfliers=False)
plt.bar(type_count.keys(), type_count.values())
plt.xlabel("Turn Types")
plt.ylabel("Frequency")
# # show plot
plt.show()
# plt.scatter(x=labels, y=durs)
# plt.xlabel("Turn Types")
# plt.ylabel("Turn Length")

print('pass add')
mask = np.where(np.array(labels) == 'pass add')
print(mask[0])
mask_durs = np.array(durs)[mask[0]]
print(len(mask_durs))
mean = np.average(mask_durs)
print("Avg dur: " + str(mean))
std = np.std(mask_durs)
print("Std dur: " + str(std))

print('pass new')
mask = np.where(np.array(labels) == 'pass new')
print(mask[0])
mask_durs = np.array(durs)[mask[0]]
print(len(mask_durs))
mean = np.average(mask_durs)
print("Avg dur: " + str(mean))
std = np.std(mask_durs)
print("Std dur: " + str(std))

print('layer add')
mask = np.where(np.array(labels) == 'layer add')
print(mask[0])
mask_durs = np.array(durs)[mask[0]]
print(len(mask_durs))
mean = np.average(mask_durs)
print("Avg dur: " + str(mean))
std = np.std(mask_durs)
print("Std dur: " + str(std))

print('support')
mask = np.where(np.array(labels) == 'support')
print(mask[0])
mask_durs = np.array(durs)[mask[0]]
print(len(mask_durs))
mean = np.average(mask_durs)
print("Avg dur: " + str(mean))
std = np.std(mask_durs)
print("Std dur: " + str(std))

print('interrupt')
mask = np.where(np.array(labels) == 'interrupt')
print(mask[0])
mask_durs = np.array(durs)[mask[0]]
print(len(mask_durs))
mean = np.average(mask_durs)
print("Avg dur: " + str(mean))
std = np.std(mask_durs)
print("Std dur: " + str(std))

print('iso')
mask = np.where(np.array(labels) == 'iso')
print(mask[0])
mask_durs = np.array(durs)[mask[0]]
print(len(mask_durs))
mean = np.average(mask_durs)
print("Avg dur: " + str(mean))
std = np.std(mask_durs)
print("Std dur: " + str(std))

print('simult')
mask = np.where(np.array(labels) == 'simult')
print(mask[0])
mask_durs = np.array(durs)[mask[0]]
print(len(mask_durs))
mean = np.average(mask_durs)
print("Avg dur: " + str(mean))
std = np.std(mask_durs)
print("Std dur: " + str(std))

print('layer new')
mask = np.where(np.array(labels) == 'layer new')
print(mask[0])
mask_durs = np.array(durs)[mask[0]]
print(len(mask_durs))
mean = np.average(mask_durs)
print("Avg dur: " + str(mean))
std = np.std(mask_durs)
print("Std dur: " + str(std))

print('duplicate')
mask = np.where(np.array(labels) == 'duplicate')
print(mask[0])
mask_durs = np.array(durs)[mask[0]]
print(len(mask_durs))
mean = np.average(mask_durs)
print("Avg dur: " + str(mean))
std = np.std(mask_durs)
print("Std dur: " + str(std))

# plt.show()

# # Open the file in read mode
# text = open('/Users/jocekav/Documents/GitHub/Turn-Taking/annotations/markdown/Chacal Ensamble - free jazz improvisation - Pizza Jazz MÃ©xico.md', 'r')
  
# # Create an empty dictionary
# d = dict()
  
# # Loop through each line of the file
# for line in text:
#     # Remove the leading spaces and newline character
#     line = line.strip()
  
#     # Convert the characters in line to
#     # lowercase to avoid case mismatch
#     line = line.lower()
  
#     # Split the line into words
#     words = line.split(" ")
                         
  
#     # Iterate over each word in line
#     for word in words:
#         # Check if the word is already in dictionary
#         if word in d:
#             # Increment count of word by 1
#             d[word] = d[word] + 1
#         else:
#             # Add the word to dictionary with count 1
#             d[word] = 1
  
# # Print the contents of dictionary
# for key in list(d.keys()):
#     print(key, ":", d[key])

