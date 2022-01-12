import streamlit as st
from matplotlib import pyplot as plt, dates as mdates
from sklearn.svm import SVR
import investpy
from datetime import datetime as dt
from datetime import date, timedelta
import matplotlib as mpl
label_size = 6




st.sidebar.header('User input')


def get_input():
    number_days=st.sidebar.text_input("Numero di giorni", "40")
    azione = st.sidebar.selectbox('Seleziona azione', ('ENI', 'ENEL', 'Terna', 'Intesa', 'Unicredit', 'Italgas', 'Leonardo', 'Generali'))

    return number_days, azione



def simbolo_azione(nome):
    if nome=="Terna":
        return "TRN"
    elif nome=="ENI":
        return "ENI"
    elif nome=="ENEL":
        return "ENEI"
    elif nome=="Intesa":
        return "ISP"
    elif nome=="Unicredit":
        return "CRDI"
    elif nome=="Italgas":
        return "IG"
    elif nome=="Leonardo":
        return "LDOF"
    elif nome=="Generali":
        return "GASI"

def changexlabelFrequency(values):
    pari = False if len(values) % 2 else True
    inc=1
    if pari==False:
        inc=0
    modxlabel=list()
    for i in values:
        if inc%2==0:
            modxlabel.append(i)
        else:
            modxlabel.append("")
        inc =inc+1  
    return modxlabel

def get_data(azione, number_days):
    azione_simb=simbolo_azione(azione)
    today = (date.today()).strftime('%d/%m/%Y')
    beforeTwoWeek = (date.today()-timedelta(days=int(number_days))).strftime('%d/%m/%Y')
    df_azioni = investpy.get_stock_historical_data(stock=azione_simb, country='Italy',from_date=beforeTwoWeek, to_date=today)   
    closed= df_azioni.loc[:,'Close']
    actual_price_azionid = float(closed.tail(1))
    
    #Tutti i dati tranne ultimo
    df_azioni=df_azioni.head(len(df_azioni)-1)
    days= list()
    adj_closes = list()
    df_azioni = df_azioni.reset_index()
    print(df_azioni.head())
    df_days=df_azioni.loc[:,'Date']
    df_adj_closes=df_azioni.loc[:,'Close']
    prev_actual_price_azionid = float(df_adj_closes.tail(1))


    for i in range(len(df_days)):
        days.append([i])
    for adj_close in df_adj_closes:
        adj_closes.append(float(adj_close))
    print(days)
    print(adj_closes)

    #Creazione 3 models
    lin_svr= SVR(kernel='linear', C=1000.0)
    lin_svr.fit(days, adj_closes)

    poly_svr= SVR(kernel='poly', C=1000.0, degree=3)
    poly_svr.fit(days, adj_closes)

    rbf_svr= SVR(kernel='rbf', C=1000.0, gamma=0.001)
    rbf_svr.fit(days, adj_closes)
    print(rbf_svr)

    #Plot
    
    st.header(f"""
    Regressione di: {azione}
    """)
    

    
    print(df_days)
    x_values=list()
    for d in df_days:
        x_values.append(d.strftime("%d-%m"))
    print(x_values)
    mpl.rcParams['xtick.labelsize'] = label_size 
    
    fig=plt.figure(figsize=(6,4))
    plt.scatter(x_values,adj_closes, s=10,color='blue', label='Chiusura')
    plt.plot(x_values,rbf_svr.predict(days), color='green', label='Gaussiana')
    plt.plot(x_values,poly_svr.predict(days), color='orange', label='Polinomile')
    plt.plot(x_values,lin_svr.predict(days), color='red', label='Lineare')
    plt.xticks(range(0,len(x_values)),changexlabelFrequency(x_values),rotation=45)
   
    plt.xlabel('Giorno')
    plt.ylabel('Prezzo')
    plt.xticks(rotation=45)
    plt.legend(loc=2, fontsize = 'x-small')
    
     #plt.show()
    st.pyplot(fig)

    day =[[len(df_azioni)]]
    daybefore =[[len(df_azioni)-1]]
    print(days)
    for i in days:
        print(i)
        print(rbf_svr.predict([i]))
    print(day)
    print(rbf_svr.predict(day))
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Gaussiana", f"{rbf_svr.predict(day)[0]:.2f}", f"{(rbf_svr.predict(day)[0]/rbf_svr.predict(daybefore)[0]-1)*100:.2f}%")
    col2.metric("Lineare",f"{lin_svr.predict(day)[0]:.2f}", f"{(lin_svr.predict(day)[0]/lin_svr.predict(daybefore)[0] -1)*100:.2f}%")
    col3.metric("Polinomiale",f"{poly_svr.predict(day)[0]:.2f}", f"{(poly_svr.predict(day)[0]/poly_svr.predict(daybefore)[0] -1)*100:.2f}%")
    col4.metric(f"Prezzo {today}",f"{actual_price_azionid:.2f}", f"{(actual_price_azionid/prev_actual_price_azionid -1)*100:.2f}%")

      

number_days, azione = get_input()
get_data(azione, number_days)
