#!/usr/bin/env python
# coding: utf-8

# # Coursera Data Science Capstone Week3

# ## FIRST SUBMISSION

# ## Creating the Dataframe

# In[92]:


import pandas
import numpy
from IPython.display import display_html
import matplotlib.cm as cm
import matplotlib.colors as colors


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


# ## THIRD SUBMISSION

# In[40]:


import folium
from sklearn.cluster import KMeans
from geopy.geocoders import Nominatim


# In[41]:


#Toronto map location
address = 'Toronto, ON'

geolocator = Nominatim(user_agent="ny_explorer")
location = geolocator.geocode(address)
latitude = location.latitude
longitude = location.longitude
print('The geograpical coordinate of Toronto are {}, {}.'.format(latitude, longitude))


# In[42]:


#Create Toronto map
map_toronto = folium.Map(location=[latitude, longitude], zoom_start=10)

#Add markers to map
for lat, lng, borough, neighborhood in zip(df5['Latitude'], df5['Longitude'], df5['Borough'], df5['Neighbourhood']):
    label = '{}, {}'.format(neighborhood, borough)
    label = folium.Popup(label, parse_html=True)
    folium.CircleMarker(
        [lat, lng],
        radius=5,
        popup=label,
        color='blue',
        fill=True,
        fill_color='#3186cc',
        fill_opacity=0.7,
        parse_html=False).add_to(map_toronto)  
    
map_toronto


# In[86]:


df6 = df5[df5['Borough'].str.contains("Toronto")]
df6.rename(columns={'Neighbourhood':'Neighborhood'},inplace=True)
df6.head()


# In[87]:


#Create Borough containing 'Toronto' map
map_toronto_new = folium.Map(location=[latitude, longitude], zoom_start=12)

#Add markers to map
for lat, lng, borough, neighborhood in zip(df6['Latitude'], df6['Longitude'], df6['Borough'], df6['Neighborhood']):
    label = '{}, {}'.format(neighborhood, borough)
    label = folium.Popup(label, parse_html=True)
    folium.CircleMarker(
        [lat, lng],
        radius=5,
        popup=label,
        color='blue',
        fill=True,
        fill_color='#3186cc',
        fill_opacity=0.7,
        parse_html=False).add_to(map_toronto_new)  
    
map_toronto_new


# ### Explore Neighbourhood using Foursquare

# In[53]:


from IPython.display import Image
from IPython.core.display import HTML
import requests
from pandas.io.json import json_normalize


# In[56]:


CLIENT_ID = '0LJP2QGV1EXCG5ALHHLTZFP5GZH300JZUEXN1ETTZOL5EE31'
CLIENT_SECRET = '1ZGVSYFAHCDOLCK3X5U2Z555KF0RRXKJOGE315PB5ITNW0ZC'
VERSION = '20191018'
LIMIT = 30
radius = 500


# In[67]:


def getNearbyVenues(names, latitudes, longitudes, radius=500):
    
    venues_list=[]
    for name, lat, lng in zip(names, latitudes, longitudes):
        print(name)
            
        # create the API request URL
        url = 'https://api.foursquare.com/v2/venues/explore?&client_id={}&client_secret={}&v={}&ll={},{}&radius={}&limit={}'.format(
            CLIENT_ID, 
            CLIENT_SECRET, 
            VERSION, 
            lat, 
            lng, 
            radius, 
            LIMIT)
            
        # make the GET request
        results = requests.get(url).json()["response"]['groups'][0]['items']
        
        # return only relevant information for each nearby venue
        venues_list.append([(
            name, 
            lat, 
            lng, 
            v['venue']['name'], 
            v['venue']['location']['lat'], 
            v['venue']['location']['lng'],  
            v['venue']['categories'][0]['name']) for v in results])

    nearby_venues = pandas.DataFrame([item for venue_list in venues_list for item in venue_list])
    nearby_venues.columns = ['Neighborhood', 
                  'Neighborhood Latitude', 
                  'Neighborhood Longitude', 
                  'Venue', 
                  'Venue Latitude', 
                  'Venue Longitude', 
                  'Venue Category']
    
    return(nearby_venues)


# In[68]:


toronto_venues = getNearbyVenues(names=df6['Neighbourhood'],
                                   latitudes=df6['Latitude'],
                                   longitudes=df6['Longitude']
                                  )


# In[73]:


print('There are {} uniques categories.'.format(len(toronto_venues['Venue Category'].unique())))


# In[75]:


