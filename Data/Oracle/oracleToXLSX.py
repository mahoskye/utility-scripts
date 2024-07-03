import os
import time
from datetime import datetime

try:
    import oracledb
    import pandas as pd
    from sqlalchemy import create_engine, text
    from tqdm import tqdm
except ImportError as e:
    missing_package = str(e).split()[-1]
    print(f"Missing required package: {missing_package}.")
    print(f"pip install {missing_package}")
    exit(1)

DATABASE = 'DEV'
OUTPUT_FILENAME = 'filename_goes_here'
CHUNK_SIZE = 1000
QUERY = '''
 
 
 
'''

# Shouldn't need to edit this unless the databases change
DATABASES = {
    'CREDENTIALS': {
        'username': 'user',
        'password': 'password'
    },
    'DEV': {
        'hostname': 'dev.host',
        'port': 1234,
        'service': 'DEV.HOST'
    },
    'TEST': {
        'hostname': 'test.host',
        'port': 1234,
        'service': 'TEST.HOST'
    },
    'PROD': {
        'hostname': 'prod.host',
        'port': 1234,
        'service': 'PROD.HOST'
    }
}

# Generate DSN Connection info
dsn_tns = oracledb.makedsn(
    host=DATABASES[DATABASE]['hostname'],
    port=DATABASES[DATABASE]['port'],
    service_name=DATABASES[DATABASE]['service']
)


# Create SQLAlchemy engine
engine = create_engine(
    f'oracle+oracledb://{DATABASES["CREDENTIALS"]["username"]}:{DATABASES["CREDENTIALS"]["password"]}@{dsn_tns}')


def generate_count_query(original_query):
    # Generate a count query from the original query
    upper_query = original_query.upper()
    from_pos = upper_query.find('FROM')

    if from_pos == -1:
        raise ValueError("The query does not contain a 'FROM' keyword")

    count_query = f"SELECT COUNT(*) {original_query[from_pos:]}"
    return count_query


def fetch_data_in_chunks(query, engine, chunk_size):
    # Execute query in chunks and provide progress
    offset = 0

    with engine.connect() as connection:
        result = connection.execute(
            text(f'{generate_count_query(query)}'))
        total_rows = result.scalar()
        print(f'Total rows to fetch: {total_rows}')
        data_frames = []

        with tqdm(total=total_rows, desc='Fetching data') as pbar:
            while offset < total_rows:
                chunk_query = f"{query} OFFSET {offset} ROWS FETCH NEXT {chunk_size} ROWS ONLY"
                chunk_df = pd.read_sql(text(chunk_query), connection)
                data_frames.append(chunk_df)
                offset += chunk_size
                pbar.update(len(chunk_df))
                # Adding a slight delay to show progress updates clearly
                time.sleep(0.1)

    return pd.concat(data_frames, ignore_index=True)


# When did we start?
start_time = time.time()


df = fetch_data_in_chunks(QUERY, engine, CHUNK_SIZE)


# Determine the user's Documents/exports directory
onedrive_folder = os.environ.get('OneDrive')
if onedrive_folder:
    documents_folder = os.path.join(onedrive_folder, "Documents")
else:
    # Fallback if onedrive not available
    documents_folder = os.path.join(os.path.expanduser("~"), "Documents")

exports_folder = os.path.join(documents_folder, "exports")
os.makedirs(exports_folder, exist_ok=True)

# Construct the output file
current_datetime = datetime.now().strftime('%Y%m%d%H%M%S')
filename = f'{current_datetime}_{OUTPUT_FILENAME}.xlsx'
output_filepath = os.path.join(exports_folder, filename)

# Save the data and the query to excel
with pd.ExcelWriter(output_filepath, engine='openpyxl') as writer:
    df.to_excel(writer, index=False, sheet_name='Data')
    # Create dataframe with the query text
    query_df = pd.DataFrame([QUERY], columns=['Query'])
    query_df.to_excel(writer, index=False, sheet_name='Query',
                      startrow=0, startcol=0)

# When did we end?
end_time = time.time()
elapsed_time = end_time - start_time

hours, rem = divmod(elapsed_time, 3600)
minutes, seconds = divmod(rem, 60)

print(
    f'Data fetching and saving completed in {int(hours):02}:{int(minutes):02}:{int(seconds):02}.')
print(f'File saved to: {exports_folder} as {filename}')
