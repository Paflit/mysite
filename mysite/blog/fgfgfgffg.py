import pandas as pd
excel_file = r'C:\Users\yhate\Downloads\rating.xlsx'
if excel_file.endswith('.xls') or excel_file.endswith('.xlsx'):
    df = pd.read_excel(excel_file)
    for index, row in df.iterrows():
        number=row['Место в рейтинге']
        last_name=row['Фамилия']
        first_name=row['Имя']
        middle_name=row['Отчество']
        job_title=row['Должность']
        department=row['Место работы']
        score=row['Итоговая оценка']
print(len(df['Должность'].unique()))
