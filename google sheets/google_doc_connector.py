from __future__ import print_function
import os.path
import pickle
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

from src.database_manager import session_maker, get_patent, get_all_patents

SAMPLE_RANGE_NAME = 'List1!A2:E246'


class GoogleSheet:
    SPREADSHEET_ID = '1vzs7EgqCFwwjtb9TfuehPW4kHL_lznI13y67xbx3tm4'
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
    service = None

    def __init__(self):
        creds = None
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                print('flow')
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', self.SCOPES)
                creds = flow.run_local_server(port=0)
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)

        self.service = build('sheets', 'v4', credentials=creds)

    def updateRangeValues(self, range, values):
        data = [{
            'range': range,
            'values': values
        }]
        body = {
            'valueInputOption': 'USER_ENTERED',
            'data': data
        }
        result = self.service.spreadsheets().values().batchUpdate(spreadsheetId=self.SPREADSHEET_ID,
                                                                  body=body).execute()
        print('{0} cells updated.'.format(result.get('totalUpdatedCells')))


def convert_postgres_to_google():
    gs = GoogleSheet()
    range = 'List1!A2:G'
    values = []
    with session_maker() as session:
        patents = get_all_patents(session)

        for patent in patents:
            valid_patent = (str(patent[0].id),
                            str(patent[0].document_number),
                            patent[0].publication_date.strftime('%Y-%m-%d'),
                            str(patent[0].patent_title),
                            str(patent[0].applicant[0]),
                            str(patent[0].patent_owner[0]),
                            str(patent[0].international_patent_classification[0]))
            values.append(valid_patent)
    gs.updateRangeValues(range, values)


if __name__ == '__main__':
    convert_postgres_to_google()