
import gearman, pickle
import pprint

# Define admin (just for fun)
admin = gearman.admin_client.GearmanAdminClient(['localhost:4730'])
pprint.pprint(admin.get_status())

# # Define client
# client = gearman.GearmanClient(['localhost:4730'])

# # Pass sample function + data
# data = {'fn': 'addLikeAsync', 'args': [1, 2, 3], 'kwargs': {'a':7}}
# client.submit_job('apiQueue', pickle.dumps(data), background=True)