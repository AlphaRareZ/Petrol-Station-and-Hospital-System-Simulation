import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
# Set random seed for reproducibility
np.random.seed(42)

# Simulation parameters
number_of_cars = int(input("Enter Number of Cars"))  # Total simulation time in minutes

inter_arrival_times = [0, 1, 2, 3]
inter_arrival_probabilities = [0.17, 0.23, 0.25, 0.35]

categories = ["A", "B", "C"]
category_probabilities = [0.2, 0.35, 0.45]

service_times_A_B = [1, 2, 3]
service_probabilities_A_B = [0.2, 0.3, 0.5]

service_times_C = [3, 5, 7]
service_probabilities_C = [0.2, 0.5, 0.3]

# Initialize variables
i = 0
time = 0
events = []
pump_idle_time = {"95 Octane": 0, "90 Octane": 0, "Gas": 0}
pump_queues = {"95 Octane": [], "90 Octane": [], "Gas": []}
last_pump_free_time = {"95 Octane": 0, "90 Octane": 0, "Gas": 0}
# time here refers to arrival time because we increment inter_arrival time to it each iteration

# Generate inter-arrival times and cars

for i in range(number_of_cars):
    inter_arrival = np.random.choice(inter_arrival_times, p=inter_arrival_probabilities)
    time += inter_arrival

    car_category = np.random.choice(categories, p=category_probabilities)

    # Assign service time
    if car_category in ["A", "B"]:
        service_time = np.random.choice(service_times_A_B, p=service_probabilities_A_B)
    else:
        service_time = np.random.choice(service_times_C, p=service_probabilities_C)

    # Determine pump assignment
    if car_category == "B":
        if len(pump_queues["90 Octane"]) > 3:  # More than 3 cars in the "90 Octane" queue
            pump = "95 Octane" if np.random.rand() < 0.6 else "90 Octane"
        else:
            pump = "90 Octane"
    elif car_category == "C":
        if len(pump_queues["Gas"]) > 4:  # More than 4 cars in the "Gas" queue
            pump = "90 Octane" if np.random.rand() < 0.4 else "Gas"
        else:
            pump = "Gas"
    else:  # Category A
        pump = "95 Octane"

    # Calculate waiting time and start/end times

    # if the queue is empty then the waiting time is the service end time of the last one in the pump - the current time
    waiting_time = max(0, last_pump_free_time[pump] - time)

    # if not pump_queues[pump]:
    #     waiting_time = max(0, last_pump_free_time[pump] - time)
    # else:
    #     # cars that came before me - the moment I came
    #     waiting_time = max(0, sum(event["service_time"] for event in pump_queues[pump]) - (time - pump_queues[pump][-1]["arrival_time"]))

    service_start_time = time + waiting_time
    service_end_time = service_start_time + service_time

    # Update idle time for pump
    #Working
    # if service_start_time > last_pump_free_time[pump]:
    #     pump_idle_time[pump] += service_start_time - last_pump_free_time[pump]
    if service_start_time >= last_pump_free_time[pump]:
        pump_idle_time[pump] = service_start_time - last_pump_free_time[pump]

    # Record event
    event = {
        "inter-arrival_time": inter_arrival,
        "arrival_time": time,
        "car_category": car_category,
        "pump": pump,
        "service_time": service_time,
        "service_start_time": service_start_time,
        "service_end_time": service_end_time,
        "waiting_time": waiting_time,
        "cumulative_pump_idle_time": pump_idle_time[pump],
    }
    events.append(event)

    # Update pump state
    pump_queues[pump].append(event)
    last_pump_free_time[pump] = service_end_time

# Convert events to DataFrame
df = pd.DataFrame(events)
df.to_excel("output.xlsx", index=False)
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)

# Display the resulting DataFrame
df.to_excel("output.xlsx", index=False)

data = df
#                           -------------------
# 1. Average service time of cars in the three categories
avg_service_time = data.groupby('car_category')['service_time'].mean()

# 2. Average waiting time in the queues for each pump, and all cars
avg_waiting_time_by_pump = data.groupby('pump')['waiting_time'].mean()
avg_waiting_time_all = data['waiting_time'].mean()

# 3. Maximum queue length for each pump (approximated as cars waiting for service at the same pump)
queue_lengths = data.groupby('pump').size()

# 4. Probability that a car waits for each pump
prob_wait_by_pump = data[data['waiting_time'] > 0].groupby('pump').size() / data.groupby('pump').size()

# 5. Portion of idle time of each pump
total_idle_time_by_pump = data.groupby('pump')['cumulative_pump_idle_time'].sum()
total_time = data['service_end_time'].max()  # Assuming service_end_time covers all events
idle_time_portion = total_idle_time_by_pump / total_time

# Visualization
fig, axes = plt.subplots(2, 2, figsize=(14, 10))
fig.suptitle('Petrol Station Multi-Channel Queue')

# Plot 1: Average service time by car category
axes[0, 0].bar(avg_service_time.index, avg_service_time.values, color='blue', alpha=0.7)
axes[0, 0].set_title('Average Service Time by Car Category')
axes[0, 0].set_xlabel('Car Category')
axes[0, 0].set_ylabel('Average Service Time')

# Plot 2: Average waiting time by pump
axes[0, 1].bar(avg_waiting_time_by_pump.index, avg_waiting_time_by_pump.values, color='green', alpha=0.7)
axes[0, 1].set_title('Average Waiting Time by Pump')
axes[0, 1].set_xlabel('Pump Type')
axes[0, 1].set_ylabel('Average Waiting Time')

# Plot 3: Maximum queue length by pump
axes[1, 0].bar(queue_lengths.index, queue_lengths.values, color='orange', alpha=0.7)
axes[1, 0].set_title('Maximum Queue Length by Pump')
axes[1, 0].set_xlabel('Pump Type')
axes[1, 0].set_ylabel('Queue Length')

# Plot 4: Portion of idle time by pump
axes[1, 1].bar(idle_time_portion.index, idle_time_portion.values, color='red', alpha=0.7)
axes[1, 1].set_title('Portion of Idle Time by Pump')
axes[1, 1].set_xlabel('Pump Type')
axes[1, 1].set_ylabel('Idle Time Portion')

plt.tight_layout(rect=[0, 0, 1, 0.96])
plt.show()

# Print results
avg_service_time, avg_waiting_time_by_pump, avg_waiting_time_all, queue_lengths, prob_wait_by_pump, idle_time_portion

print(df)