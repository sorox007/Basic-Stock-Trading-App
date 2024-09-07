import pandas as pd
import numpy as np
import sqlite3, requests 
from bs4 import BeautifulSoup
from nselib import capital_market
import matplotlib as mpl
import matplotlib.pyplot as plt
import mplfinance as mpf
from rich import print

import datetime




# Defining all the used classes

def initialize_tables():
    conn = sqlite3.connect('stocks.db')
    c = conn.cursor()
    #c.execute("""CREATE TABLE users(
    #          Name  TEXT,
    #          ID TEXT 
    #          )
    #          """)
    #c.execute("""CREATE TABLE accounts(
    #          ID  TEXT,
    #          Acc_no INTEGER,
    #          TYPE TEXT
    #          )
    #          """)
    #c.execute("""CREATE TABLE transactions(
    #          Acc_no INTEGER,
    #          Type TEXT
    #          Date TEXT,
    #          Amount REAL,
    #          Description TEXT
    #          )
    #          """)
    
    #c.execute("""CREATE TABLE stocks(
    #          stock_name TEXT,
    #          owner TEXT,
    #          value REAL,
    #          quantity INTEGER,
    #          Date TEXT
    #          )
    #          """)
    #stocks_table = pd.DataFrame()
    #conn.commit()
    #conn.close()
 

    

class User:

    def __init__(self,name,ID):
        self._name = name
        self._ID = ID

    @property
    def name(self):
        return self._name
    
    @name.setter
    def name(self,value):
        self._name = value

    @property
    def ID(self):
        return self._ID
    
    @ID.setter
    def ID(self,value):
        self._ID = value

    def save_entry(self):
        conn =  sqlite3.connect('stocks.db')
        c = conn.cursor()
        input_list =[(self.name,self.ID)]
        c.executemany("INSERT INTO users VALUES (?,?)",input_list)
        conn.commit()
        conn.close()



class Account:

    def __init__(self,acc_number,owner,type):
        self._acc_number = acc_number
        self._owner = owner
        self._type = type

    @property
    def acc_number(self):
        return self._acc_number
    
    @acc_number.setter
    def acc_number(self,value):
        self._acc_number = value

    @property
    def owner(self):
        return self._owner
    
    @owner.setter
    def ID(self,value):
        self._owner = value

    @property
    def type(self):
        return self._type
    
    @type.setter
    def type(self,value):
        self._type = value

    def save_entry(self):
        conn =  sqlite3.connect('stocks.db')
        c = conn.cursor()
        input_list =[(self.owner,self.acc_number,self.type)]
        c.executemany("INSERT INTO accounts VALUES (?,?,?)",input_list)
        conn.commit()
        conn.close()
    
    
def main():
    
    #user1 = User('Soumit','sorox')
    #conn = sqlite3.connect('stocks.db')
    #c = conn.cursor()
    #c.execute('select * from users')
    #print(c.fetchall())
    #user_making()
    account_making('sorox')

def user_making():
    name = input("Enter your name: -> ")
    ID = input("Enter your ID ->" )

    user1 = User(name,ID)
    user1.save_entry()

def account_making(ID):
    acc_1 = 91101
    acc_2 = 91102
    acc_1 = Account(acc_number= acc_1, owner=ID, type = 'Cash')
    acc_1.save_entry()
    acc_2 = Account(acc_number= acc_2, owner=ID, type = 'Equity')
    acc_2.save_entry()

def transaction_handler(user,stock_price,quantity):
    conn = sqlite3.connect('stocks.db')
    c = conn.cursor()
    
    c.execute(f"""select ID FROM users 
              where ID = '{user}'""")
    output = c.fetchall()
    print(output[0][0])
    conn.commit()
    conn.close()

def current_price_fetcher(stock):
    #ideal url f'https://www.google.com/finance/quote/{stock}:NSE'
    main_url = 'https://www.google.com/finance/quote/'

    get_url = f'{main_url}{stock}:NSE'

    response = requests.get(get_url)
    soup = BeautifulSoup(response.text,'html.parser')
    class_name = 'YMlKec fxKbKc'
    price = float(soup.find(class_ = class_name).text.strip()[1:].replace(',',''))

    return price

def stock_terminal(stock,user):
    price = current_price_fetcher(stock)
    print(f'current price of stock is -> {price}')
    print('Past week prices of the stock are')

    chart_plotter(stock)
    
    
    ch = input('Do you want to buy the stock?(Y/N) -> ')
    
    if ch.lower() == 'y':
        n = int(input('Enter amount of stocks to buy?'))
        net_amount = n*price

        print(f'Your transaction will amount to: {net_amount}')
        confirmation = input('Are you sure you want to buy the stock?(Y/N) ->') 
        if confirmation.lower() == 'y':
            # add to the stocks table
            stock_input(stock,user,price,n)
            print('Success')
    
    else:
        print('Alright... where do you wish to go? ->')
#main()
#transaction_handler('sorox')
#stock_terminal('SBIN')

def chart_plotter(stock):
    data = capital_market.price_volume_and_deliverable_position_data(symbol='SBIN',period='1M')
    data = data.dropna(axis=0)
    data = data[['Date','OpenPrice','HighPrice','LowPrice','ClosePrice']]
    data['Date'] = pd.to_datetime(data['Date'])
    data.columns = ['Date','open','high','low','close']
    data = data.set_index('Date')
    mpf.plot(data, type='candle')


def stock_input(name,owner,price,n):
    conn = sqlite3.connect('stocks.db')
    c = conn.cursor()
    #name = 'SBIN'
    #owner = 91101
    #value = 98.1
    #quantity = 3
    #date = '11-01-2024'
    input_string = f'''INSERT INTO stocks(
        stock_name, owner, value, quantity, Date) VALUES
        ('{name}','{owner}','{price}','{n}','{datetime.datetime.now(datetime.UTC)}')
    '''
    c.execute(input_string)
    conn.commit()
    conn.close()


#print(current_price_fetcher('SBIN','sorox'))
stock_terminal('SBIN','sorox')

def value_delta(x,df):
    old_price = df.iloc[x,2]
    new_price = df.iloc[x,6]
    raw_change = new_price - old_price
    delta = raw_change/old_price * 100
    
    return raw_change,delta



def portfolio():
    conn = sqlite3.connect('stocks.db')
    c = conn.cursor()
    c.execute('SELECT * FROM stocks')
    output = c.fetchall()
    df = pd.DataFrame(output,columns = ['Stock_name','ID','Unit_Price','Volume','Date'])
    #df.set_index(df.columns[0])
    #print(type(output))
    #print(df)
    net_price = df['Unit_Price']*df['Volume']
    #df = pd.concat([df,net_price],axis=1,join='inner')
    df = df.assign(Value = net_price)
    #print(df)    
    print(f'Net Value of Portfolio = {sum(df['Value'])}')
    current_price = np.array([current_price_fetcher(symbol) for symbol in df['Stock_name']])
    df = df.assign(current_price = current_price)
    print(df)
    raw_change,delta = value_delta(4,df)
    if raw_change<0:
        print(f'Change in price is [bold red]{raw_change} -> {delta}[/bold red]')
    else:
        print(f'Change in price is [bold green]{raw_change} -> {delta}[/bold green]')
    
portfolio()