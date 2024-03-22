from sys import argv
from re import findall
from json import load
from geopandas import read_file
from cartopy import crs as ccrs
from cartopy.mpl.geoaxes import GeoAxes
from matplotlib.pyplot import subplots, savefig
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
from hashlib import md5
from itertools import chain

################################## LOAD DATA ##################################

riggiuni = read_file("./finaiti/riggiuni/riggiuni.shp")
cumuna = read_file("./finaiti/cumuna/cumuna.shp")
with open("./vs.json") as f: all_codes = load(f)

################################ PROCESS DATA ################################

# Parse input strings into chunks
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

# Find all names associated with a given code
def get_names(dictionary):
    return list(extract_names_recursive("name", dictionary))

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

# Filter spelling for some specific cases
def filter_spelling(spelling):
    official_spellings = [
        "Joppolo Giancaxio",
        "San Giuseppe Jato",
        "Mezzojuso",
        "Raccuja",
        "Moio Alcantara",
        "Letojanni",
        "Castel di Iudica",
    ]
    possible_spellings = [
        "Ioppolo Giancaxio",
        "San Giuseppe Iato",
        "Mezzoiuso",
        "Raccuia",
        "Mojo Alcantara",
        "Letoianni",
        "Castel di Judica",
    ]
    if spelling in possible_spellings:
        index = possible_spellings.index(spelling)
        corrected_spelling = official_spellings[index]
        return corrected_spelling
    else:
        return spelling

# Get user strings
input_string1 = argv[1]
input_string2 = argv[2]
input_string3 = argv[3]

# Get Italian names from 1st input string
codes = parse_input_string(input_string1)
names_ita = set(chain.from_iterable(lookup(code, all_codes) for code in codes))

# Get Italian names from 2nd input string
names_ita.update(filter_spelling(name.strip()) for name in input_string2.split(","))

# Get Sicilian names from 3rd input string
names_scn = {name.strip() for name in input_string3.split(",")}

# Filter cumuna based on all names
chosen_cumuna = cumuna["ITA"].isin(names_ita) | cumuna["SCN"].isin(names_scn)

################################### PLOTTING ##################################

crs_epsg = ccrs.epsg("3857")
riggiuni_epsg = riggiuni.to_crs(epsg="3857")
cumuna_epsg = cumuna.to_crs(epsg="3857")

fig, ax = subplots(subplot_kw={"projection": crs_epsg}, figsize=(7, 7))
ax.set_extent([11.8, 15.7, 38.9, 36.6])
ax.add_geometries(riggiuni_epsg["geometry"], crs=crs_epsg, facecolor="white", edgecolor="black", linewidth=1)
ax.add_geometries(cumuna_epsg["geometry"][chosen_cumuna], crs=crs_epsg, facecolor="#2ECC71", edgecolor="black", linewidth=0.5)

# Create an inset axes for zoomed-in view of isuli Pilaggi
axins = inset_axes(ax, width="60%", height="60%", loc="lower left", bbox_to_anchor=(0.085, 0.01, 0.34, 0.34), bbox_transform=ax.transAxes, axes_class=GeoAxes, axes_kwargs=dict(projection=crs_epsg))
axins.set_extent([12.24, 12.96, 35.95, 35.4])
axins.add_geometries(riggiuni_epsg["geometry"], crs=crs_epsg, facecolor="white", edgecolor="black", linewidth=0.5)
axins.add_geometries(cumuna_epsg["geometry"][chosen_cumuna], crs=crs_epsg, facecolor="#2ECC71", edgecolor="black", linewidth=0.1)

# Make filenames with unique identifier based on input strings
unique_id = md5((input_string1 + input_string2 + input_string3).encode()).hexdigest()
base_path = f"output/{unique_id}"
png_path = f"./public/output/{unique_id}.png"
svg_path = f"./public/output/{unique_id}.svg"

# Save as PNG and SVG files
savefig(png_path, bbox_inches="tight", dpi=150)
savefig(svg_path, bbox_inches="tight")

# Return base path to server.js
print(base_path)
