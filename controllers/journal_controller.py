from models.month import Month
from data_access.journal_data import JournalData
from datetime import *
from dateutil.relativedelta import *

class JournalController():
    def __init__(self):
        self.journal_data = JournalData()
        self.current_date = self.initialize_date() # date object with day, month, year attributes
        self.month = self.get_month()
        
    def initialize_date(self):
        today = date.today()
        return today

    def get_month(self):
        month = Month(self.current_date, self.journal_data)
        return month
    
    def increase_month(self):
        self.current_date = self.current_date+relativedelta(days =+ 1)
        
