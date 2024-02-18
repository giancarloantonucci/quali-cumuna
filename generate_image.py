from sys import argv
from re import findall, match
from json import load
from geopandas import read_file
from cartopy import crs as ccrs
from cartopy.mpl.geoaxes import GeoAxes
from matplotlib.pyplot import subplots, savefig
from mpl_toolkits.axes_grid1.inset_locator import inset_axes

def parse_string(input_string):
    result = []
    tokens = findall(r'\b(?:AG|CL|CT|EN|ME|PA|RG|SR|TP)(?:(?:\s*,)?\s*[AIV0-9]+[a-z]*(?:-\d+)?)+\b', input_string)
    for token in tokens:
        header = token[:2]
        idxs = [s.strip() for s in token[2:].split(',')]
        for idx in idxs:
            _match = match(r'((\d+)-(\d+))', idx)
            if _match:
                _, start, end = _match.groups()
                start = int(start)
                end = int(end)
                for n in range(start, end + 1):
                    result.append(f"{header} {n}")
            else:
                result.append(f"{header} {idx}")
    return result

def extract(string_or_list_of_strings, dictionary):
    output = []
    get_name = False
    if isinstance(string_or_list_of_strings, str):
        string = string_or_list_of_strings
        find_in_list(string_or_list_of_strings, dictionary, output, get_name)
    elif isinstance(string_or_list_of_strings, list):
        list_of_strings = string_or_list_of_strings
        for string in list_of_strings:
            find_in_list(string, dictionary, output, get_name)
    return output
    
def find_in_list(string, _list, output, get_name):
    for _dict in _list:
        find_in_dict(string, _dict, output, get_name)
    return output
    
def find_in_dict(string, _dict, output, get_name):
    if _dict['acronym'] == string:
        get_name = True
    data = _dict['data']
    if isinstance(data, list):
        find_in_list(string, data, output, get_name)
    if get_name:
        output.append(_dict['name'])
    return output

input_string1 = argv[1]
input_string2 = argv[2]
input_string3 = argv[3]

riggiuni = read_file("./finaiti/riggiuni/riggiuni.shp")
cumuna = read_file("./finaiti/cumuna/cumuna.shp")

crs_epsg = ccrs.epsg("3857")
riggiuni_epsg = riggiuni.to_crs(epsg="3857")
cumuna_epsg = cumuna.to_crs(epsg="3857")

f = open('./piccitto.json')
piccitto = load(f)
f.close()

list_of_headers_plus_idxs = parse_string(input_string1)
names = extract(list_of_headers_plus_idxs, piccitto) + [x.strip() for x in input_string2.split(',')]
names_scn = [x.strip() for x in input_string3.split(',')]

idx = (cumuna_epsg['ITA'] == "")
for name in names:
    idx = idx | (cumuna_epsg['ITA'] == name)
for name in names_scn:
    idx = idx | (cumuna_epsg['SCN'] == name)
    
fig, ax = subplots(subplot_kw={"projection": crs_epsg}, figsize=(7, 7))
ax.set_extent([11.8, 15.7, 38.9, 36.6])
ax.add_geometries(riggiuni_epsg["geometry"], crs=crs_epsg, facecolor="white", edgecolor="black", linewidth=1)
ax.add_geometries(cumuna_epsg["geometry"][idx], crs=crs_epsg, facecolor="#2ECC71", edgecolor='black', linewidth=0.5)

axins = inset_axes(ax, width="60%", height="60%", loc='lower left',
    bbox_to_anchor=(0.085, 0.01, 0.34, 0.34),
    bbox_transform=ax.transAxes,
    axes_class=GeoAxes,
    axes_kwargs=dict(projection=crs_epsg))
axins.set_extent([12.24, 12.96, 35.95, 35.4])
axins.add_geometries(riggiuni_epsg["geometry"], crs=crs_epsg, facecolor="white", edgecolor="black", linewidth=1)
axins.add_geometries(cumuna_epsg["geometry"][idx], crs=crs_epsg, facecolor="#2ECC71", edgecolor='black', linewidth=0.5)

savefig('./public/mmaggini.png', bbox_inches='tight')
savefig('./public/mmaggini.svg', bbox_inches='tight')
print('mmaggini.png')
