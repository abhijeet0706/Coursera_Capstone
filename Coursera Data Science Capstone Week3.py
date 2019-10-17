#!/usr/bin/env python
# coding: utf-8

# # Coursera Data Science Capstone Week3

# ## Creating the Dataframe

# In[7]:


get_ipython().system('conda install -c menpo wget --yes')


# In[20]:


import wget
import pandas
from IPython.display import display_html


# In[ ]:


url1 = 'https://en.wikipedia.org/wiki/List_of_postal_codes_of_Canada:_M'


# In[30]:


df1 = pandas.read_html(url1,header=0)[0]


# In[65]:


#Removing 'Borough' = 'Not assigned'
df2 = df1.drop(df1[df1['Borough']=="Not assigned"].index)
df2.head()


# In[59]:


def Combine_Neigh(x):
    return pandas.Series(dict(Neighbourhood=','.join(x['Neighbourhood'])))


# In[87]:


#Combining Neighbourhood for (Postcode,Borough) group
df3 = df2.groupby(['Postcode','Borough'],sort=False).apply(Combine_Neigh).reset_index()
df3.head()


# In[98]:


#Replacing 'Not assigned' Neighbourhood values with Borough values
for i in range(len(df3)):
    if df3['Neighbourhood'][i] == "Not assigned":
        df3['Neighbourhood'][i] = df3['Borough'][i]
df3.head()


# In[97]:


df3.shape

