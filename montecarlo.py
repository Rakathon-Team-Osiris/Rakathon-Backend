from pinecone import Pinecone

# Initialize the Pinecone client
pc = Pinecone(api_key="97cc1ea8-d32a-4966-82ed-22e191ba93ec")

# Connect to the index
index = pc.Index("slay-vector-db")

# Fetch the vector and its metadata for the specific ID
item_id = "c2d766ca982eca8304150849735ffef9"
response = index.fetch(ids=[item_id])

# Extract the vector and metadata
vector_data = response['vectors'][item_id]

# Print the vector and metadata
print("Vector:", vector_data['values'])

ans = index.query(
    vector=vector_data['values'],
    top_k=100,
    include_values=True,
    include_metadata=True,
)
 
array =[]

for i in range(len(ans['matches'])):
    array.append(ans['matches'][i]['id'])

import random

# The given ID to search for
target_id = "0bb61c94868e866fb432a7608e87460d"

# Simulate the list with 7287 random elements including the target ID
list_size = 7287
elements = [f"random_id_{i}" for i in range(list_size - 1)]
elements.append(target_id)

# Monte Carlo simulation to determine the number of attempts to find the target ID
def monte_carlo_simulation(elements, target_id, num_simulations=10000):
    attempts = []
    
    for _ in range(num_simulations):
        count = 0
        while True:
            count += 1
            chosen_id = random.choice(elements)
            if chosen_id == target_id:
                attempts.append(count)
                break
    
    # Calculate the average number of attempts
    average_attempts = sum(attempts) / len(attempts)
    return average_attempts

# Run the simulation
average_attempts = monte_carlo_simulation(elements, target_id)
print(f"Average attempts to find the target ID: {average_attempts}")
