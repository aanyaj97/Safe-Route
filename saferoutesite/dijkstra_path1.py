import osmnx as ox
import networkx as nx
import geopy.geocoders
import datetime
import numpy as np
import math
from math import radians, cos, sin, asin, sqrt
from scipy import stats

from geopy.geocoders import Nominatim
from SQLRequest3 import Regression_List 
from current_weather import get_current_weather
   
def get_coordinates(start_address, end_address):
    '''
    Obtain (latitude, longitude) pairs from desired starting and ending 
    addresses
    
    Inputs:
      start_address (string): the starting point in the route
      end_address (string): the destination of the route
      
    Output:
      (tuple of tuples of floats): the coordinate pairs for the starting and
          ending addresses
    '''

    geolocator = Nominatim(user_agent="saferoute",\
                           format_string="%s, Chicago IL")

    start_loc = geolocator.geocode(start_address)
    end_loc = geolocator.geocode(end_address)
    start_coord = None
    end_coord = None
    if start_loc and end_loc:
        start_coord = (start_loc.latitude, start_loc.longitude)
        end_coord = (end_loc.latitude, end_loc.longitude)
    return start_coord, end_coord


def get_bounding_box(start_coord, end_coord):
    '''
    Find coordinates representing the edges of the bounding box for the route
    
    Inputs:
      start_coord (tuple of floats): the coordinates of the starting point in
          the route
      end_coord (tuple of floats): the coordinates of the destination of the 
          route
     
    Output:
        (tuple of four floats): the northernmost and southernmost latitudes and
            the easternmost and westernmost longitudes of the bounding box
    '''

    start_lat = start_coord[0]
    start_lon = start_coord[1]
    end_lat = end_coord[0]
    end_lon = end_coord[1]
    
    if start_lat <= end_lat:
        s_lat = start_lat - 0.001
        n_lat = end_lat + 0.001
    else:
        n_lat = start_lat + 0.001
        s_lat = end_lat - 0.001
    
    if start_lon <= end_lon:
        w_lon = start_lon - 0.001
        e_lon = end_lon + 0.001
    else:
        e_lon = start_lon + 0.001
        w_lon = end_lon - 0.001
    
    return(n_lat, s_lat, e_lon, w_lon)
                           

def get_graph(n_lat, s_lat, e_lon, w_lon): 
    '''
    Using the bounding box, obtain an undirected graph representing the 
    desired section of the city in which the route will take place
    
    Inputs:
      n_lat (float): the northermost latitude of the bounding box
      s_lat (float): the southernmost latitude of the bounding box
      e_lon (float): the easternmost longitude of the bounding box
      w_lon (float): the westernmost longitude of the bounding box
     
    Output:
      A networkx graph  
    '''

    B = ox.core.graph_from_bbox(n_lat, s_lat, e_lon, w_lon,\
                                network_type= 'walk', simplify=True,\
                                retain_all=False, truncate_by_edge=False,\
                                name='bounded', timeout=180, memory=None,\
                                max_query_area_size=2500000000,\
                                clean_periphery=True,\
                                infrastructure='way["highway"]',\
                                custom_filter=None)
    
    B_undirected = ox.save_load.get_undirected(B)
    
    return B_undirected


def update_edge_lengths(G, scores):
    '''
    Update the lengths of each edge in the graph in order to weight them
    according to their safety scores
    
    Inputs:
      G (networkx graph): the graph
      scores (dictionary): the safety score for each edge
    '''

    set_edge_dict = {}
    new_attrs = {}
    for start, end, attrs in list(G.edges(data = True)):
        length = attrs['length']
        score = scores.get(edge_to_latlon_pair(G, (start, end)), 10**12)
        weight = score * length
        set_edge_dict[(start, end,0)] = {'length': weight}
    
    nx.set_edge_attributes(G, set_edge_dict)


def edge_to_latlon_pair(G, edge):
    '''
    Convert an edge to the pair of (latitude, longitude) coordinates
    corresponding to the nodes of the edge
    
    Inputs:
      G (networkx graph): the graph
      edge (networkx edge): the desired edge to convert
    
    Output:
      (tuple of tuple of floats): the pair of coordinates 
    '''

    node1 = G.nodes[edge[0]]
    node2 = G.nodes[edge[1]]
    n1 = (node1['y'], node1['x'])
    n2 = (node2['y'], node2['x'])
    return ((n1),(n2))


