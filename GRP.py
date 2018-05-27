from scipy.spatial import distance
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from math import sin, cos, sqrt, atan2, radians


# approximate flat distance between two points in km
def flat_dist(lat1, lon1, lat2, lon2):
    # approximate radius of earth in km
    R = 6371.0
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    x = (lon2 - lon1) * cos(0.5 * (lat2 + lat1))
    y = lat2 - lat1
    distance = R * sqrt(x * x + y * y)
    return distance


def terminal_point_in_sector(begin_lat, begin_lon, end_lat, end_lon, banner_lat, banner_lon, r):
    dst1 = flat_dist(begin_lat, begin_lon, banner_lat, banner_lon) * 1000
    dst2 = flat_dist(end_lat, end_lon, banner_lat, banner_lon) * 1000

    if dst1 < r:
        if begin_lat > banner_lat and begin_lon < banner_lon:
            return True
    elif dst2 < r:
        if end_lat > banner_lat and end_lon < banner_lon:
            return True
    else:
        return False


def trajectory_intersects_circle(begin_lat, begin_lon, end_lat, end_lon, banner_lat, banner_lon, r):
    a = flat_dist(begin_lat, begin_lon, banner_lat, banner_lon) * 1000
    b = flat_dist(end_lat, end_lon, banner_lat, banner_lon) * 1000
    c = flat_dist(begin_lat, begin_lon, end_lat, end_lon) * 1000

    p = 0.5 * (a + b + c)
    h_c = 2 * sqrt(p * (p - a) * (p - b) * (p - c)) / c

    a_h = sqrt(a ** 2 - h_c ** 2)
    b_h = sqrt(b ** 2 - h_c ** 2)

    # print(round(b_h - c, 3))
    # print(round(a_h, 3))

    if round(b_h - c, 3) == round(a_h, 3) or round(a_h - c, 3) == round(b_h, 3):
        return False
    elif h_c > r:
        return False
    else:
        return True


def trajectory_intersects_sector(begin_lat, begin_lon, end_lat, end_lon, banner_lat, banner_lon, r):
    # y-y1/y2-y1 = x-x1/x2-x1
    # y = (x-x1)*(y2-y1)/(x2-x1) + y1
    # x = (y-y1)*(x2-x1)/(y2-y1) + x1

    new_lat = ((banner_lon - begin_lon) * (end_lat - begin_lat) / (end_lon - begin_lon)) + begin_lat
    new_lon = ((banner_lat - begin_lat) * (end_lon - begin_lon) / (end_lat - begin_lat)) + begin_lon

    dst1 = flat_dist(new_lat, banner_lon, banner_lat, banner_lon) * 1000
    dst2 = flat_dist(banner_lat, new_lon, banner_lat, banner_lon) * 1000

    if dst1 < r:
        if new_lat > banner_lat:
            return True
    elif dst2 < r:
        if new_lon < banner_lon:
            return True
    else:
        return False


in_contact = []

data = pd.read_csv('01_test_data.csv')
data.drop_duplicates(inplace=True)
data.drop(data[(data.begin_lon == data.end_lon) & (data.begin_lat == data.end_lat)].index, inplace=True)
data.reset_index(inplace=True)

for index, row in data.iterrows():

    banner_lat = 55.777914
    banner_lon = 37.678778

    if terminal_point_in_sector(row['begin_lat'], row['begin_lon'], row['end_lat'], row['end_lon'], banner_lat,
                                banner_lon, 300):
        if 90 <= row['direction'] <= 180:
            if row['hash'] not in in_contact:
                in_contact.append(row['hash'])


    elif trajectory_intersects_circle(row['begin_lat'], row['begin_lon'], row['end_lat'], row['end_lon'], banner_lat,
                                      banner_lon, 300):
        if trajectory_intersects_sector(row['begin_lat'], row['begin_lon'], row['end_lat'], row['end_lon'], banner_lat,
                                        banner_lon, 300):
            if 90 <= row['direction'] <= 180:
                if row['hash'] not in in_contact:
                    in_contact.append(row['hash'])

watchers = len(in_contact)
persons = len(data['hash'].unique().tolist())
print("GRP: %f" % (watchers / persons * 100))