import requests
import os
import json
import smtplib
import ssl
import imaplib
import datetime
import logging
import pandas as pd

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from jinja2 import Environment
from datetime import datetime
from datetime import time
from requests.adapters import HTTPAdapter
from urllib3 import Retry
from dotenv import load_dotenv

def set_current_directory():
    logging.info('Setting current directory')
    os.chdir(os.getcwd())

def start_logging():
    global process_name

    # Get File Name of existing script
    process_name = os.path.basename(__file__).replace('.py', '').replace(' ', '_')

    logging.basicConfig(filename=f'Logs/{process_name}.log', format='%(asctime)s %(message)s', filemode='w',
                        level=logging.DEBUG)

    # Printing the output to file for debugging
    logging.info('Starting the Script')

def stop_logging():
    logging.info('Stopping the Script')

def set_api_request_strategy():
    logging.info('Setting API Request strategy')

    global http

    retry_strategy = Retry(
        total=3,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=['HEAD', 'GET', 'OPTIONS'],
        backoff_factor=10
    )

    adapter = HTTPAdapter(max_retries=retry_strategy)
    http = requests.Session()
    http.mount('https://', adapter)
    http.mount('http://', adapter)

def get_env_variables():
    logging.info('Setting Environment variables')

    global RE_API_KEY, MAIL_USERN, MAIL_PASSWORD, IMAP_URL, IMAP_PORT, SMTP_URL, SMTP_PORT, SEND_TO

    load_dotenv()

    RE_API_KEY = os.getenv('RE_API_KEY')
    MAIL_USERN = os.getenv('MAIL_USERN')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    IMAP_URL = os.getenv('IMAP_URL')
    IMAP_PORT = os.getenv('IMAP_PORT')
    SMTP_URL = os.getenv('SMTP_URL')
    SMTP_PORT = os.getenv('SMTP_PORT')
    SEND_TO = os.getenv('SEND_TO')

def send_error_emails(subject):
    logging.info('Sending email for an error')

    message = MIMEMultipart()
    message["Subject"] = subject
    message["From"] = MAIL_USERN
    message["To"] = SEND_TO

    # Adding Reply-to header
    message.add_header('reply-to', MAIL_USERN)

    TEMPLATE = """
    <table style="background-color: #ffffff; border-color: #ffffff; width: auto; margin-left: auto; margin-right: auto;">
    <tbody>
    <tr style="height: 127px;">
    <td style="background-color: #363636; width: 100%; text-align: center; vertical-align: middle; height: 127px;">&nbsp;
    <h1><span style="color: #ffffff;">&nbsp;Raiser's Edge Automation: {{job_name}} Failed</span>&nbsp;</h1>
    </td>
    </tr>
    <tr style="height: 18px;">
    <td style="height: 18px; background-color: #ffffff; border-color: #ffffff;">&nbsp;</td>
    </tr>
    <tr style="height: 18px;">
    <td style="width: 100%; height: 18px; background-color: #ffffff; border-color: #ffffff; text-align: center; vertical-align: middle;">&nbsp;<span style="color: #455362;">This is to notify you that execution of Auto-updating Alumni records has failed.</span>&nbsp;</td>
    </tr>
    <tr style="height: 18px;">
    <td style="height: 18px; background-color: #ffffff; border-color: #ffffff;">&nbsp;</td>
    </tr>
    <tr style="height: 61px;">
    <td style="width: 100%; background-color: #2f2f2f; height: 61px; text-align: center; vertical-align: middle;">
    <h2><span style="color: #ffffff;">Job details:</span></h2>
    </td>
    </tr>
    <tr style="height: 52px;">
    <td style="height: 52px;">
    <table style="background-color: #2f2f2f; width: 100%; margin-left: auto; margin-right: auto; height: 42px;">
    <tbody>
    <tr>
    <td style="width: 50%; text-align: center; vertical-align: middle;">&nbsp;<span style="color: #ffffff;">Job :</span>&nbsp;</td>
    <td style="background-color: #ff8e2d; width: 50%; text-align: center; vertical-align: middle;">&nbsp;{{job_name}}&nbsp;</td>
    </tr>
    <tr>
    <td style="width: 50%; text-align: center; vertical-align: middle;">&nbsp;<span style="color: #ffffff;">Failed on :</span>&nbsp;</td>
    <td style="background-color: #ff8e2d; width: 50%; text-align: center; vertical-align: middle;">&nbsp;{{current_time}}&nbsp;</td>
    </tr>
    </tbody>
    </table>
    </td>
    </tr>
    <tr style="height: 18px;">
    <td style="height: 18px; background-color: #ffffff;">&nbsp;</td>
    </tr>
    <tr style="height: 18px;">
    <td style="height: 18px; width: 100%; background-color: #ffffff; text-align: center; vertical-align: middle;">Below is the detailed error log,</td>
    </tr>
    <tr style="height: 217.34375px;">
    <td style="height: 217.34375px; background-color: #f8f9f9; width: 100%; text-align: left; vertical-align: middle;">{{error_log_message}}</td>
    </tr>
    </tbody>
    </table>
    """

    # Create a text/html message from a rendered template
    emailbody = MIMEText(
        Environment().from_string(TEMPLATE).render(
            job_name=subject,
            current_time=datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            error_log_message=Argument
        ), "html"
    )

    # Add HTML parts to MIMEMultipart message
    # The email client will try to render the last part first
    try:
        message.attach(emailbody)
        attach_file_to_email(message, f'Logs/{process_name}.log')
        emailcontent = message.as_string()

    except:
        message.attach(emailbody)
        emailcontent = message.as_string()

    # Create secure connection with server and send email
    context = ssl._create_unverified_context()
    with smtplib.SMTP_SSL(SMTP_URL, SMTP_PORT, context=context) as server:
        server.login(MAIL_USERN, MAIL_PASSWORD)
        server.sendmail(
            MAIL_USERN, SEND_TO, emailcontent
        )

    # Save copy of the sent email to sent items folder
    with imaplib.IMAP4_SSL(IMAP_URL, IMAP_PORT) as imap:
        imap.login(MAIL_USERN, MAIL_PASSWORD)
        imap.append('Sent', '\\Seen', imaplib.Time2Internaldate(time.time()), emailcontent.encode('utf8'))
        imap.logout()

