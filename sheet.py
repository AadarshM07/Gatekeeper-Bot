import gspread
from google.oauth2.service_account import Credentials

class GoogleSheet:
    def __init__(self, sheet_name):
        scopes = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ]
        creds = Credentials.from_service_account_file("gatekeeper-463405-7c90c42b22ef.json", scopes=scopes)
        self.client = gspread.authorize(creds)
        self.sheet = self.client.open(sheet_name).sheet1 

    def get_all_records(self):
        return self.sheet.get_all_records()
    
    def find_in_column(self, value, number):
        col_values = self.sheet.col_values(number)
        for idx, cell_value in enumerate(col_values[1:], start=2):  
            if cell_value == value:
                return idx
        return None

    def find_user(self, discord_username):
        cell = self.sheet.find(discord_username)
        return cell.row if cell else None

    def get_row(self, row_number):
        return self.sheet.row_values(row_number)

if __name__ == "__main__":
    sheet = GoogleSheet("Gatekeeper")

    user_row = sheet.find_in_column("zay5507", 1)

    if user_row:
        print(f"User found at row: {user_row}")
        print(sheet.get_row(user_row))
    else:
        print("User not found.")