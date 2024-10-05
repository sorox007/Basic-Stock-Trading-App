import pandas as pd
import numpy as np
import sqlite3, requests 
from bs4 import BeautifulSoup
from nselib import capital_market
import matplotlib as mpl
import matplotlib.pyplot as plt
import mplfinance as mpf
from rich import print
import questionary


import datetime
import random



# Defining all the used classes

def initialize_tables():
    conn = sqlite3.connect('stocks.db')
    c = conn.cursor()
    c.execute("""CREATE TABLE users(
              Name  TEXT,
              ID TEXT 
              )
              """)
    c.execute("""CREATE TABLE accounts(
              ID  TEXT,
              Acc_no INTEGER,
              TYPE TEXT
             )
              """)
    c.execute("""CREATE TABLE transactions(
              Acc_no INTEGER,
              Amount REAL,
              Date TEXT
              )
              """)
    
    c.execute("""CREATE TABLE stocks(
              stock_name TEXT,
              owner TEXT,
              value REAL,
              quantity INTEGER,
              Date TEXT
              )
              """)
    #stocks_table = pd.DataFrame()
    conn.commit()
    conn.close()
 


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
    
    

def user_making():
    name = input("Enter your name: -> ")
    ID = input("Enter your ID ->" )

    user1 = User(name,ID)
    user1.save_entry()
    account_making(ID)
    
    question = questionary.confirm('Do you want to add funds? ').ask()
    if question:
        adding_funds(ID)
    else:
        exit()
    

def account_making(ID):
    acc_1 = 1100000000 + random.randint(0,99999999)
    acc_2 = 2200000000 + random.randint(0,99999999)
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

def stock_terminal(ID):
    stock = input('Enter the symbol of the stock you are interested in -> ')
    price = current_price_fetcher(stock)
    print(f'current price of stock is -> {price}')
    print('Past week prices of the stock are')

    chart_plotter(stock)
    
    
    confirmation = questionary.confirm("Do you want to continue?").ask()
    
    if confirmation:
        n = int(input('Enter amount of stocks to buy?'))
        net_amount = n*price
        
        current_cash = total_cash(ID)

        print(f'Your transaction will amount to: {net_amount}')
        if current_cash < net_amount:
            print('[bold red] Sorry you do not have adequate funds[/bold red]')
            print(f'Your current cash is -> {current_cash}')
        else:
            print(f'Your current cash is -> {current_cash}')
            print(f'Remaining Balance = {current_cash-net_amount}')
            confirmation_ = questionary.confirm("Do you want to continue?").ask()
            if confirmation_:
                # add to the stocks table
                stock_input(stock,ID,price,n)
                
                print('Success')
    
    else:
        print('Alright... where do you wish to go? ->')


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



def value_delta(x,df):
    old_price = df.iloc[x,2]
    new_price = df.iloc[x,6]
    raw_change = new_price - old_price
    delta = raw_change/old_price * 100
    
    return raw_change,delta



def portfolio(ID):
    conn = sqlite3.connect('stocks.db')
    c = conn.cursor()
    c.execute(f'SELECT * FROM stocks where owner = "{ID}"')
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
    n = int(input('Check Price delta for which of the following? (Enter the index number) ->'))
    raw_change,delta = value_delta(n,df)
    if raw_change<0:
        print(f'Change in price is [bold red]{raw_change} -> {delta}[/bold red]')
    else:
        print(f'Change in price is [bold green]{raw_change} -> {delta}[/bold green]')
    

def transaction_handler(price,volume,ID):
    amt = price*volume
    conn = sqlite3.connect('stocks.db')
    c = conn.cursor()
    c.execute(f'SELECT Acc_no from accounts where ID ="{ID}" and Acc_no < 2200000000')
    cash_account = c.fetchall()[0][0]
    c.execute(f'SELECT Acc_no from accounts where ID ="{ID}" and Acc_no >= 2200000000')
    equity_account = c.fetchall()[0][0]
    #print(cash_account,equity_account)
    cash_string = f""" INSERT INTO transactions(
        Acc_no, Amount, Date)
        VALUES({cash_account},{-amt},'{datetime.datetime.now(datetime.UTC)}'
        )
    """
    c.execute(cash_string)
    equity_string = f""" INSERT INTO transactions(
        Acc_no, Amount, Date)
        VALUES({equity_account},{amt},'{datetime.datetime.now(datetime.UTC)}'
        )"""
    c.execute(equity_string)
    conn.commit()
    conn.close()
   
def adding_funds(ID):
    cash = float(input('How much funds would you like to add -> '))
    conn = sqlite3.connect('stocks.db')
    c = conn.cursor()
    c.execute(f'SELECT Acc_no from accounts where ID ="{ID}" and Acc_no < 2200000000')
    cash_account = c.fetchall()[0][0]
    cash_string = f""" INSERT INTO transactions(
        Acc_no, Amount, Date)
        VALUES({cash_account},{cash},'{datetime.datetime.now(datetime.UTC)}'
        )
    """
    c.execute(cash_string)
    conn.commit()
    conn.close()
     
def total_cash(ID):
    conn = sqlite3.connect('stocks.db')
    c = conn.cursor()
    c.execute(f'SELECT Acc_no from accounts where ID ="{ID}" and Acc_no < 2200000000')
    cash_account = c.fetchall()[0][0]
    c.execute(f'SELECT * FROM transactions where Acc_no ="{cash_account}"')
    table = c.fetchall()
    df = pd.DataFrame(table,columns=['Account_no','Amt','Date'])
    cash = sum(df['Amt'])
    return cash

def user_interface():
    question = questionary.confirm('Are you a new user? ').ask()
    if question:
        user_making()
    else:
        username = input('Enter your username -> ')
        choices = ['Portfolio','Buy Stocks','Add funds','Exit']
        choice = questionary.select('Where do you want to head to? ', choices=choices).ask()
        
        if choice == choices[-1]:
            exit()
        elif choice == choices[0]:
            portfolio(ID = username)
        elif choice=='Buy Stocks':
            stock_terminal(ID = username)
        elif choice == choices[2]:
            adding_funds(ID = username)
        else:
            raise ValueError('Wrong input')
            