def attach_file_to_email(message, filename):
    # Open the attachment file for reading in binary mode, and make it a MIMEApplication class
    with open(filename, "rb") as f:
        file_attachment = MIMEApplication(f.read())

    # Add header/name to the attachments
    file_attachment.add_header(
        "Content-Disposition",
        f"attachment; filename= {filename}",
    )

    # Attach the file to the message
    message.attach(file_attachment)

def retrieve_token():

    logging.info('Retrieve token for API connections')

    with open('access_token_output.json') as access_token_output:
        data = json.load(access_token_output)
        access_token = data['access_token']

    return access_token

def get_request_re(url, params):
    logging.info('Running GET Request from RE function')

    # Request Headers for Blackbaud API request
    headers = {
        # Request headers
        'Bb-Api-Subscription-Key': RE_API_KEY,
        'Authorization': 'Bearer ' + retrieve_token(),
    }

    logging.info(params)

    re_api_response = http.get(url, params=params, headers=headers).json()

    return re_api_response

def post_request_re(url, params):
    logging.info('Running POST Request to RE function')

    # Request headers
    headers = {
        'Bb-Api-Subscription-Key': RE_API_KEY,
        'Authorization': 'Bearer ' + retrieve_token(),
        'Content-Type': 'application/json',
    }

    logging.info(params)

    re_api_response = http.post(url, params=params, headers=headers, json=params).json()

    return re_api_response

def patch_request_re(url, params):
    logging.info('Running PATCH Request to RE function')

    # Request headers
    headers = {
        'Bb-Api-Subscription-Key': RE_API_KEY,
        'Authorization': 'Bearer ' + retrieve_token(),
        'Content-Type': 'application/json'
    }

    logging.info(params)

    re_api_response = http.patch(url, headers=headers, data=json.dumps(params))

    return re_api_response

def load_data(source):
    logging.info(f'Load Data from {source}')

    df = pd.read_parquet(source)
    return df

def get_hard_bounces():
    logging.info('Getting the list of Hard Bounces')

    df = netcore[netcore['Bounce Type'] == 'Hard Bounce'][['EMAIL (Primary Key)']].drop_duplicates().reset_index(drop=True)
    return df

def find_remaining_data(all_df, partial_df):
    logging.info('Identifying missing data between two Panda Dataframes')

    # Concatenate dataframes A and B vertically and drop duplicates
    df = pd.concat([all_df, partial_df]).drop_duplicates(keep=False)

    # df = pd.merge(partial_df, all_df, how='left', indicator=True)
    # df = df[df['_merge'] == 'left_only']
    #
    # # Drop the '_merge' column from the result
    # df = df.drop('_merge', axis=1)

    return df

def identify_hard_bounces():
    logging.info('Identifying New Hard Bounces')

    # Load Records already uploaded in RE
    if os.path.exists('Databases/Hard Bounces.parquet'):
        hard_bounces_uploaded = pd.read_parquet('Databases/Hard Bounces.parquet')
        df = find_remaining_data(hard_bounces, hard_bounces_uploaded).copy()
    else:
        df = hard_bounces.copy()

    return df

def get_unsubscribes():
    logging.info('Getting the list of Unsubscribes')

    df = netcore[~netcore['Unsub reason'].isnull()][['EMAIL (Primary Key)', 'Subject', 'Sent Date', 'Open time', 'Unsub reason']].drop_duplicates().reset_index(drop=True)
    return df

def identify_unsubscribes():
    logging.info('Identifying new Unsubscribes')

    # Load Records already uploaded in RE
    if os.path.exists('Databases/Unsubscribes.parquet'):
        unsubscribes_uploaded = pd.read_parquet('Databases/Unsubscribes.parquet')
        df = find_remaining_data(unsubscribes, unsubscribes_uploaded).copy()
    else:
        df = unsubscribes.copy()

    return df

def post_unsubscribes_to_re():
    logging.info('Posting Unsubscribers to RE')

    # Check if there's anything to upload
    if unsubscribes_new.shape[0] != 0:

        # Load Records already uploaded in RE
        if os.path.exists('Databases/Unsubscribes.parquet'):
            unsubscribes_uploaded = pd.read_parquet('Databases/Unsubscribes.parquet')
        else:
            unsubscribes_uploaded = pd.DataFrame()

        # Iterate over rows
        for index, row in unsubscribes_new.iterrows():

            # Load Object to Dataframe
            row = pd.DataFrame(row)
            row = row.T.reset_index(drop=True).copy()

            # Get Email Address
            email = row['EMAIL (Primary Key)'].tolist()[0]

            # Get date
            date = row['Open time'].tolist()[0]

            if pd.isnull(date):
                date = row['Sent Date'].tolist()[0]

            date = pd.to_datetime(date, format='%Y-%m-%d %H:%M:%S')
            date = date.isoformat()

            # Get RE IDs associated with that email
            re_ids = re_email_list[re_email_list['address'] == email]['constituent_id'].drop_duplicates().tolist()

            # Loop over each unique RE ID
            for re_id in re_ids:

                # Opt-out
                params = {
                    'constituent_id': re_id,
                    'channel': 'Email',
                    'category': 'Netcore Email Marketing',
                    'source': 'Netcore',
                    'consent_date': date,
                    'constituent_consent_response': 'OptOut',
                    'consent_statement': email + ': ' + row['Subject'].tolist()[0] + ' | ' + row['Unsub reason'].tolist()[0]
                }

                url = 'https://api.sky.blackbaud.com/commpref/v1/consent/consents'

                # Post Data to RE
                post_request_re(url, params)

                # Update the Dataframe
                unsubscribes_uploaded = pd.concat([unsubscribes_uploaded, row], ignore_index=True)

        # Update Database of one marked as unsubscribed in RE
        unsubscribes_uploaded.to_parquet('Databases/Unsubscribes.parquet')

def post_bounces_to_re():
    logging.info('Marking Inactive Emails in RE')

    # Check if there's anything to upload
    if hard_bounces_new.shape[0] != 0:

        # Load Records already uploaded in RE
        if os.path.exists('Databases/Hard Bounces.parquet'):
            hard_bounces_uploaded = pd.read_parquet('Databases/Hard Bounces.parquet')
        else:
            hard_bounces_uploaded = pd.DataFrame()

        # Iterate over rows
        for index, row in hard_bounces_new.iterrows():

            # Load Object to DataFrame
            row = pd.DataFrame(row)
            row = row.T.reset_index(drop=True).copy()

            # Get Email Address
            email = row['EMAIL (Primary Key)'].tolist()[0]

            # Get RE IDs associated with that email
            email_address_ids = re_email_list[re_email_list['address'] == email]['id'].drop_duplicates().tolist()

            # Loop over each unique Email Address ID
            for email_address_id in email_address_ids:

                # Mark as Inactive
                params = {
                    'inactive': True,
                    'primary': False
                }

                url = f'https://api.sky.blackbaud.com/constituent/v1/emailaddresses/{email_address_id}'

                # Post Data to RE
                patch_request_re(url, params)

                # Update the Dataframe
                hard_bounces_uploaded = pd.concat([hard_bounces_uploaded, row], ignore_index=True)

        # Update Database of one marked as unsubscribed in RE
        hard_bounces_uploaded.to_parquet('Databases/Hard Bounces.parquet')

try:

    # Start Logging for Debugging
    start_logging()

    # Set current directory
    set_current_directory()

    # Retrieve contents from .env file
    get_env_variables()

    # Set API Request strategy
    set_api_request_strategy()

    # Get RE Email List
    re_email_list = load_data('Databases/Email List.parquet').copy()

    # Load Netcore's Data
    netcore = load_data('Databases/Netcore Data.parquet').copy()

    # Get Unsubscribes
    unsubscribes = get_unsubscribes().copy()

    # Identify Unsubscribes yet to upload in RE
    unsubscribes_new = identify_unsubscribes().copy()

    # Upload Unsubscribes data to RE
    post_unsubscribes_to_re()

    # Get Hard Bounces
    hard_bounces = get_hard_bounces().copy()

    # Identify Bounces yet to upload in RE
    hard_bounces_new = identify_hard_bounces().copy()

    # Upload Hard Bounces data to RE
    post_bounces_to_re()

except Exception as Argument:

    logging.error(Argument)
    send_error_emails('Error while uploading unsubscribes and bounces | Netcore Sync')

finally:

    # Stop Logging
    stop_logging()

    exit()