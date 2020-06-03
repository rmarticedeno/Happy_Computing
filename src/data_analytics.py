import pandas as pd
from happy_computing import HappyComputing

experiments = 1000

results = {
    'Client Count': [0]*experiments,
    'Type 1 Client Count': [0]*experiments,
    'Type 2 Client Count': [0]*experiments,
    'Type 3 Client Count': [0]*experiments,
    'Type 4 Client Count': [0]*experiments,
    'Total Vendor Waiting Time': [0]*experiments,
    'Total Technical Works Waiting Time': [0]*experiments,
    'Total Specialized Technical Works Waiting Time': [0]*experiments,
    'Vendor 1 Client Count': [0]*experiments,
    'Vendor 2 Client Count': [0]*experiments,
    'Technician 1 Client Count': [0]*experiments,
    'Technician 2 Client Count': [0]*experiments,
    'Technician 3 Client Count': [0]*experiments,
    'Experienced Technician Client Count': [0]*experiments,
    'Profit': [0]*experiments
}

workers = {
    1:'Vendor 1 Client Count',
    2:'Vendor 2 Client Count',
    3:'Technician 1 Client Count',
    4:'Technician 2 Client Count',
    5:'Technician 3 Client Count',
    6:'Experienced Technician Client Count',
}

profit = {
    1: 0,
    2: 350,
    3: 500,
    4: 750
}

index = [ i for i in range(1,experiments+1)]

workshop = HappyComputing(logs=False)

for i in range(experiments):
    workshop.simulate()

    for client in workshop.visitors_list:
        results['Client Count'][i] += 1
        results['Total Vendor Waiting Time'][i] += client.vendor_waiting_time
        results['Total Technical Works Waiting Time'][i] += client.tec_waiting_time
        results['Total Specialized Technical Works Waiting Time'][i] += client.stec_waiting_time

        results[workers[client.vendor_id]][i] += 1

        if client.type != 4:
            results[workers[client.tec_id]][i] += 1

        results['Profit'][i] += profit[client.type]

        if client.type == 1:
            results['Type 1 Client Count'][i] += 1
        elif client.type == 2:
            results['Type 2 Client Count'][i] += 1
        elif client.type == 3:
            results['Type 3 Client Count'][i] += 1
        else:
            results['Type 4 Client Count'][i] += 1

#print(results)

data = pd.DataFrame(results)

summary = data.describe()

summary.to_csv('summary.csv')
