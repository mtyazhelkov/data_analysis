#!/usr/bin/env python
# coding: utf-8

# In[59]:


import telegram
import pandas as pd
import pandahouse


# In[60]:


bot=telegram.Bot(token='5312807014:AAHzC6ssge6NsRskn-Ftnyx10kKJyR7T1_o')


# In[61]:


chat_id= -715060805


# In[62]:


#строка подключения к feed_actions
connection = {
    'host': 'https://clickhouse.lab.karpov.courses',
    'password': 'dpo_python_2020',
    'user': 'student',
    'database': 'simulator_20220520.feed_actions'
}


# In[63]:


q="""
select toDate(time) as date,
count(DISTINCT user_id) AS users,
countIf(user_id, action='view') AS views,
countIf(user_id, action='like') AS like,
countIf(user_id, action='like')/countIf(user_id,action='view') AS CTR
from simulator_20220520.feed_actions 
where toDate(time)>=today()-7 and toDate(time)<today()
group by  toDate(time)
order by  toDate(time)
"""
data_daily= pandahouse.read_clickhouse(q, connection=connection) 


# In[64]:


from datetime import datetime
data_daily['date2']=data_daily['date'].map(lambda x: x.date())
data_yesterday=data_daily.iloc[[6]]


# In[65]:


#строка подключения к message_actions
connection_message = {
    'host': 'https://clickhouse.lab.karpov.courses',
    'password': 'dpo_python_2020',
    'user': 'student',
    'database': 'simulator_20220520.message_actions'
}


# In[66]:


y="""
select toDate(time) as date,
count(DISTINCT user_id) AS users
FROM simulator_20220520.feed_actions as t1
JOIN simulator_20220520.message_actions as t2 on t1.user_id=t2.user_id
where toDate(time)>=today()-7 and toDate(time)<today()
GROUP BY toDate(time)
ORDER BY toDate(time)
"""
data_news_mes= pandahouse.read_clickhouse(y, connection=connection_message) 


# In[67]:


data_nm_yesterday=data_news_mes.iloc[[6]]


# In[68]:


msg=f"Метрики (лента) за {str(data_yesterday.iloc[0][5])}:     \nDAU: {str(data_yesterday.iloc[0][1])}    \nПросмотры: {str(data_yesterday.iloc[0][2])}    \nЛайки:{str(data_yesterday.iloc[0][3])}    \nCTR: {str(data_yesterday.iloc[0][4])}    \nDAU(лента+мессенджер): {str(data_nm_yesterday.iloc[0][1])}"


# In[71]:


#Отправляем себе сообщение
bot.sendMessage(chat_id=chat_id, text=msg)


# In[73]:


import matplotlib.pyplot as plt
import seaborn as sns
sns.set()
#Dau
plt.figure(figsize=(17,17))
plt.subplot(2,2,1)
sns.lineplot(data=data_daily, x=data_daily['date'],y=data_daily['users'])
plt.title('Лента. DAU')
plt.xticks(rotation=45)
plt.xlabel('')

#Просмотры и лайки
plt.subplot(2,2,2)
sns.lineplot(data=data_daily, x=data_daily['date'],y=data_daily['views'],label=u'просмотры')
sns.lineplot(data=data_daily, x=data_daily['date'],y=data_daily['like'],label=u'лайки')
plt.title('Лента. Просмотры и лайки')
plt.xticks(rotation=45)
plt.xlabel('')
plt.ylabel('')

#Dau (лента +мессенджер)
plt.subplot(2,2,3)
sns.lineplot(data=data_news_mes, x=data_news_mes['date'],y=data_news_mes['users'])
plt.title('Лента+Мессенджер. Dau')
plt.xticks(rotation=45) 
plt.xlabel('')   

#CTR
plt.subplot(2,2,4)
sns.lineplot(data=data_daily, x=data_daily['date'],y=data_daily['CTR'])
plt.title('Лента. CTR')
plt.xticks(rotation=45) 
plt.xlabel('')   

import io #сохраняем файлы в буфер как объект, а не в файловую систему
plot_object=io.BytesIO() #создаем файловый объект
plt.savefig(plot_object) #заводим в файловый объект наш график
plot_object.name='CTR.png' #задем имя файловому объекту
plot_object.seek(0)
plt.close()

bot.sendPhoto(chat_id=chat_id, photo=plot_object)


# In[ ]:




