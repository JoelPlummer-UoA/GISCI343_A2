"""from shiny import App, ui, render, reactive
from shinywidgets import output_widget, render_widget
from ipyleaflet import Map, GeoData, CircleMarker, GeoJSON, basemaps, LayerGroup
import geopandas as gpd
from ipywidgets import HTML
import pandas as pd
import folium

# --- Load data ---
cas = gpd.read_file("Data/CAS.geojson").to_crs(4326)
cycling_network = gpd.read_file("Data/Cycling_Network.shp").to_crs(4326)

cas.head()
cycling_network.head()

cas.dtypes
cycling_network.dtypes

cas.columns
cycling_network.columns

cas.shape
cycling_network.shape


# --- Cleaning data ---
#crash = cas.drop(columns=['advisorySp', 'areaUnitID', 'bridge', 'bus', 'carStation', 'cliffBank', 'crashDirec', 'crashFinan', 'crashLocat', 'crashRoadS', 'crashSHDes', 'debris', 'directionR', 'ditch', 'fence', 'flatHill', 'guardRail', 'holiday', 'houseOrBui', 'intersecti', 'kerb', 'light', 'meshblockI', 'moped', 'motorcycle', 'NumberOfLa', 'objectThro', 'otherObjec', 'otherVehic', 'overBank', 'parkedVehi', 'pedestrian', 'phoneBoxEt', 'postOrPole', 'region', 'roadCharac', 'roadLane', 'roadSurfac', 'roadworks', 'schoolBus', 'seriousInj', 'slipOrFloo', 'strayAnima', 'streetLigh', 'suv', 'taxi', 'temporaryS', 'tlaId', 'tlaName', 'trafficCon', 'trafficIsl', 'trafficSig', 'train', 'tree', 'truck', 'unknownVeh', 'urban', 'vanOrUtili', 'vehicle', 'waterRiver', 'weatherB'])
#crash.columns
#crash.head()

#cycle = cycling_network.drop(columns=['IDENTIFIER', 'ROUTEFUNCT', 'STATUS', 'VEHICLESPE', 'TRAFFICAAD', 'JOURNEYCOR', 'Shape__Len'])
#cycle.columns
#cycle.head()

#cycle['TYPEOFFACI'].unique()
#cycle['LOCALBOARD'].unique()



app_ui = ui.page_fluid( 

    ui.layout_sidebar(   
        ui.sidebar(
            ui.input_slider("bicycle_slider", "Number of Bicycles involved", min=1, max=5, value=[1, 5]),
            ui.input_checkbox_group("TYPEOFFACI", "Type of Cycling Facility", choices=['Off-road shared path', 'Local area traffic management', 'Off-road cycleway', 'On-road unbuffered cycle lane', 'On-road protected cycle lane', 'On-road protected cycle lane (bi-directional)', 'On-road buffered cycle lane', 'Off-road trail', 'Shared zone'], selected=['Off-road shared path', 'Local area traffic management', 'Off-road cycleway', 'On-road unbuffered cycle lane', 'On-road protected cycle lane', 'On-road protected cycle lane (bi-directional)', 'On-road buffered cycle lane', 'Off-road trail', 'Shared zone']),
            ui.input_selectize("LOCALBOARD", "Local Board", choices=['Howick', 'Upper Harbour', 'Orakei', 'Henderson - Massey', 'Waitakere Ranges', 'Puketapapa', 'Whau', 'Devonport-Takapuna', 'Manurewa', 'Hibiscus and Bays', 'Kaipatiki', 'Albert - Eden', 'Waitemata', 'Mangere - Otahuhu', 'Maungakiekie - Tamaki', 'Otara - Papatoetoe', 'Henderson Massey', 'Waiheke', 'Kaipataki', 'Papakura', 'Rodney','Franklin'], selected=[], multiple=True),
        ), 
    

    ui.card(
        output_widget("map"),
        full_screen=True,
        height="500px",
        width="500px",
    ),

    title="Auckland Bicycle Crash Dashboard",))





def server(input, output, session):

     m = Map(
        center=(-36.84, 174.76),
        zoom=10,
        basemap=basemaps.CartoDB.Positron
    )

    # --- Cycle layer (GeoJSON works fine here) ---
     cycle_layer = GeoJSON(
        data={},
        style={"color": "green", "weight": 2}
    )

    # --- Crash layer FIX: use LayerGroup instead of GeoJSON ---
     crash_layer = LayerGroup()


     m.add_layer(cycle_layer)
     m.add_layer(crash_layer)

     @render_widget
     def map():
        return m

    # --- Reactive update ---
     @reactive.effect
     def _():

        bike_range = input.bicycle_slider()
        selected_facilities = input.TYPEOFFACI()
        selected_boards = input.LOCALBOARD()

        # --- Filter crash data ---
        filtered_crash = cas[
            cas["bicycle"].between(bike_range[0], bike_range[1])
        ]

        # --- Filter cycle data ---
        filtered_cycle = cycling_network.copy()

        if selected_facilities:
            filtered_cycle = filtered_cycle[
                filtered_cycle["TYPEOFFACI"].isin(selected_facilities)
            ]

        if selected_boards:
            filtered_cycle = filtered_cycle[
                filtered_cycle["LOCALBOARD"].isin(selected_boards)
            ]

        # --- Update cycle GeoJSON ---
        cycle_layer.data = filtered_cycle.__geo_interface__

# --- Update crash markers ---
        crash_layer.clear_layers()

        markers = []

        for _, row in filtered_crash.iterrows():

            geom = row.geometry

            if geom is None:
                continue

            markers.append(
                CircleMarker(
                    location=(geom.y, geom.x),
                    radius=3,
                    color="blue",
                    fill_color="blue",
                    fill_opacity=0.6,
                )
            )

        crash_layer.layers = tuple(markers)
        

app = App(app_ui, server)


#crash_layer.add_layer"""

