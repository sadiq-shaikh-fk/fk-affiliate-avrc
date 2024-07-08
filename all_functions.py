import pandas as pd
import warnings
warnings.filterwarnings("ignore")

def start(path):
    data = input_data(path)
    output_data_path = data_cleaning(data)
    return output_data_path

def input_data(path):
    data  = pd.read_csv(path)
    data = data[['Prospect ID', 'Mobile Number','Phone Number', 'Email', 'Primary Source Campaign', 'eKYC Stage Code', 'Total Payment Amount', 'Created On']]
    print(f'Data has {data.shape[0]} rows {data.shape[1]} and columns')
    return data

def data_cleaning(data):
    print('------------------ Benging with Data Cleaning ------------------\n')
    data1 = handle_mob_no(data)
    data2 = handle_ekyc_stage(data1)
    data3 = handle_vendors_data(data2)
    data4 = creating_lead_stage(data3)
    data5 = creating_pivot_agency_wise(data4)
    #data6 = craete_excel(data5)
    print('------------------ DONE! ------------------\n')
    return data5

def handle_mob_no(data):
    print('------------------ Filling Mob No column ------------------\n')
    # ---------------- Task 1 -Fill Mob No from Phone Number where Mob No is empty ----------------
    data_main = data    
    # Fill the null values in 'Mobile Number' with the last 10 digits of 'Phone Number'
    data_main['Mobile Number'] = data_main.apply(
    lambda row: extract_last_10_digits(row['Phone Number']) if pd.isnull(row['Mobile Number']) or row['Mobile Number'] in ['None', 'nan'] else row['Mobile Number'], axis=1)
    # Convert 'Mobile Number' to integer to remove any .0, then back to string
    data_main['Mobile Number'] = data_main['Mobile Number'].apply(lambda x: str(int(float(x))))
    return data_main

def handle_ekyc_stage(data):
    print('------------------ Filling e-KYC Stage column ------------------\n')
    # ---------------- Task 2 - Fill 'e2_Email' in eKYC Stage Code column ----------------
    data_main = data    
    data_main["eKYC Stage Code"] = data_main['eKYC Stage Code'].fillna('e2_Email')
    return data_main

def handle_vendors_data(data):
    print('------------------ Merging Vendors Data ------------------\n')
    data_main = data
    # Task 3 - 
    csv_url = 'https://docs.google.com/spreadsheets/d/1osDdsySYQdoBZlguvbb_UCZt2wfRbQvhSj8B2qa_RgU/export?format=csv'
    vendors_data = pd.read_csv(csv_url, header=None)
    # Set the first row as the header
    vendors_data.columns = vendors_data.iloc[1]
    vendors_data = vendors_data.drop([0, 1]).reset_index(drop=True)
    # extracting only the required values from vendors_data
    vendors_data_req = vendors_data[['TG/YT1 Bitly','campaign', 'Agency']]
    # renaming the columns
    vendors_data_req.columns= ['Bitly Link','Primary Source Campaign','agency']
    # removing null 
    vendors_data_req.dropna(how='any', inplace=True)
    # printing null valuse from each column after removing null
    print(vendors_data_req.isna().sum())
    print(vendors_data_req.shape[0])
    # Merge the data_main DataFrame with the vendors DataFrame on 'Primary Source Campaign'
    data_merged = data_main.merge(vendors_data_req, on='Primary Source Campaign', how='left')
    return data_merged

def creating_lead_stage(data_merged):
    print('------------------ Creating Lead Stage column ------------------\n')
    # filling 0 in all NaN values
    data_merged['Total Payment Amount'].fillna(0, inplace=True)
    # adding a new column called Lead Stage
    data_merged.insert(5, 'Lead Stage', None)
    # adding values into Lead Stage
    data_merged['Lead Stage'] = data_merged.apply(generate_lead_stage, axis=1)
    # removing empty values from 'agency', 'Bitly Link' 
    data_merged.dropna(subset=['agency', 'Bitly Link'], inplace=True)
    # dropping unused columns
    data_merged.drop(columns=['Prospect ID', 'Phone Number', 'Email'], inplace=True)   
    data_merged_lead = data_merged
    return data_merged_lead

def creating_pivot_agency_wise(data_merged_lead):
    print('------------------ Pivoting the Data - Agency wise ------------------\n')
    # grouping data by agency
    agency_groups = data_merged_lead.groupby('agency')
    # from df creating a dict of df 
    agency_dfs = {agency: group.drop(columns=['agency']) for agency, group in agency_groups}

    # from the dict creating list of key and values
    list_of_agency = []
    list_of_agency_df = []
    for agency, df in agency_dfs.items():
        list_of_agency.append(agency)
        list_of_agency_df.append(df)
    
    # from the df of dict generating pivot for each df
    pivoted_df = []
    for each_df in list_of_agency_df:
        each_df_pivot = pd.pivot_table(each_df, index='Primary Source Campaign', columns='Lead Stage', values='Mobile Number', aggfunc='count', fill_value=0)

        # adding a row of TOTAL
        sum_row = each_df_pivot.sum()
        sum_row.name = 'TOTAL'
        each_df_pivot = pd.concat([each_df_pivot, pd.DataFrame(sum_row).T])

        # Reset the index to make 'Primary Source Campaign' a regular column
        each_df_pivot = each_df_pivot.reset_index()

        # Ensure all desired columns are present
        required_columns = ['999-Account Opened', 'L2-in process', 'L4-Account Opened']
        for col in required_columns:
            if col not in each_df_pivot.columns:
                each_df_pivot[col] = 0

        # merging Bitly Links to it ---- # Create a dictionary to map 'Primary Source Campaign' to 'Bitly Link'
        campaign_to_bitly = data_merged_lead.set_index('Primary Source Campaign')['Bitly Link'].to_dict()

        # Add 'Bitly Link' column to data_merged_pivot by mapping
        each_df_pivot['Bitly Link'] = data_merged_lead['Primary Source Campaign'].map(campaign_to_bitly)
        each_df_pivot.rename(columns={'index':'Primary Source Campaign'}, inplace=True)
    
        pivoted_df.append(each_df_pivot)
    
    agency_pivotdf_dict = agency_dfs.copy()
    agency_pivotdf_dict.update(dict(zip(agency_dfs.keys(), pivoted_df)))
    return agency_pivotdf_dict

# ------------------------- supporting functions ---------------------------
# Function to extract the last 10 digits of the phone number
def extract_last_10_digits(phone):
    return str(phone)[-10:]

# Define the generate_lead_stage function
def generate_lead_stage(row):
    ekyc_stage_code = row['eKYC Stage Code']
    total_payment_amount = row['Total Payment Amount']
    
    if 'e12' in ekyc_stage_code or 'e14' in ekyc_stage_code or 'e15' in ekyc_stage_code:
        if total_payment_amount > 100:
            return '999-Account Opened'
        else:
            return 'L4-Account Opened'
    else:
        return 'L2-in process'
