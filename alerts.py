#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import telegram
import pandahouse
from datetime import date
import io
import sys
import os


# In[2]:


chat_id =  -652068442 #796299361
bot = telegram.Bot(token='5312807014:AAHzC6ssge6NsRskn-Ftnyx10kKJyR7T1_o')


# In[215]:


connection = {
    'host': 'https://clickhouse.lab.karpov.courses',
    'password': 'dpo_python_2020',
    'user': 'student',
    'database': 'simulator_20220520'
     }
    
q="""
select 
toStartOfFifteenMinutes(time) as ts
,toDate(time) as date
,formatDateTime(ts,'%R') as hm
,count(DISTINCT user_id) AS users_feed
,countIf(user_id, action='view') AS views
,countIf(user_id, action='like') AS likes
,countIf(user_id, action='like')/countIf(user_id,action='view') AS CTR
from simulator_20220520.feed_actions
where toDate(time)>=today()-1 and toDate(time)<toStartOfFifteenMinutes(now())
group by ts, date, hm
order by ts
"""
data_feed= pandahouse.read_clickhouse(q, connection=connection)


# In[227]:


connection_message = {
    'host': 'https://clickhouse.lab.karpov.courses',
    'password': 'dpo_python_2020',
    'user': 'student',
    'database': 'simulator_20220520'
     }
    
y="""
select
 toStartOfFifteenMinutes(time) as ts
,toDate(time) as date
,formatDateTime(ts,'%R') as hm
,count(DISTINCT user_id) AS users_message
FROM simulator_20220520.message_actions 
where toDate(time)>=today()-1 and toDate(time)<toStartOfFifteenMinutes(now())
group by ts, date, hm
ORDER BY ts
"""
data_message=pandahouse.read_clickhouse(y, connection=connection_message) 


# In[230]:

#Проверяем не последнюю 15 минутку, а 30 мин назад так как границы up и low текущем алгоритме для 15 минутки равны NaN
def check_anomaly(df, metric, a=3,n=5):
    
    df['mean']=df[metric].shift(1).rolling(n, min_periods=1).mean()
    df['std']=df[metric].shift(1).rolling(n, min_periods=1).std()
    

    df['up']=df['mean']+ a*df['std']
    df['low']=df['mean']-a*df['std']
    
    df['up']=df['up'].rolling(n,center=True).mean()
    df['low']=df['low'].rolling(n,center=True).mean()
    df['is_alert']=df.apply(lambda x: 1 if (x[metric] < x['low'] or x[metric] > x['up'] ) else 0, axis=1)
    
    
    current_value = df[metric].iloc[-3] 
    previous_value =df[metric].iloc[-4] 
    diff=(current_value/previous_value)-1
    
    #
    if  df['is_alert'].iloc[-3]==1:
        is_alert = 1
    else:
        is_alert = 0
    
    return is_alert, current_value, diff, df


# In[231]:


def run_alerts(metric,data):
    
    is_alert, current_value, diff, df = check_anomaly(data, metric) # проверяем метрику на аномальность алгоритмом, описаным внутри функции check_anomaly()
    
    if is_alert:
       
        msg="""Метрика {metric}:\nтекущее значение = {current_value:.2f}            \nотклонение от пред.значения {diff:.2%}            \nhttps://superset.lab.karpov.courses/superset/dashboard/882/"""            .format(metric=metric,current_value=current_value,diff=diff )

        sns.set(rc={'figure.figsize': (16, 10)}) # задаем размер графика
        plt.tight_layout()
        
        ax=sns.lineplot(x=df['ts'], y=df[metric], label='metric')
        ax=sns.lineplot(x=df['ts'], y=df['up'], label='up')
        ax=sns.lineplot(x=df['ts'], y=df['low'], label='low')
        
         
        ax.set(xlabel='time')
        ax.set(ylabel=metric)    
        
        ax.set_title('{}'.format(metric)) # задае заголовок графика
        ax.set(ylim=(0, None)) # задаем лимит для оси У

        # формируем файловый объект
        plot_object = io.BytesIO()
        ax.figure.savefig(plot_object)
        plot_object.seek(0)
        plot_object.name = '{0}.png'.format(metric)
        plt.close()

        # отправляем алерт
        bot.sendMessage(chat_id=chat_id, text=msg)
        bot.sendPhoto(chat_id=chat_id, photo=plot_object)


# In[233]:


metrics_list=['users_feed','views', 'likes', 'CTR']
for metric in metrics_list:
    try:
        run_alerts(metric,data_feed)
    except Exception as e:
         print(e)


# In[234]:


metrics_mes_list=['users_message']
for metric in metrics_mes_list:
    try:
        run_alerts(metric,data_message)
    except Exception as e:
         print(e)


# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:




