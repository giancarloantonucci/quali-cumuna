from sys import argv
from re import findall
from json import load
from geopandas import read_file
from cartopy import crs as ccrs
from cartopy.mpl.geoaxes import GeoAxes
from matplotlib.pyplot import subplots, savefig
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
from hashlib import md5

# Parse input strings into manageable chunks
def parse_input_string(input_string):
    pattern = (r"\b(?:AG|CL|CT|EN|ME|PA|RG|SR|TP)(?:(?:\s*,)?\s*[AIV0-9]+[a-z]*(?:-\d+)?)*\b")
    tokens = findall(pattern, input_string)
    result = []
    for token in tokens:
        header = token[:2]
        indices = [s.strip() for s in token[2:].split(",")]
        if indices[0]:
            for idx in indices:
                if "-" in idx:
                    start, end = map(int, idx.split("-"))
                    result.extend(f"{header} {n}" for n in range(start, end + 1))
                else:
                    result.append(f"{header} {idx}")
        else:
            result.append(f"{header}")
    return result

# Extract names from nested dictionaries
def extract_names_recursive(key, dictionary):
    if hasattr(dictionary, "items"):
        for k, v in dictionary.items():
            if k == key:
                yield v
            if isinstance(v, dict):
                for result in extract_names_recursive(key, v):
                    yield result
            elif isinstance(v, list):
                for d in v:
                    for result in extract_names_recursive(key, d):
                        yield result

def get_names(dictionary):
    return list(extract_names_recursive("name", dictionary))

# Find all names associated with a given code
def lookup(code, all_codes):
    header = code.split(" ")[0]
    for province in all_codes:
        if code == province["code"]:
            return get_names(province)
        elif header == province["code"]:
            areas = province["data"]
            for area in areas:
                if code == area["code"]:
                    return get_names(area)
            for area in areas:
                cumuna = area["data"]
                for cumuni in cumuna:
                    if code == cumuni["code"]:
                        return get_names(cumuni)
                    else:
                        circuscrizziuna = cumuni["data"]
                        # TODO: Uncomment when circuscrizziuna will have polygons
                        # if not isinstance(circuscrizziuna, str):
                        #     for circuscrizziuni in circuscrizziuna:
                        #         if code == circuscrizziuni['code']:
                        #             return get_names(circuscrizziuni)
                        if not isinstance(circuscrizziuna, str):
                            if any(code == circuscrizziuni["code"] for circuscrizziuni in circuscrizziuna):
                                return [cumuni["name"]]
    return []

# Load data files
riggiuni = read_file("./finaiti/riggiuni/riggiuni.shp")
cumuna = read_file("./finaiti/cumuna/cumuna.shp")
with open("./vs.json") as f: all_codes = load(f)

# Collect user strings
input_string1 = argv[1]
input_string2 = argv[2]
input_string3 = argv[3]

# Process strings
codes = parse_input_string(input_string1)
from itertools import chain

names_ita = set(chain.from_iterable(lookup(code, all_codes) for code in codes))
names_ita.update(name.strip() for name in input_string2.split(","))
names_scn = {name.strip() for name in input_string3.split(",")}
selected_cumuna = cumuna["ITA"].isin(names_ita) | cumuna["SCN"].isin(names_scn)

# Plotting
crs_epsg = ccrs.epsg("3857")
riggiuni_epsg = riggiuni.to_crs(epsg="3857")
cumuna_epsg = cumuna.to_crs(epsg="3857")

fig, ax = subplots(subplot_kw={"projection": crs_epsg}, figsize=(7, 7))
ax.set_extent([11.8, 15.7, 38.9, 36.6])
ax.add_geometries(riggiuni_epsg["geometry"], crs=crs_epsg, facecolor="white", edgecolor="black", linewidth=1)
ax.add_geometries(cumuna_epsg["geometry"][selected_cumuna], crs=crs_epsg, facecolor="#2ECC71", edgecolor="black", linewidth=0.5)

# Create an inset axes for zoomed-in view of isuli Pilaggi
axins = inset_axes(ax, width="60%", height="60%", loc="lower left", bbox_to_anchor=(0.085, 0.01, 0.34, 0.34), bbox_transform=ax.transAxes, axes_class=GeoAxes, axes_kwargs=dict(projection=crs_epsg))
axins.set_extent([12.24, 12.96, 35.95, 35.4])
axins.add_geometries(riggiuni_epsg["geometry"], crs=crs_epsg, facecolor="white", edgecolor="black", linewidth=1)
axins.add_geometries(cumuna_epsg["geometry"][selected_cumuna], crs=crs_epsg, facecolor="#2ECC71", edgecolor="black", linewidth=0.5)

# Generate filenames with unique identifier based on input parameters
def generate_images(input_string1, input_string2, input_string3):
    unique_id = md5((input_string1 + input_string2 + input_string3).encode()).hexdigest()
    base_path = f"output/{unique_id}"
    png_path = f"./public/output/{unique_id}.png"
    svg_path = f"./public/output/{unique_id}.svg"
    return base_path, png_path, svg_path

base_path, png_path, svg_path = generate_images(input_string1, input_string2, input_string3)

# Save the figure as PNG and SVG files
savefig(png_path, bbox_inches="tight")
savefig(svg_path, bbox_inches="tight")

print(base_path)
