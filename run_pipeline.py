from time import sleep
from scripts.data_ingestion import extract_data_from_api
from scripts.data_analysis import analyze

datapath = './data/morocco_flights.csv'

def execute_sequential_tasks():
    """Execute tasks one after another"""
    extract_data_from_api(datapath)
    sleep(1)
    analyze(datapath)

execute_sequential_tasks()

