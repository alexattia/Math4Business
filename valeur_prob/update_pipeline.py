import download_data
import data_to_variables
import model

def update_pipeline():
	download_data.main()
	data_to_variables.main()

update_pipeline()