# one hot encoding
toronto_onehot = pandas.get_dummies(toronto_venues[['Venue Category']], prefix="", prefix_sep="")

# add neighborhood column back to dataframe
toronto_onehot['Neighborhood'] = toronto_venues['Neighborhood'] 

# move neighborhood column to the first column
fixed_columns = [toronto_onehot.columns[-1]] + list(toronto_onehot.columns[:-1])
toronto_onehot = toronto_onehot[fixed_columns]

toronto_onehot.head()


# In[76]:


toronto_grouped = toronto_onehot.groupby('Neighborhood').mean().reset_index()


# In[77]:


def return_most_common_venues(row, num_top_venues):
    row_categories = row.iloc[1:]
    row_categories_sorted = row_categories.sort_values(ascending=False)
    
    return row_categories_sorted.index.values[0:num_top_venues]


# In[82]:


num_top_venues = 10

indicators = ['st', 'nd', 'rd']

# create columns according to number of top venues
columns = ['Neighborhood']
for ind in numpy.arange(num_top_venues):
    try:
        columns.append('{}{} Most Common Venue'.format(ind+1, indicators[ind]))
    except:
        columns.append('{}th Most Common Venue'.format(ind+1))

# create a new dataframe
neighborhoods_venues_sorted = pandas.DataFrame(columns=columns)
neighborhoods_venues_sorted['Neighborhood'] = toronto_grouped['Neighborhood']

for ind in numpy.arange(toronto_grouped.shape[0]):
    neighborhoods_venues_sorted.iloc[ind, 1:] = return_most_common_venues(toronto_grouped.iloc[ind, :], num_top_venues)

neighborhoods_venues_sorted.head()


# ### K Means Clustering

# In[83]:


kclusters = 5

toronto_grouped_clustering = toronto_grouped.drop('Neighborhood', 1)

# run k-means clustering
kmeans = KMeans(n_clusters=kclusters, random_state=0).fit(toronto_grouped_clustering)

# check cluster labels generated for each row in the dataframe
kmeans.labels_[0:10] 


# In[88]:


neighborhoods_venues_sorted.insert(0, 'Cluster Labels', kmeans.labels_)


# In[89]:


toronto_merged = df6

# merge toronto_grouped with toronto_data to add latitude/longitude for each neighborhood
toronto_merged = toronto_merged.join(neighborhoods_venues_sorted.set_index('Neighborhood'), on='Neighborhood')

toronto_merged.head()


# In[94]:


# create map
map_clusters = folium.Map(location=[latitude, longitude], zoom_start=12)

# set color scheme for the clusters
x = numpy.arange(kclusters)
ys = [i + x + (i*x)**2 for i in range(kclusters)]
colors_array = cm.rainbow(numpy.linspace(0, 1, len(ys)))
rainbow = [colors.rgb2hex(i) for i in colors_array]

# add markers to the map
markers_colors = []
for lat, lon, poi, cluster in zip(toronto_merged['Latitude'],toronto_merged['Longitude'],toronto_merged['Neighborhood'], toronto_merged['Cluster Labels']):
    label = folium.Popup(str(poi) + ' Cluster ' + str(cluster), parse_html=True)
    folium.CircleMarker(
        [lat, lon],
        radius=5,
        popup=label,
        color=rainbow[cluster-1],
        fill=True,
        fill_color=rainbow[cluster-1],
        fill_opacity=0.7).add_to(map_clusters)
       
map_clusters


# ### 1st Cluster

# In[95]:


toronto_merged.loc[toronto_merged['Cluster Labels'] == 0, toronto_merged.columns[[1] + list(range(5, toronto_merged.shape[1]))]]


# ### 2nd Cluster

# In[97]:


toronto_merged.loc[toronto_merged['Cluster Labels'] == 1, toronto_merged.columns[[1] + list(range(5, toronto_merged.shape[1]))]]


# ### 3rd Cluster

# In[98]:


toronto_merged.loc[toronto_merged['Cluster Labels'] == 2, toronto_merged.columns[[1] + list(range(5, toronto_merged.shape[1]))]]


# ### 4th Cluster

# In[99]:


toronto_merged.loc[toronto_merged['Cluster Labels'] == 3, toronto_merged.columns[[1] + list(range(5, toronto_merged.shape[1]))]]


# ### 5th Cluster

# In[96]:


toronto_merged.loc[toronto_merged['Cluster Labels'] == 4, toronto_merged.columns[[1] + list(range(5, toronto_merged.shape[1]))]]


# In[ ]:




