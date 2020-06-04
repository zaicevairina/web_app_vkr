from nltk.corpus import stopwords
from google.oauth2 import service_account

credentials = service_account.Credentials.from_service_account_file('./diplom-275218-a097a7baee3f.json')
project_id = 'diplom-275218'
private_key = 'diplom-275218-a097a7baee3f.json'
stops = set(stopwords.words("english")) | set(stopwords.words("russian"))
stops.add('рис')
stops.add('университет')
stops.add('брянск')