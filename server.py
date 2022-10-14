from flask import Flask, render_template, request
import folium
from folium import plugins
import json
import io, os
import numpy as np # linear algebra
import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)
from folium.plugins import HeatMap


app = Flask(__name__)

app.secret_key = os.environ.get('APP_SECRET_KEY')

@app.route('/')
def index():
  return render_template("index.html", form={})
  
@app.route('/map', methods=['POST'])
def showmap():
  if (request.form['password'] != app.secret_key):
    return render_template("index.html", form=request.form)
  
  start_coords = (46.9540700, 142.7360300);
  
  m = folium.Map(
      location=start_coords, 
      zoom_start=14, 
      tiles="Stamen Terrain",
      width="100%", height="100%",
      control_scale=True,
  );
  
  if request.form['heatmap_points']:
    heatmap_data = io.StringIO(request.form['heatmap_points'].replace("\t",","))
    df_acc = pd.read_csv(heatmap_data, dtype=object)
    df_acc.drop_duplicates()
    df_acc = df_acc.dropna(axis=0)
    heat_data = [[row[0],row[1]] for index, row in df_acc.iterrows()]

    # Plot it on the map
    HeatMap(heat_data).add_to(m)
  
  if request.form['point_points']:
    points_data = io.StringIO(request.form['point_points'].replace("\t",","))
    df_acc2 = pd.read_csv(points_data, dtype=object)
    df_acc2.drop_duplicates()
    df_acc2 = df_acc2.dropna(axis=0)
    latlon = [[row[0],row[1]] for index, row in df_acc2.iterrows()]

    for coord in latlon:
      folium.Marker( location=[ coord[0], coord[1] ], fill_color='#43d9de', radius=8 ).add_to( m )

  
  m.fit_bounds(m.get_bounds(), padding=(30, 30))

  folium.TileLayer('stamentoner').add_to(m)
  folium.TileLayer('stamenwatercolor').add_to(m)
  folium.TileLayer('cartodbpositron').add_to(m)
  folium.TileLayer('openstreetmap').add_to(m)

  # Add the option to switch tiles
  folium.LayerControl().add_to(m)

  fs = plugins.Fullscreen().add_to(m)

  gc = plugins.Geocoder(collapsed=True, position='topleft', add_marker=True).add_to(m)

  mc = plugins.MeasureControl( position='topleft').add_to(m)

  return m._repr_html_()
  
if __name__ == '__main__':
    app.run(debug=True)
