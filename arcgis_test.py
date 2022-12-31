from arcgis.gis import GIS

from arcgis.geocoding import reverse_geocode

from arcgis.geometry import Point

import pandas as pd

import re

import os

from tqdm import tqdm

gis = GIS()


def reverse_geocode_to_address(path, filename):
    _, file_extension = os.path.splitext(os.path.join(path, filename))

    if file_extension == '.csv':

        coord_df_orig = pd.read_csv(os.path.join(path, filename))

    elif file_extension == '.xlsx':

        coord_df_orig = pd.read_excel(os.path.join(path, filename))

    coord_df_lat = coord_df_orig.filter(regex=re.compile(r"lat.*?", re.IGNORECASE))

    coord_df_long = coord_df_orig.filter(regex=re.compile(r"long.*?", re.IGNORECASE))

    coord_df_time = coord_df_orig.filter(regex=re.compile(r".*?(date|time).*?", re.IGNORECASE))

    coord_df = coord_df_lat.merge(coord_df_long, left_index=True, right_index=True)

    coord_df = coord_df.merge(coord_df_time, left_index=True, right_index=True)

    m = gis.map("Akron, OH", zoomlevel=9)

    address_list = []

    rows_complete = 0

    with tqdm(total=coord_df.shape[0]) as pbar:

        for index, row in coord_df.iterrows():

            rows_complete += 1

            try:

                location = {'Y': row[0], 'X': row[1]}

                unknown_pt = Point(location)

                address_return = reverse_geocode(location=unknown_pt)

                address = address_return['address']['Address'] + ', ' + address_return['address']['City'] + ', ' + \
                          address_return['address']['Region']

                m.draw(address_return, popup={'title': address,
                                              'content': f'Time Stamp: {row[2]}<br> Latitude: {row[0]}<br> Longitude: {row[1]}'})

                address_list.append(address)

            except:

                address_list.append('')

                continue

            pbar.update(1)

    coord_df_orig['Address'] = address_list

    coord_df_orig.to_csv(os.path.join(path, filename + '_amended.csv'))

    m.export_to_html(os.path.join(path, filename + '_map.html'))


reverse_geocode_to_address(path="C:\\path\\to\\file\\", filename="file.csv")
