import csv
import os

class DataManager:

    def __init__(self, filepath="pkd_diary.csv"):
        home_dir = os.path.expanduser("~")
        self.filepath = os.path.join(home_dir, filepath)

        self.headers = [
            "Date", "Sleep_Start", "Sleep_End", "Sleep_Hours",
            "Medication_Time", "Medication_Count",
            "Exercise_Type", "Exercise_Duration",
            "Symptom_Occurred", "Symptom_Count", "Symptom_Score",
            "Transition_Type", "Notes"
        ]
        self._initialize_file()

    def _initialize_file(self):

        if not os.path.exists(self.filepath):
            with open(self.filepath, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(self.headers)

    def save_entry(self, entry_data):

        all_data = self.load_all_data()

        date_exists = False
        for i, row in enumerate(all_data):
            if row.get('Date') == entry_data.get('Date'):
                all_data[i] = entry_data
                date_exists = True
                break

        if not date_exists:
            all_data.append(entry_data)

        all_data.sort(key=lambda x: x.get('Date', ''))

        with open(self.filepath, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=self.headers)
            writer.writeheader()
            writer.writerows(all_data)

    def load_all_data(self):

        if not os.path.exists(self.filepath):
            return []

        data = []
        with open(self.filepath, mode='r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                data.append(row)
        return data

    def get_entry_by_date(self, date_str):

        all_data = self.load_all_data()
        for row in all_data:
            if row.get('Date') == date_str:
                return row
        return None