from shiny import App, ui, render, reactive
from shinywidgets import output_widget, render_widget
from ipyleaflet import (
    Map,
    CircleMarker,
    GeoJSON,
    basemaps,
    LayerGroup,
    LayersControl,
    LegendControl,
)
import geopandas as gpd
import pandas as pd
import plotly.express as px

# =====================================================
# LOAD DATA
# =====================================================
cas = gpd.read_file("Data/CAS.geojson").to_crs(4326)
cycling_network = gpd.read_file("Data/Cycling_Network.shp").to_crs(4326)

# =====================================================
# CLEAN DATA
# =====================================================
cas = cas[cas.geometry.notnull()].copy()
cycling_network = cycling_network[cycling_network.geometry.notnull()].copy()

cas["bicycle"] = pd.to_numeric(cas["bicycle"], errors="coerce")
cas = cas.dropna(subset=["bicycle"])

# =====================================================
# UI
# =====================================================
app_ui = ui.page_fluid(

    # ---------------- TITLE ----------------
    ui.div(
        ui.h1("🚴 Auckland Bicycle Crash Dashboard",
              class_="display-5 fw-bold"),
        ui.p(
            "Explore bicycle crashes and cycling infrastructure across Auckland.",
            class_="lead"
        ),
        class_="p-4 mb-4 bg-light rounded-3 shadow-sm"
    ),

    # ---------------- HELP CARD ----------------
    ui.card(
        ui.card_header("How to use this dashboard"),
        ui.p(
            "Use the filters on the left to explore crash patterns. "
            "The map and chart update automatically."
        ),
        class_="mb-4"
    ),

    # ---------------- SIDEBAR LAYOUT ----------------
    ui.layout_sidebar(

        # =================================================
        # SIDEBAR
        # =================================================
        ui.sidebar(

            ui.h4("Filters"),

            # INPUT 1
            ui.input_slider(
                "bicycle_slider",
                "Number of bicycles involved",
                min=1,
                max=5,
                value=[1, 5]
            ),

            # INPUT 2
            ui.input_checkbox_group(
                "TYPEOFFACI",
                "Cycling facility type",
                choices=sorted(
                    cycling_network["TYPEOFFACI"]
                    .dropna()
                    .unique()
                    .tolist()
                ),
                selected=sorted(
                    cycling_network["TYPEOFFACI"]
                    .dropna()
                    .unique()
                    .tolist()
                ),
            ),

            # INPUT 3
            ui.input_selectize(
                "LOCALBOARD",
                "Local board",
                choices=['Howick', 'Upper Harbour', 'Orakei', 'Henderson - Massey', 'Waitakere Ranges', 'Puketapapa', 'Whau', 'Devonport-Takapuna', 'Manurewa', 'Hibiscus and Bays', 'Kaipatiki', 'Albert - Eden', 'Waitemata', 'Mangere - Otahuhu', 'Maungakiekie - Tamaki', 'Otara - Papatoetoe', 'Henderson Massey', 'Waiheke', 'Kaipataki', 'Papakura', 'Rodney','Franklin'],
                selected=[],
                multiple=True,
            ),

            # INPUT 4
            ui.input_radio_buttons(
                "map_theme",
                "Map theme",
                choices={
                    "light": "Light",
                    "dark": "Dark"
                },
                selected="light"
            ),

            # INPUT 5
            ui.input_action_button(
                "reset",
                "Reset filters",
                class_="btn-primary"
            ),

            width=350,
            open="desktop",
        ),

        # =================================================
        # MAIN PANEL
        # =================================================
        ui.layout_columns(

            # ---------------- MAP CARD ----------------
            ui.card(
                ui.card_header("Interactive Crash Map"),
                output_widget("map"),
                full_screen=True,
                height="650px",
                class_="shadow-sm"
            ),

            # ---------------- CHART CARD ----------------
            ui.card(
                ui.card_header("Crash Counts"),
                output_widget("crash_plot"),
                full_screen=True,
                height="650px",
                class_="shadow-sm"
            ),

            col_widths=[7, 5],
        ),
    ),

    # =================================================
    # KPI CARDS
    # =================================================
    ui.layout_columns(

        ui.value_box(
            "Total Crashes",
            ui.output_text("total_crashes"),
            showcase="🚨",
            theme="bg-danger"
        ),

        ui.value_box(
            "Cycle Routes",
            ui.output_text("total_routes"),
            showcase="🛣️",
            theme="bg-success"
        ),

        ui.value_box(
            "Selected Boards",
            ui.output_text("selected_boards"),
            showcase="📍",
            theme="bg-primary"
        ),
    ),

    title="Auckland Bicycle Crash Dashboard",
)