def get_path(start_coord, end_coord, G, nodes, scores):
    '''
    Find the closest nodes to the start and the destination in the graph
    and use them to compute the shortest weighted path in between
    
    Inputs:
      start_coord (tuple of floats): the coordinates of the starting point in
          the route
      end_coord (tuple of floats): the coordinates of the destination of the 
          route 
      G (networkx graph): the graph
      nodes (list of nodes): the list of graph nodes
      scores (dictionary): the safety score dictionary
    
    Output:
      (list of nodes) the safest path in terms of graph nodes
    '''

    update_edge_lengths(G, scores)

    s_min_lon_dist = 0.001
    s_min_lat_dist = 0.001
    e_min_lon_dist = 0.001
    e_min_lat_dist = 0.001
    start_node = None
    end_node = None
    
    for node, attrs in nodes:
        lat = attrs['y']
        lon = attrs['x']
        s_lat_dist = abs(start_coord[0] - lat)
        s_lon_dist = abs(start_coord[1] - lon)
        e_lat_dist = abs(end_coord[0] - lat)
        e_lon_dist = abs(end_coord[1] - lon)
        if s_lat_dist <= s_min_lat_dist and s_lon_dist <= s_min_lon_dist:
            s_min_lat_dist = s_lat_dist
            s_min_lon_dist = s_lon_dist
            start_node = node
        if e_lat_dist <= e_min_lat_dist and e_lon_dist <= e_min_lon_dist:
            e_min_lat_dist = e_lat_dist
            e_min_lon_dist = e_lon_dist
            end_node = node
    
    path = nx.dijkstra_path(G, start_node, end_node, weight='length')
    #length of the shortest path
    s_length = nx.shortest_path_length(
        G, source=start_node, target=end_node, weight='length')    
    return path, s_length


#From PA3 (modified)
def haversine(t1, t2):
    '''
    Calculate the circle distance between two points
    on the earth (specified in decimal degrees)
    '''
    lat1, lon1 = t1
    lat2, lon2 = t2
    # convert decimal degrees to radians
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    # haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * asin(sqrt(a))

    # 6367 km is the radius of the Earth
    km = 6367 * c
    m = km * 1000
    return m


#From Stack Overflow Question 8747761
def lognorm(x):
    ''' 
    gives result of cdf of lognorm given mu/sigma
    '''
    #mu, sigma from Distribution_Creation
    if x <= 0:
        return 0
    mu = np.log(893840.8440044996)
    sigma = 10.433836709999136
    a = (math.log(x) - mu)/math.sqrt(2 * sigma ** 2)
    p = 0.5 + 0.5 * math.erf(a)
    return p


def go(args):
    '''
    Pull data from the crime database and weather information in order to 
    compute the safety score dictionary and runs all previous code in 
    order to find the safest route from start_address to end_address.
    
    Inputs:
    {args} containing:
      start_address (string): the starting point in the route
      end_address (string): the destination of the route
      date (string): the desired date if provided
      hour (int): the time of day if provided
      temp (int): temperature if provided
      precip (int): precipitation (inches) if provided

    
    Outputs:
      (list of lists of floats): the safest path in terms of (lat,lon)
      coordinates
    '''

    start_address = args["start_address"]
    end_address = args["end_address"]
    date = args["date_of_travel"]
    hour = args["hour_of_travel"]
    temp = args["temperature"]
    precip = args["precipitation"]

    current_DT = datetime.datetime.now()
    # handle optional args and set to defaults if necessary
    if not date:
        date = current_DT.strftime('%Y-%m-%d') 
    if not hour:
        hour = current_DT.hour
    current_temp, current_precip = get_current_weather()
    if not temp:
        temp = current_temp
    if not precip:
        precip = current_precip
    start_coord, end_coord = get_coordinates(start_address, end_address)

    if not start_coord or not end_coord:
        return "Please enter valid addresses within the City of Chicago."

    n_lat, s_lat, e_lon, w_lon = get_bounding_box(start_coord, end_coord)
    G = get_graph(n_lat, s_lat, e_lon, w_lon)
    nodes = list(G.nodes(data = True))
    edges = [(start, end, attrs) for (start, end, attrs) in G.edges(data = True)\
             if 'name' in attrs.keys()]
    node_dic = dict(G.nodes(data = True))
    edges_lst = [edge_to_latlon_pair(G, edge) for edge in edges]

    # adjust temperature and time sensitivities
    t_sens = 12
    time_low = hour - 2
    time_up = hour + 2
    p_sens = 0.5
    scores = Regression_List(edges_lst, temp, precip, t_sens, p_sens, date,\
                             time_low, time_up)
    
    path, s_length = get_path(start_coord, end_coord, G, nodes, scores)
    
    route_steps = [[G.nodes[node]['y'],G.nodes[node]['x']] for node in path]
    path_coords = [[start_coord[0],start_coord[1]]] + route_steps +\
                  [[end_coord[0],end_coord[1]]]
    if type(s_length) == dict:
        s_length = s_length[end_node]
        
    return path_coords, 1 - lognorm(s_length / haversine(start_coord, end_coord))