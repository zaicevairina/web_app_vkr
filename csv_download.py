from google.oauth2 import service_account
from google.cloud import bigquery

import pandas as pd
import pandas_gbq as gbq
from env import project_id, private_key,credentials


gbq.context.credentials = credentials
gbq.context.project = project_id


def upload_user_bd(list_of_lists,username):
	try:
		print(list_of_lists)
		print(username)
		df = pd.DataFrame(list_of_lists, columns=['author','title','keywords'])
		print(df)
		gbq.to_gbq(df,'dataset.'+username, project_id , if_exists = 'append' )
		return True

	except:
		return -1