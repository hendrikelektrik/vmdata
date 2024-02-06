import requests
from bs4 import BeautifulSoup
import pandas as pd
from sqlalchemy import create_engine
from datetime import datetime

login_url = 'http://192.168.1.99:8080/vmweb_AW/jsp/Login?se_kubun=kubun_003'

data = {
    's_UID': 'VM_SU',
    's_PWD': 'VM_DMC1_SU'
}

with requests.Session() as s:
    response = s.post(login_url , data)
    #print(response.text)
    index_page= s.get('http://192.168.1.99:8080/vmweb_AW/jsp/VM0201?MENUID=RunData&KINDID=Machine&TYPEID=Standard&selectKey=')
   

#print(response.text)

# parser-lxml = Change html to Python friendly format
# Obtain page's information
soup = BeautifulSoup(index_page.text, 'lxml')
#print(soup)

# find title of destination page
strong = soup.find("strong")
print(strong.text)

shift = soup.find("option",selected=True)
print (shift.text)

# Obtain information from tag <table>
table1 = soup.find("table", id="data-table")

# # find header
# heads = table1.find("thead").find_all("tr")
# title_list = []
# for head in heads:
#     outs = head.find_all("th")
#     title = [out.get_text(strip=True) for out in outs]
#     title_list.append(title)
# print(title_list)

# find data row
rows= table1.find("tbody").find_all("tr")
# print(rows)
data=[]
for row in rows:#[1:]:
    cells = row.find_all("td")
    text = [cell.get_text(strip=True) for cell in cells]
    #print (text)
    data.append(text)


df = pd.DataFrame(data)
# drop column 24
df = df.drop(df.columns[24],axis=1)
# write date shift info to column 24
df[24]=shift.text

column_names =['NoMesin', 'SNo', 'AEF', 'SEF', 'DAS', 'YLW', 'YF_Y', 'MIS', 'RTI', 'NDOF', 'PRKG', 'DOF', 'NCOP', 'YEF',
                'YEFA', 'YEFB', 'FBE', 'FBEA', 'FBEB', 'SBE', 'SBEA', 'SBEB', 'NCTB', 'NT_T', 'INFO']

avg_column_names =['AVG', 'AEF', 'SEF', 'DAS', 'YLW', 'YF_Y', 'MIS', 'RTI', 'NDOF', 'PRKG', 'DOF', 'NCOP', 'YEF',
                'YEFA', 'YEFB', 'FBE', 'FBEA', 'FBEB', 'SBE', 'SBEA', 'SBEB', 'NCTB', 'NT_T', 'INFO','INFO2']
# obtain average value
df_avg=df.head(1)
df_avg.loc[0,24]=''
df_avg.loc[0,23]=shift.text
df_avg.columns=avg_column_names


df.columns=column_names
df=df.iloc[1:]



# Create a SQLAlchemy engine to connect to the MySQL database
engine = create_engine("mysql+mysqlconnector://dbuser:dbuser123@192.168.2.2/vmdb")
# insert data average to database
df_avg.to_sql('vm_avg_scrapes', con=engine, if_exists='append', index=False)
# # Convert the Pandas DataFrame to a format for MySQL table insertion
df.to_sql('vm_scrapes', con=engine, if_exists='append', index=False)
# print(df_avg)
# print(df)
print("VM data saved successfully at ",datetime.now().strftime("%Y-%m-%d %H:%M:%S"))