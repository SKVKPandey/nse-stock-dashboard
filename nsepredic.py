from nsetools import Nse
import yfinance as yf
from urllib.request import urlopen
#import os
import numpy as np
import pandas as pd
#import _thread as th
#import time
from datetime import datetime, timedelta
#from PIL import Image, ImageTk
#from matplotlib.figure import Figure
#from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import streamlit as st
from streamlit_autorefresh import st_autorefresh
import plotly.graph_objs as go
import plotly.express as px
#import matplotlib.pyplot as plt
#from pprint import pprint

class stockNSE():

    def __init__(self):
        self.nifty50Symbol = self.niftynext50Symbol = self.niftymidcap50Symbol = self.niftybankSymbol = self.niftyfinanceSymbol = None
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        if (now.strftime("%A") not in ['Saturday', 'Sunday']) and (
                float(current_time[:2] + '.' + current_time[3:5]) >= 9.0 and float(
            current_time[:2] + '.' + current_time[3:5]) < 15.30):
            # update every 1 mins
            st_autorefresh(interval=0.5 * 60 * 1000, key="datarefresh")
        self.ReadSymbol()
        self.topGainerdf, self.topLooserdf = self.fetchDataGainerLooser()

    def ReadSymbol(self):
        url = 'https://archives.nseindia.com/content/indices/ind_nifty50list.csv'
        fs = urlopen(url)
        self.nifty50Symbol = pd.read_csv(fs)
        #self.nifty50Symbol = df['Symbol'].tolist()

        url = 'https://archives.nseindia.com/content/indices/ind_niftynext50list.csv'
        fs = urlopen(url)
        self.niftynext50Symbol = pd.read_csv(fs)
        #self.niftynext50Symbol = df['Symbol'].tolist()
        # print(self.niftynext50Symbol)

        url = 'https://archives.nseindia.com/content/indices/ind_niftymidcap50list.csv'
        fs = urlopen(url)
        self.niftymidcap50Symbol = pd.read_csv(fs)
        #self.niftymidcap50Symbol = df['Symbol'].tolist()
        # print(self.niftymidcap50Symbol)

        url = 'https://archives.nseindia.com/content/indices/ind_niftybanklist.csv'
        fs = urlopen(url)
        self.niftybankSymbol  = pd.read_csv(fs)
        #self.niftybankSymbol = df['Symbol'].tolist()

        url = 'https://archives.nseindia.com/content/indices/ind_niftyfinancelist.csv'
        fs = urlopen(url)
        self.niftyfinanceSymbol = pd.read_csv(fs)
        #self.niftyfinanceSymbol = df['Symbol'].tolist()

        '''
        df = pd.DataFrame(data=None, columns=['Symbol', 'Name'])
        all_stock_codes = Nse_data.get_stock_codes(cached=False)
        for key in all_stock_codes:
            if 'BANK' in all_stock_codes[key].upper():
                df = df.append({'Symbol': key, 'Name': all_stock_codes[key]}, ignore_index=True)
        self.niftyBankSymbol = df['Symbol'].tolist()
        '''

    '''
    def startThread(self, s='nifty50'):
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        if (now.strftime("%A") not in ['Saturday', 'Sunday']) and (
                float(current_time[:2] + '.' + current_time[3:5]) >= 9.0 and float(
            current_time[:2] + '.' + current_time[3:5]) < 15.30):
            th.start_new_thread(fetchForB, (s,))
            th.start_new_thread(fetchData, (s,))
        else:
            self.fetchT = self.fetchDataGainer(s)
            self.fetchL = self.fetchDataLooser(s)

    def fetchData(self, s='nifty50'):
        self.fetchT = self.fetchDataGainer(s)
        self.fetchL = self.fetchDataLooser(s)
        self.fetchInfo = fetchForB(s)
        time.sleep(30)
    '''

    def fetchData(self, s='nifty 50'):
        loopsymbol=[]
        if s == 'nifty 50':
            loopsymbol = self.nifty50Symbol['Symbol'].tolist()
        elif s == 'nifty next 50':
            loopsymbol = self.niftynext50Symbol['Symbol'].tolist()
        elif s == 'nifty midcap 50':
            loopsymbol = self.niftymidcap50Symbol['Symbol'].tolist()
        elif s == 'nifty bank':
            loopsymbol = self.niftybankSymbol['Symbol'].tolist()
        elif s == 'nifty finance':
            loopsymbol = self.niftyfinanceSymbol['Symbol'].tolist()

        #pprint(self.niftybankSymbol['Symbol'].tolist())
        ydata = pd.DataFrame()
        with st.spinner("Wait!!!    Data Fetching...."):
            for x in loopsymbol:
                q = Nse_data.get_quote(x)
                q = {k: [v] for k, v in q.items()}
                q = pd.DataFrame(q)
                q = q[['symbol', 'companyName', 'open', 'dayHigh', 'dayLow', 'previousClose', 'lastPrice', 'change',
                   'pChange','totalTradedVolume', 'totalTradedValue', 'high52', 'low52']]
                #print(type(q))
                ydata = ydata.append(q, ignore_index=True)

        ydata['pChange'] = pd.to_numeric(ydata['pChange'], errors='coerce')
        ydata = ydata.sort_values(by=['pChange'], ascending=False)
        ydata.reset_index(drop=True)
        ydata.set_index('symbol', inplace=True)
        return ydata[ydata['pChange'] > 0].head(20), ydata[ydata['pChange'] < 0].tail(20)

    def fetchDataGainerLooser(self, s='nifty50'):
        dfGainer = Nse_data.get_top_gainers()
        dfGainer = pd.DataFrame(dfGainer)
        dfGainer = dfGainer[['symbol', 'ltp', 'netPrice', 'tradedQuantity']]

        top_looser = Nse_data.get_top_losers()
        dfLooser = pd.DataFrame(top_looser)
        dfLooser = dfLooser[['symbol', 'ltp', 'netPrice', 'tradedQuantity']]
        if s == 'nifty 50':
            dfGainer = dfGainer[dfGainer['symbol'].isin(self.nifty50Symbol['Symbol'].tolist())]
            dfLooser = dfLooser[dfLooser['symbol'].isin(self.nifty50Symbol['Symbol'].tolist())]
        elif s == 'nifty next 50':
            dfGainer = dfGainer[dfGainer['symbol'].isin(self.niftynext50Symbol['Symbol'].tolist())]
            dfLooser = dfLooser[dfLooser['symbol'].isin(self.niftynext50Symbol['Symbol'].tolist())]
        elif s == 'nifty midcap 50':
            dfGainer = dfGainer[dfGainer['symbol'].isin(self.niftymidcap50Symbol['Symbol'].tolist())]
            dfLooser = dfLooser[dfLooser['symbol'].isin(self.niftymidcap50Symbol['Symbol'].tolist())]
        elif s == 'nifty bank':
            dfGainer = dfGainer[dfGainer['symbol'].isin(self.niftybankSymbol['Symbol'].tolist())]
            dfLooser = dfLooser[dfLooser['symbol'].isin(self.niftybankSymbol['Symbol'].tolist())]
        elif s == 'nifty finance':
            dfGainer = dfGainer[dfGainer['symbol'].isin(self.niftyfinanceSymbol['Symbol'].tolist())]
            dfLooser = dfLooser[dfLooser['symbol'].isin(self.niftyfinanceSymbol['Symbol'].tolist())]
        dfGainer.reset_index(drop=True)
        dfGainer.set_index('symbol', inplace=True)
        dfLooser.reset_index(drop=True)
        dfLooser.set_index('symbol', inplace=True)
        return dfGainer, dfLooser

    def get_specificdataframe(self, ticker=''):
        ydata=pd.DataFrame()
        with st.spinner('Wait for Data loading...'):
            if ticker == '^NSEI' or ticker=='^CNX100' or ticker == '^NSMIDCP'  or ticker == '^NSEMDCP50' or ticker == '^NSEBANK' :
                if self.topGainerdf.empty:
                    return pd.DataFrame(columns=['companyName','open', 'dayHigh', 'dayLow', 'previousClose', 'lastPrice', 'change','pChange','totalTradedVolume', 'totalTradedValue', 'high52', 'low52'])
                else:
                    '''
                    if ticker == '^NSEI':
                        loopsymbol = self.niftynext50Symbol
                    elif ticker == '^CNX100':
                        loopsymbol = self.nifty100Symbol
                    elif ticker == '^NSMIDCP':
                        loopsymbol = self.niftynext50Symbol
                    elif ticker == '^NSEMDCP50':
                        loopsymbol = self.niftymidcap50Symbol
                    elif ticker == '^NSEBANK':
                        loopsymbol = self.niftyBankSymbol
                    '''
                    #for x in self.nifty50Symbol:
                    for x in self.topGainerdf['SYMBOL']:
                        q = Nse_data.get_quote(x)
                        q = {k: [v] for k, v in q.items()}
                        q = pd.DataFrame(q)
                        q = q[['symbol', 'companyName', 'open', 'dayHigh', 'dayLow', 'previousClose', 'lastPrice', 'change','pChange','totalTradedVolume', 'totalTradedValue', 'high52', 'low52']]
                        #print(type(q))
                        ydata = ydata.append(q, ignore_index=True, sort=True)
                        '''
                        q = yf.download(tickers=x+'.NS', period='1d', interval='1m').tail(1)
                        q['Symbol'] = x
                        ydata = ydata.append(q, ignore_index=True, sort=True)
                        '''
            else:
                q = Nse_data.get_quote(ticker)
                q = {k: [v] for k, v in q.items()}
                q = pd.DataFrame(q)
                q = q[['symbol', 'companyName', 'open', 'dayHigh', 'dayLow', 'previousClose', 'lastPrice', 'change', 'pChange',
                       'totalTradedVolume', 'totalTradedValue', 'high52', 'low52']]
                # print(type(q))
                ydata = ydata.append(q, ignore_index=True, sort=True)
                '''
                q = yf.download(tickers=x+'.NS', period='1d', interval='1m').tail(1)
                q['Symbol'] = x
                ydata = ydata.append(q, ignore_index=True, sort=True)
                '''
        ydata = ydata.sort_values(by=['pChange'], ascending=False)
        #ydata = ydata.sort_values(by=['High'], ascending=False)
        ydata.reset_index(drop=True)
        ydata.set_index('symbol', inplace=True)
        #ydata.set_index('Symbol', inplace=True)
        return ydata.head(10)

    def create_dataset(self, dataset, timestep=1):
        dataX, dataY = [], []
        for i in range(len(dataset) - timestep - 1):
            dataX.append(dataset[i:(i + timestep), 0])
            dataY.append(dataset[(i + timestep), 0])
        return np.array(dataX), np.array(dataY)

    def widget(self):
        #st.set_page_config(
            #page_title="NSE Stock Market",
            #layout='wide'
            # initial_sidebar_state="expanded",
        #)

        st.sidebar.markdown("## STOCK PREDICTION")
        st.sidebar.markdown("You can **Select** any one Symbols to *Predict*.")
        gn = st.sidebar.radio('',
                              options=('NIFTY 50', 'NIFTY NEXT 50', 'NIFTY MIDCAP 50', 'NIFTY BANK', 'NIFTY FINANCE'))
        symbols = ['Select Symbols']
        if gn == 'NIFTY 50':
            symbols.extend(self.nifty50Symbol['Symbol'].tolist())
        elif gn == 'NIFTY NEXT 50':
            symbols.extend(self.niftynext50Symbol['Symbol'].tolist())
        elif gn == 'NIFTY MIDCAP 50':
            symbols.extend(self.niftymidcap50Symbol['Symbol'].tolist())
        elif gn == 'NIFTY BANK':
            symbols.extend(self.niftybankSymbol['Symbol'].tolist())
        elif gn == 'NIFTY FINANCE':
            symbols.extend(self.niftyfinanceSymbol['Symbol'].tolist())
        Ticker = st.sidebar.selectbox('', options=symbols)



        _, col1, col2, col3, _ = st.columns([1, 2, 11, 2, 1])
        #col1.image('nse-logo.png')
        col2.title('Stock Market')

        with st.form('form1'):
            _, lcol1, lcol2, lcol3, lcol4, lcol5, _ = st.columns([1, 2, 2, 2, 2, 3, 1])
            with lcol1:
                with st.container():
                    nifty50DailyQuote = Nse_data.get_index_quote("nifty 50")
                    print(nifty50DailyQuote)
                    # nifty50DailyQuote=yf.Ticker('^NSEI').info
                    # if (nifty50DailyQuote['regularMarketPrice']-nifty50DailyQuote['regularMarketPreviousClose'])/nifty50DailyQuote['regularMarketPreviousClose']*100 >0 :

                    if float(nifty50DailyQuote['pChange']) > 0:
                        txtcolor = 'color:green'
                        imagetxt = '<i class="fa fa-caret-up" style="font-size:20px;color:green;"></i>'
                    else:
                        txtcolor = 'color:red'
                        imagetxt = '<i class="fa fa-caret-down" style="font-size:20px;color:red;"></i>'

                    # txt = f'''<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css"> \
                    #    <p align='center'><font size="4" style="{txtcolor}">NIFTY 50</font><br />{str(nifty50DailyQuote['regularMarketPrice'])} \
                    #    <br />{str(round((nifty50DailyQuote['regularMarketPrice']-nifty50DailyQuote['regularMarketPreviousClose']),2))} \
                    #    ({str(round(((nifty50DailyQuote['regularMarketPrice']-nifty50DailyQuote['regularMarketPreviousClose'])/ nifty50DailyQuote['regularMarketPreviousClose']*100),2))}%  {imagetxt})</p>'''

                    txt = f'''<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css"> \
                        <p align='center'><font size="4" style="{txtcolor}">NIFTY 50</font><br />{str(nifty50DailyQuote['lastPrice'])} \
                        <br />{str(nifty50DailyQuote['change'])} ({str(nifty50DailyQuote['pChange'])}%  {imagetxt})</p>'''

                    st.markdown(txt, unsafe_allow_html=True)
                    B1 = st.form_submit_button("NIFTY 50")
                    if B1:
                        self.topGainerdf, self.topLooserdf = self.fetchData('nifty 50')
                        Ticker = 'Select Symbols'

            with lcol2:
                niftynext50DailyQuote = Nse_data.get_index_quote("nifty next 50")
                if float(niftynext50DailyQuote['pChange']) > 0:
                    txtcolor = 'color:green'
                    imagetxt = '<i class="fa fa-caret-up" style="font-size:20px;color:green;"></i>'
                else:
                    txtcolor = 'color:red'
                    imagetxt = '<i class="fa fa-caret-down" style="font-size:20px;color:red;"></i>'
                txt = f'''<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css"> \
                    <p align='center'><font size="4" style="{txtcolor}">NIFTY NEXT 50</font><br />{str(niftynext50DailyQuote['lastPrice'])} \
                    <br />{str(niftynext50DailyQuote['change'])} ({str(niftynext50DailyQuote['pChange'])}%  {imagetxt})</p>'''

                st.markdown(txt, unsafe_allow_html=True)
                B2 = st.form_submit_button("NIFTY NEXT 50")
                if B2:
                    self.topGainerdf, self.topLooserdf = self.fetchData('nifty next 50')
                    Ticker = 'Select Symbols'

            with lcol3:
                niftymidcap50DailyQuote = Nse_data.get_index_quote("nifty midcap 50")
                if float(niftymidcap50DailyQuote['pChange']) > 0:
                    txtcolor = 'color:green'
                    imagetxt = '<i class="fa fa-caret-up" style="font-size:20px;color:green;"></i>'
                else:
                    txtcolor = 'color:red'
                    imagetxt = '<i class="fa fa-caret-down" style="font-size:20px;color:red;"></i>'

                txt = f'''<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css"> \
                    <p align='center'><font size="4" style="{txtcolor}">NIFTY MIDCAP 50</font><br />{str(niftymidcap50DailyQuote['lastPrice'])} \
                    <br />{str(niftymidcap50DailyQuote['change'])} ({str(niftymidcap50DailyQuote['pChange'])}% {imagetxt})</p>'''
                st.markdown(txt, unsafe_allow_html=True)
                B3 = st.form_submit_button("NIFTY MIDCAP 50")
                if B3:
                    self.topGainerdf, self.topLooserdf = self.fetchData('nifty midcap 50')
                    Ticker = 'Select Symbols'

            with lcol4:
                niftyBankDailyQuote = Nse_data.get_index_quote("NIFTY BANK")
                if float(niftyBankDailyQuote['pChange']) > 0:
                    txtcolor = 'color:green'
                    imagetxt = '<i class="fa fa-caret-up" style="font-size:20px;color:green;"></i>'
                else:
                    txtcolor = 'color:red'
                    imagetxt = '<i class="fa fa-caret-down" style="font-size:20px;color:red;"></i>'

                txt = f'''<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css"> \
                    <p align='center'><font size="4" style="{txtcolor}">NIFTY BANK</font><br />{str(niftyBankDailyQuote['lastPrice'])} \
                    <br />{str(niftyBankDailyQuote['change'])} ({str(niftyBankDailyQuote['pChange'])}% {imagetxt})</p>'''
                st.markdown(txt, unsafe_allow_html=True)
                B4 = st.form_submit_button("NIFTY BANK")
                if B4:
                    self.topGainerdf, self.topLooserdf = self.fetchData('nifty bank')
                    Ticker = 'Select Symbols'

            with lcol5:
                print(Nse_data.get_index_list())
                niftyfinanceDailyQuote = Nse_data.get_index_quote("nifty fin service")
                print(niftyfinanceDailyQuote)
                if float(niftyfinanceDailyQuote['pChange']) > 0:
                    txtcolor = 'color:green'
                    imagetxt = '<i class="fa fa-caret-up" style="font-size:20px;color:green;"></i>'
                else:
                    txtcolor = 'color:red'
                    imagetxt = '<i class="fa fa-caret-down" style="font-size:20px;color:red;"></i>'

                txt = f'''<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css"> \
                    <p align='center'><font size="4" style="{txtcolor}">NIFTY FINANCIAL SERVICES</font><br />{str(niftyfinanceDailyQuote['lastPrice'])} \
                    <br />{str(niftyfinanceDailyQuote['change'])} ({str(niftyfinanceDailyQuote['pChange'])}% {imagetxt})</p>'''

                st.markdown(txt, unsafe_allow_html=True)
                B5 = st.form_submit_button("NIFTY FINANCIAL SERVICES")
                if B5:
                    self.topGainerdf, self.topLooserdf = self.fetchData('nifty finance')
                    Ticker = 'Select Symbols'


        self.topG, self.topL = st.columns([4, 2])
        ticker = '^NSEI'
        titles = 'NIFTY 50 live Price'
        with self.topG:
            if B1:
                ticker = '^NSEI'
                titles = 'NIFTY 50 live Price'
            elif B2:
                ticker = '^CNX100'
                titles = 'NIFTY 100 live Price'
            elif B3:
                ticker = '^NSMIDCP'
                titles = 'NIFTY NEXT 50 live Price'
            elif B4:
                ticker = '^NSEMDCP50'
                titles = 'NIFTY MICAD CAP live Price'
            elif B5:
                ticker = '^NSEBANK'
                titles = 'NIFTY BANK live Price'

            # Interval required 1 minute
            ydata = yf.download(tickers=ticker, period='1d', interval='1m')

            cdata = pd.DataFrame({'OPEN': ydata['Open'], 'HIGH': ydata['High'], 'LOW': ydata['Low']}).tail(1)
            cdata.reset_index(drop=True, inplace=True)
            cdata.index = ('',)
            st.table(cdata.style.format("{:.2f}"))

            # declare figure
            fig = go.Figure()
            # Candlestick
            fig.add_trace(go.Candlestick(x=ydata.index,
                                         open=ydata['Open'],
                                         high=ydata['High'],
                                         low=ydata['Low'],
                                         close=ydata['Close'],
                                         name='market data'))
            # Add titles
            fig.update_layout(
                #title=titles,
                yaxis_title=titles, #'Stock Price',
                height=500,
                autosize=True,
                margin=dict(
                    l=10,
                    r=10,
                    b=30,
                    t=0,
                    pad=4
                ),
                #paper_bgcolor="LightSteelBlue",
            )
            # X-Axes
            fig.update_xaxes(
                rangeslider_visible=True
            )
            st.plotly_chart(fig, use_container_width=True)

        with self.topL:
            with st.container():
                st.subheader('TOP GAINER')
                if B1 or B2 or B3 or B4 or B5:
                    df = self.topGainerdf[['change', 'pChange', 'totalTradedVolume']]
                    df = df.rename(columns={'change':'LTP', 'pChange':'%CHNG','totalTradedVolume':'VOLUME' })
                else:
                    df = self.topGainerdf
                    df = df.rename(columns={'ltp': 'LTP', 'netPrice': '%CHNG', 'tradedQuantity': 'VOLUME'})
                st.table(df.head().style.set_precision(2))

            with st.container():
                st.subheader('TOP LOOSER')
                if B1 or B2 or B3 or B4 or B5:
                    df = self.topLooserdf[['change', 'pChange', 'totalTradedVolume']]
                    df.rename(columns={'change':'LTP', 'pChange':'%CHNG','totalTradedVolume':'VOLUME' })
                else:
                    df = self.topLooserdf
                    df.rename(columns={'ltp': 'LTP', 'netPrice': '%CHNG', 'tradedQuantity': 'VOLUME'})
                    st.table(df.head())
                #st.table(df.head().style.set_precision(2))

        if B1 or B2 or B3 or B4 or B5:
            dispDataDetails = st.container()
            with dispDataDetails:
                df = self.topGainerdf
                df=pd.DataFrame(df,columns = ['companyName','open', 'dayHigh', 'dayLow', 'previousClose', 'lastPrice', 'change','pChange','totalTradedVolume', 'totalTradedValue', 'high52', 'low52'])
                df = df.rename(columns={'companyName':'Company Name','open':'Open','dayHigh':'dHigh','dayLow':'dLow', 'previousClose':'pClose','pChange':'%Chg','totalTradedVolume':'tTVolume', 'totalTradedValue':'tTValue'})
                #print(df)
                st.table(df.style.set_precision(2))

        if Ticker != 'Select Symbols':
            start = '2011-01-01'
            end = datetime.today()
            #print(datetime.today())

            df = yf.download(tickers=Ticker+'.NS', start=start, end = end, interval='1d')

            actualData = df.reset_index()
            actualFig = px.line(actualData.tail(365), x="Date", y="Close", title='Last One Year Actual Data of ' + Ticker)
            #st.subheader()
            st.plotly_chart(actualFig, use_container_width=True)
            st.table(df.tail(10).style.set_precision(2))

            dfDate= df.index
            df1 = df.reset_index()['Close']
            #print(df1.shape)
            # Now Scaling the data for between 0 and 1 for LSTM
            from sklearn.preprocessing import MinMaxScaler  # pip install sklearn
            scaler = MinMaxScaler(feature_range=(0, 1))
            df1 = scaler.fit_transform(np.array(df1).reshape(-1, 1))
            #print(df1.shape)

            # Splitting dataset into train 65% and test 35%
            training_size = int(len(df1) * 0.65)
            test_size = len(df1) - training_size
            train_data, test_data = df1[0:training_size:], df1[training_size:len(df1),:1]
            #print(train_data, test_data)

            time_step = 100
            X_train, y_train = self.create_dataset(train_data, time_step)
            X_test, ytest = self.create_dataset(test_data, time_step)

            #print(X_train.shape)
            #print(y_train.shape)

            inputshape = X_train.shape[1]

            # reshape input data to be [samples, time step, features] which is required for LSTM
            X_train = X_train.reshape(X_train.shape[0], X_train.shape[1], 1)
            X_test = X_test.reshape(X_test.shape[0], X_test.shape[1], 1)

            from tensorflow.keras.models import Sequential
            from tensorflow.keras.layers import Dense, LSTM, Dropout

            model = Sequential()
            # Now Creating the various Layer
            model.add(LSTM(50, return_sequences=True, input_shape=(inputshape, 1)))
            model.add(Dropout(0.2))
            model.add(LSTM(50, return_sequences=True))
            model.add(Dropout(0.3))
            model.add(LSTM(50))
            #model.add(Dropout(0.4))
            # Now join/Connect all the Layers for ML
            model.add(Dense(units=1))  # units is 1 because predict  one column ie Close column

            #print(model.summary())
            model.compile(optimizer='adam', loss='mean_squared_error')

            with st.spinner('Wait System Generate the AI Maching Learing and Predict the Data'):
                model.fit(X_train, y_train, validation_data=(X_test, ytest), epochs=30, batch_size=64, verbose=1)

                # Making Predictions and check performance metrics
                train_predict = model.predict(X_train)
                test_predict = model.predict(X_test)

                # Transform to original form
                train_predict = scaler.inverse_transform(train_predict)
                test_predict = scaler.inverse_transform(test_predict)

                # Calculate RMSE (Root Mean Squared Error) performance metics
                import math
                from sklearn.metrics import mean_squared_error
                math.sqrt(mean_squared_error(y_train, train_predict))
                math.sqrt(mean_squared_error(ytest, test_predict))

                # Now Plotting
                # Shift train predictions for plotting
                look_back = time_step  # 100
                trainPredictedPlot = np.empty_like(df1)
                trainPredictedPlot[:, :] = np.nan
                trainPredictedPlot[look_back:len(train_predict) + look_back, :] = train_predict
                # Shift test predictions for plotting
                testPredictedPlot = np.empty_like(df1)
                testPredictedPlot[:, :] = np.nan
                testPredictedPlot[len(train_predict) + (look_back * 2) + 1 : len(df1) - 1, :] = test_predict

                #print(scaler.inverse_transform(df1).shape, trainPredictedPlot.shape, testPredictedPlot.shape, dfDate.shape)
                # declare figure for Plot baseline ie Actual, Trained Data and Test Predicted Data
                # Now Prediction of Next one Day
                # By Using test data of 35% calculate based on time_step

                x_input = test_data[len(test_data) - time_step:].reshape(1, -1)
                #print(x_input.shape)
                temp_input = list(x_input)
                temp_input = temp_input[0].tolist()

                # Similarly Algo for prediction of Next 30 days
                days = 30
                lst_output = []
                n_steps = time_step
                i = 0
                while (i < days):
                    if (len(temp_input) > n_steps):  # it will execute later for next 60 daya data
                        #print(temp_input)
                        x_input = np.array(temp_input[1:])
                        #print("{} day input {}".format(i, x_input))
                        x_input = x_input.reshape(1, -1)
                        x_input = x_input.reshape(1, n_steps, 1 )
                        # print(x_input)
                        yhat = model.predict(x_input, verbose=0)
                        #print("{} day output {}".format(i, yhat))
                        temp_input.extend(yhat[0].tolist())
                        temp_input = temp_input[1:]
                        # print(temp_input)
                        lst_output.extend(yhat.tolist())
                        i += 1
                    else:
                        # Firts it will execute and store last 100 ie based on time_step
                        x_input = x_input.reshape((1, n_steps, 1))
                        yhat = model.predict(x_input, verbose=0)
                        #print(yhat[0])
                        temp_input.extend(yhat[0].tolist())
                        #print(len(temp_input))
                        lst_output.extend(yhat.tolist())
                        i += 1
                #print(lst_output)

                tilldays = dfDate[len(dfDate) - time_step:]  # np.arange(1, (time_step + 1))
                predictdays = [dfDate[-1] + timedelta(days=i) for i in range(1, 31)]  # np.arange((time_step + 1), (time_step + days + 1))

                tillvalue = scaler.inverse_transform(df1[(len(df1) - time_step):]).reshape(-1, 1)
                tillvalue = pd.DataFrame(tillvalue)
                tillvalue = tillvalue.iloc[:, 0].values.tolist()

                predictvalue = pd.DataFrame(scaler.inverse_transform(lst_output))
                predictvalue = predictvalue.iloc[:, 0].values.tolist()

                dff = pd.DataFrame({'Date': tilldays, 'Amount': tillvalue, 'Context': 'Actual Data'})
                dff1 = pd.DataFrame({'Date': predictdays, 'Amount': predictvalue, 'Context': 'Predicted Data'})
                dff = dff.append(dff1, ignore_index=True)

                pe_fig = px.line(dff.tail(365), x="Date", y="Amount", color='Context')
                st.subheader('PREDICTION GRAPH FOR NEXT 30 Days of '+Ticker)
                st.plotly_chart(pe_fig, use_container_width=True)

                dff1 = dff1.tail(41)
                dff1 = dff1[['Date', 'Amount']]
                dff1 = dff1.head(10)
                dff1 = dff1.set_index('Date')
                dff1 = dff1.T
                '''
                st.markdown("""
                <style>
                table td:nth-child(1) {
                    display: none
                }
                table th:nth-child(1) {
                    display: none
                }
                </style>
                """, unsafe_allow_html=True)
                '''
                st.subheader('NEXT 10 Days Predictions of '+ Ticker)
                st.table(dff1)
                #st.table(dff1.style.set_precision(2))


if __name__ == '__main__':
    Nse_data = Nse()
    stockNSE().widget()
