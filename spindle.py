import pandas as pd
import requests
from bs4 import BeautifulSoup
from sqlalchemy import create_engine
from datetime import datetime

login_url = 'http://192.168.1.99:8080/vmweb_AW/jsp/Login?se_kubun=kubun_003'
spindle_url = 'http://192.168.1.99:8080/vmweb_AW/jsp/RunningData?getJson={"mcno":"222","date":{"date":"20240213","shift":"2"}}'
spindle_site = 'http://192.168.1.99:8080/vmweb_AW/jsp/VM0201?MENUID=RunData&KINDID=Spindle&TYPEID=Standard&selectKey='
data = {
    's_UID': 'VM_SU',
    's_PWD': 'VM_DMC1_SU'
}

my_session = requests.Session()

# with requests.Session() as s:
#     response = s.post(login_url , data)
#     #print(response.text)
#     spindle_door=s.get('http://192.168.1.99:8080/vmweb_AW/jsp/VM0201?MENUID=RunData&KINDID=Spindle&TYPEID=Standard&selectKey=')
#     spindle_door_soup = BeautifulSoup(spindle_door.text, 'lxml')

#     spindle_page = s.get(spindle_url)
#     spindle_page_soup = BeautifulSoup(spindle_page.text, 'lxml')
    
def enter_spindle_site(url,url_data):
    response = my_session.post(url,url_data)
    return response

def prepare_soup(url):
    get_site = my_session.get(url)
    soup = BeautifulSoup(get_site.text,'lxml')
    return soup

def prepare_machine_url(mcno,dateshift):
    # declare mcno and dateshift
    # year + month + day
    dst = dateshift[2] + dateshift[1] + dateshift[0]
    shift = dateshift[3]
    date_url = f"\"date\":\"{dst}\",\"shift\":\"{shift}\""


    formatted = f"{{\"mcno\":\"{mcno}\",\"date\":{{{date_url}}}}}"
    machine_url = 'http://192.168.1.99:8080/vmweb_AW/jsp/RunningData?getJson={}'.format(formatted)
    return machine_url

def get_dateshift(soup):
    # find title of destination page
    # strong = soup.find("strong")
    # print(strong.text)
    dateshift = soup.find("option",selected=True)
    #15/Feb/2024-1
    # break to list
    dst = dateshift.text
    ds=[]   #[day,month,year,shift]
    ds.append(dst[0]+dst[1]) #day
    month = (dst[3]+dst[4]+dst[5]) #month
    # convert month from name to string number
    months = {'Jan':'01','Feb':'02','Mar':'03','Apr':'04','May':'05'
                ,'Jun':'06','Jul':'07','Aug':'08','Sep':'09','Oct':'10','Nov':'11',
                'Dec':'12'}
    ds.append(months[month])
    # year
    ds.append(dst[7]+dst[8]+dst[9]+dst[10])
    ds.append(dst[12])  #shift
    return ds

def get_dataframe(soup):
    # Obtain information from tag <table>
    table1 = soup.find("table", id="data-table")
    # find data row
    rows= table1.find("tbody").find_all("tr")
    # print(rows)
    data=[]
    for row in rows:#[1:]:
        cells = row.find_all("td")
        text = [cell.get_text(strip=True) for cell in cells]
        #print (text)
        data.append(text)

    column_names =['NoSpindle','SNo','Lot','AEF', 'SEF', 'DAS', 'YLW', 'YF_Y',
                    'MIS', 'RTI', 'JO_Y','NDOF','PRKG','DOF', 'NCOP']
    df = pd.DataFrame(data)
    df=df.drop(labels=0,axis=0)     #df= df.iloc[1:]
    #df.loc[0,16]=''
    df.columns=column_names
    return df

def data_spindle(mcno,dateshift):
     # take data
    machine_url = prepare_machine_url(mcno,dateshift)
    data_soup = prepare_soup(machine_url)
    df = get_dataframe(data_soup)
    df['INFO'] = dateshift[0]+"/"+dateshift[1]+"/"+dateshift[2]+"-"+dateshift[3]
    # fill No Machine into column SNo
    df['SNo'] = mcno
    return df

if __name__=="__main__":
    # enter to vm site
    enter_spindle_site(login_url,data)
    # take date shift information
    site_soup = prepare_soup(spindle_site)
    dateshift = get_dateshift(site_soup)
    print(dateshift)
    # take data
    # list machine
    # 1,2,3,4,5,6,23,31,32,33,34,210,211,212,213,214,216,219,222

    df1 = data_spindle('1',dateshift)
    df2 = data_spindle('2',dateshift)
    df3 = data_spindle('3',dateshift)
    df4 = data_spindle('4',dateshift)
    df5 = data_spindle('5',dateshift)
    df6 = data_spindle('6',dateshift)
    df23 = data_spindle('23',dateshift)
    df31 = data_spindle('31',dateshift)
    df32 = data_spindle('32',dateshift)
    df33 = data_spindle('33',dateshift)
    df34 = data_spindle('34',dateshift)
    df210 = data_spindle('210',dateshift)
    df211 = data_spindle('211',dateshift)
    df212 = data_spindle('212',dateshift)
    df213 = data_spindle('213',dateshift)
    df214 = data_spindle('214',dateshift)
    df216 = data_spindle('216',dateshift)
    df219 = data_spindle('219',dateshift)
    df222 = data_spindle('222',dateshift)

    frames = [df1,df2,df3,df4,df5,df6,df23,df31,df32,df33,df34,df210,df211,df212,df213,df214,df216,df219,df222]
    data = pd.concat(frames)

    print (data)

        
    # Create a SQLAlchemy engine to connect to the MySQL database
    engine = create_engine("mysql+mysqlconnector://dbuser:dbuser123@192.168.2.2/vmdb")
    # insert data spindle to database
    data.to_sql('vm_spindle_scrapes', con=engine, if_exists='append', index=False)
   
    print("VM data saved successfully at ",datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
   