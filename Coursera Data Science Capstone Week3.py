#!/usr/bin/env python
# coding: utf-8

# # Coursera Data Science Capstone Week3

# ## FIRST SUBMISSION

# ## Creating the Dataframe

# In[23]:


import pandas
from IPython.display import display_html


# In[24]:


url1 = 'https://en.wikipedia.org/wiki/List_of_postal_codes_of_Canada:_M'


# In[25]:


df1 = pandas.read_html(url1,header=0)[0]


# In[26]:


#Removing 'Borough' = 'Not assigned'
df2 = df1.drop(df1[df1['Borough']=="Not assigned"].index)
df2.head()


# In[27]:


def Combine_Neigh(x):
    return pandas.Series(dict(Neighbourhood=','.join(x['Neighbourhood'])))


# In[28]:


#Combining Neighbourhood for (Postcode,Borough) group
df3 = df2.groupby(['Postcode','Borough'],sort=False).apply(Combine_Neigh).reset_index()
df3.head()


# In[29]:


#Replacing 'Not assigned' Neighbourhood values with Borough values
for i in range(len(df3)):
    if df3['Neighbourhood'][i] == "Not assigned":
        df3['Neighbourhood'][i] = df3['Borough'][i]
df3.head()


# In[30]:


df3.shape


# ## SECOND SUBMISSION

# In[31]:


pip install geocoder


# In[32]:


import geocoder # import geocoder
#Geocoder not working. Infinite loop.


# In[34]:


#Create dataframe of Geospatial Coordinates
df4 = pandas.read_csv('C:/Users/User/Downloads/Geospatial_Coordinates.csv')
df4.rename(columns={'Postal Code':'Postcode'},inplace=True)
df4.head()


# In[35]:


df5 = pandas.merge(df3,df4,on='Postcode')
df5.head()


# In[36]:


df5.shape

