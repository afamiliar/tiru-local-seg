# Python script to upload data to Flywheel
#       uses flywheel-sdk to upload processed data
#
#   created March 24, 2021
#   modified March 28, 2021 for liquid biopsy batch #2
#   amf
#
#       Based on: https://docs.flywheel.io/hc/en-us/articles/1500001422482-Upload-Data-To-A-New-Project
#
#   INPUTS:
#     input_fn              CSV file with subjects and sessions to download
#                               - should include header row ("C_ID","Session")
#                               - each subsequent row should correspond to one subject
#     fw_proj_label         name of Flywheel project to download data from (user must have appropriate read permissions for this project)
#     fw_group_label        name of Flywheel group that the project is associated with
#     api_key               user's unique Flywheel api key
#     files                 list of nifti filles to upload
#
#
#           REQUIRED DEPENDENCIES:  flywheel-sdk
#

# ====== user input ====== 
api_key='insert-API-key-here' # Flywheel API key

input_fn="subj_list.csv" # CSV file name
fw_proj_label='Liquid_Biopsy'
fw_group_label='d3b'

files=['brainTumorMask_SRI_edit1.nii.gz'] # files to upload




#  ************** REQUIRED FUNCTION(S) **************
def upload_file_to_acquistion(acquistion, fp, update=True, **kwargs):
    """Upload file to Acquisition container and update info if `update=True`
    
    Args:
        acquisition (flywheel.Acquisition): A Flywheel Acquisition
        fp (Path-like): Path to file to upload
        update (bool): If true, update container with key/value passed as kwargs.        
        kwargs (dict): Any key/value properties of Acquisition you would like to update.        
    """
    basename = os.path.basename(fp)
    if not os.path.isfile(fp):
        raise ValueError(f'{fp} is not file.')
        
    if acquistion.get_file(basename):
        return
    else:
        acquistion.upload_file(fp)
        while not acquistion.get_file(basename):   # to make sure the file is available before performing an update
            acquistion = acquistion.reload()
            time.sleep(1)
            
    if update and kwargs:
        f = acquisition.get_file(basename)
        f.update(**kwargs)



#  ************** MAIN PROCESSES **************
import csv
import flywheel
import os
import time
# import shutil

# ====== access the flywheel client for the instance ====== 
fw = flywheel.Client(api_key)

# ====== loop through subjects & upload files to Flywheel ====== 
## get existing containers from Flywheel
grp_cntnr = fw.lookup(fw_group_label)
proj_cntnr = grp_cntnr.projects.find_first(f'label={fw_proj_label}')

## get list of all subject in CSV
input_file = csv.DictReader(open(input_fn, "r", encoding="utf-8-sig"))

for row in input_file:
    sub = row["C_ID"]
    session_label = row["Session"]

    ## get existing containers from Flywheel
    sub_cntnr = proj_cntnr.subjects.find_first(f'label={sub}')
    session = sub_cntnr.sessions.find_first(f'label={session_label}')

    ## auto seg results
    for file in files:
        file_path='data/'+sub+'/'+session_label+'/'
        acq_label='brainTumorMask_SRI'
        if os.path.exists(file_path+file):
            acquisition=fw.lookup(fw_group_label+'/'+fw_proj_label+'/'+sub+'/'+session_label+'/'+acq_label)
            upload_file_to_acquistion(acquisition, file_path+file)
        else:
            print('Skipping '+sub+' - no file found for this subject!')
