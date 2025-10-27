
import json
import agent

#with open("test1.json", "r") as f:
   #event_data = json.load(f)  # Read and parse the JSON event file

# Simulate AWS Lambda handler call
#def lambda_handler(event,context):
    #agent.run(event) #pass test_mode=True
    #return json.loads("{}")  # Returns an empty JSON object

# Call the lambda_handler explicitly for local testing
#print("before call the lambda_handler function") #add new log to the code
#lambda_handler(event_data, None) #call the lambda_handler function
#print("after call the lambda_handler function") #add new log to the code




def lambda_handler(event, context):
    agent.run(event)
    return json.loads("{}")



