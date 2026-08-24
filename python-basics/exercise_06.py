import json

class Formater:
    def format(self, title:str, rows:dict):
        raise NotImplementedError
    
class JsonFormatter(Formater):
    def format(self, title:str, rows: dict):
        new_dict = {"title": title, "rows": rows}
        new_dict_values = json.dumps(new_dict, indent=4)
        return new_dict_values

class TextFormatter(Formater):
    def format(self, title: str, rows: dict):
        text = f"title: {title} \n"
        row_text = ""
        for key, value in rows.items():
            row_text += f"{key}: {value}" + "\n"
        full_text = text + row_text
        return full_text
    
class ReportService:
    def __init__(self, formatter: Formater, title: str, rows: dict):
        self.formatter = formatter
        self.title = title
        self.rows = rows
    
    def report(self)-> str:
        return self.formatter.format(self.title, self.rows)
    
    
title1 = "person"
row1 = {"name": "Lalit", "age": "27"}

title2 = "developer"
row2 = {"loves":"python", "quality": "curious"}

report1 = ReportService(TextFormatter(), title=title1, rows=row1)
report2 = ReportService(JsonFormatter(), title=title2, rows=row2)

print(report1.report())
print(report2.report())