# =====================================================
# SERVER
# =====================================================
def server(input, output, session):

    # =================================================
    # MAP SETUP
    # =================================================
    m = Map(
        center=(-36.84, 174.76),
        zoom=10,
        basemap=basemaps.CartoDB.Positron,
        scroll_wheel_zoom=True,
    )

    # Cycling network layer
    cycle_layer = GeoJSON(
        data={},
        style={
            "color": "#2E8B57",
            "weight": 3,
            "opacity": 0.8,
        },
        name="Cycling Network"
    )

    # Crash point layer
    crash_layer = LayerGroup(name="Crash Locations")

    # Add layers
    m.add_layer(cycle_layer)
    m.add_layer(crash_layer)

    # Layer controls
    m.add_control(LayersControl(position="topright"))

    # Legend
    legend = LegendControl(
        {
            "Cycle routes": "#2E8B57",
            "Crash points": "blue",
        },
        name="Legend",
        position="bottomright"
    )

    m.add_control(legend)

    # =================================================
    # SHARED REACTIVE FILTER
    # =================================================
    @reactive.calc
    def filtered_data():

        bike_range = input.bicycle_slider()
        selected_facilities = input.TYPEOFFACI()
        selected_boards = input.LOCALBOARD()

        # Crash filtering
        filtered_crash = cas[
            cas["bicycle"].between(
                bike_range[0],
                bike_range[1]
            )
        ]

        # Cycling network filtering
        filtered_cycle = cycling_network.copy()

        if selected_facilities:
            filtered_cycle = filtered_cycle[
                filtered_cycle["TYPEOFFACI"].isin(
                    selected_facilities
                )
            ]

        if selected_boards:
            filtered_cycle = filtered_cycle[
                filtered_cycle["LOCALBOARD"].isin(
                    selected_boards
                )
            ]

        return filtered_crash, filtered_cycle

    # =================================================
    # RESET BUTTON
    # =================================================
    @reactive.effect
    @reactive.event(input.reset)
    def _():

        ui.update_slider(
            "bicycle_slider",
            value=[1, 5]
        )

        ui.update_checkbox_group(
            "TYPEOFFACI",
            selected=sorted(
                cycling_network["TYPEOFFACI"]
                .dropna()
                .unique()
                .tolist()
            )
        )

        ui.update_selectize(
            "LOCALBOARD",
            selected=[]
        )

    # =================================================
    # MAP OUTPUT
    # =================================================
    @render_widget
    def map():
        return m

    # =================================================
    # UPDATE MAP
    # =================================================
    @reactive.effect
    def update_map():

        filtered_crash, filtered_cycle = filtered_data()

        # Change map theme
        if input.map_theme() == "dark":
            m.basemap = basemaps.CartoDB.DarkMatter
        else:
            m.basemap = basemaps.CartoDB.Positron

        # Update cycling network
        cycle_layer.data = filtered_cycle.__geo_interface__

        # Clear old crash markers
        crash_layer.clear_layers()

        markers = []

        # Limit markers for performance
        sample_data = filtered_crash.head(1500)

        for _, row in sample_data.iterrows():

            geom = row.geometry

            if geom is None:
                continue

            markers.append(
                CircleMarker(
                    location=(geom.y, geom.x),
                    radius=4,
                    color="blue",
                    fill_color="blue",
                    fill_opacity=0.6,
                    stroke=False,
                )
            )

        crash_layer.layers = tuple(markers)

    # =================================================
    # PLOT OUTPUT
    # =================================================
    @render_widget
    def crash_plot():

        filtered_crash, _ = filtered_data()

        summary = (
            filtered_crash.groupby("bicycle")
            .size()
            .reset_index(name="Crash Count")
        )

        fig = px.bar(
            summary,
            x="bicycle",
            y="Crash Count",
            color="Crash Count",
            color_continuous_scale="Blues",
            labels={
                "bicycle": "Bicycles involved"
            },
            title="Crash Frequency"
        )

        fig.update_layout(
            template="plotly_white",
            height=550,
            title_x=0.5,
            margin=dict(
                l=20,
                r=20,
                t=50,
                b=20
            ),
        )

        return fig

    # =================================================
    # KPI OUTPUTS
    # =================================================
    @render.text
    def total_crashes():

        filtered_crash, _ = filtered_data()

        return f"{len(filtered_crash):,}"

    @render.text
    def total_routes():

        _, filtered_cycle = filtered_data()

        return f"{len(filtered_cycle):,}"

    @render.text
    def selected_boards():

        boards = input.LOCALBOARD()

        if len(boards) == 0:
            return "All"

        return str(len(boards))

# =====================================================
# APP
# =====================================================
app = App(app_ui, server)