import json
from pathlib import Path
import geopandas as gpd
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
from matplotlib.font_manager import FontProperties


class MapModel:
    """
    Taiwan map model.

    Attributes:
    ----------
    crs : str
        Coordinate Reference System
    county_gdf : gpd.GeoDataFrame
        Taiwan counties GeoDataFrame
    town_gdf : gpd.GeoDataFrame
        Taiwan towns GeoDataFrame
    font : FontProperties
        Font properties

    Methods:
    --------
    draw_counties_map(gdf: gpd.GeoDataFrame = None, col: str = None, cmap: str = None) -> plt.Figure, plt.Axes
        Draw Taiwan counties map
    default_counties_map() -> plt.Figure, plt.Axes
        Draw default Taiwan counties map
    draw_towns_map(gdf: gpd.GeoDataFrame = None, col: str = None, cmap: str = None) -> plt.Figure, plt.Axes
        Draw Taiwan towns map
    default_towns_map() -> plt.Figure, plt.Axes
        Draw default Taiwan towns map
    """

    def __init__(self):
        self.crs = "WGS84"
        self.county_gdf = gpd.read_file(
            Path().cwd() / "shp" / "COUNTY_MOI_1090820.shp",
            encoding="utf-8",
            crs=self.crs,
        )
        self.town_gdf = gpd.read_file(
            Path().cwd() / "shp" / "TOWN_MOI_1120825.shp",
            encoding="utf-8",
            crs=self.crs,
        )
        self.font = FontProperties(
            fname=Path().cwd() / "font" / "Urbanist-VariableFont_wght.ttf"
        )
        with open(
            Path().cwd() / "config" / "map_range.json", "r", encoding="utf-8"
        ) as f:
            self._map_range = json.load(f)

        with open(Path().cwd() / "config" / "style.json", "r", encoding="utf-8") as f:
            self._style_list = json.load(f)

    def _inset_zoom_in_map(self, ax, bounds: list, zoom_in_range: dict) -> plt.Axes:
        """Set zoom in map range.

        This method sets the zoom in map range for the given Axes object.

        Parameters:
        -----------
        ax : plt.Axes
            The Axes object to set the zoom in map range for.
        bounds : list
            The bounds of the inset_axes.
        zoom_in_range : dict
            The zoom in map range, specified as a dictionary with the following keys:
            - "min_x": The minimum x-coordinate of the zoom in range.
            - "max_x": The maximum x-coordinate of the zoom in range.
            - "min_y": The minimum y-coordinate of the zoom in range.
            - "max_y": The maximum y-coordinate of the zoom in range.

        Returns:
        --------
        add_ax : plt.Axes
            The Inset Axes object with the zoom in map range set.
        """
        add_ax = ax.inset_axes(bounds)
        add_ax.set_xlim(zoom_in_range["min_x"], zoom_in_range["max_x"])
        add_ax.set_ylim(zoom_in_range["min_y"], zoom_in_range["max_y"])
        add_ax.set_xticks([])
        add_ax.set_yticks([])
        return add_ax

    def _set_subset_map_range(self, ax) -> list[plt.Axes]:
        """
        Set subset map range.

        This method sets the subset map range for the given Axes object.

        Parameters:
        -----------
        ax : plt.Axes
            The Axes object to set the subset map range for.

        Returns:
        --------
        subset_axes : list[plt.Axes]
            The list of Axes objects with the subset map range set.
        """
        map_range = self._map_range

        # mainland range
        ax.set_xlim(map_range["taiwan"]["min_x"], map_range["taiwan"]["max_x"])
        ax.set_ylim(map_range["taiwan"]["min_y"], map_range["taiwan"]["max_y"])

        # penghu range
        pen = self._inset_zoom_in_map(ax, [0.02, 0.25, 0.25, 0.40], map_range["penghu"])

        # kinmen range
        kin = self._inset_zoom_in_map(ax, [0.02, 0.58, 0.25, 0.25], map_range["kinmen"])
        kin_wuqiu = self._inset_zoom_in_map(
            ax, [0.22, 0.69, 0.06, 0.06], map_range["kinmen_wuqiu"]
        )

        # lienchiang range
        lie = self._inset_zoom_in_map(
            ax, [0.02, 0.734, 0.25, 0.25], map_range["lienchiang"]
        )
        lie_dongyin = self._inset_zoom_in_map(
            ax, [0.22, 0.87, 0.06, 0.06], map_range["lienchiang_dongyin"]
        )
        lie_juguang = self._inset_zoom_in_map(
            ax, [0.22, 0.80, 0.06, 0.06], map_range["lienchiang_juguang"]
        )
        return [ax, pen, kin, kin_wuqiu, lie, lie_dongyin, lie_juguang]

    def _colorbar(self, ax, vmin: float, vmax: float, cmap: str) -> plt.colorbar:
        """Set colorbar.

        This method sets the colorbar for the given Axes object.

        Parameters:
        -----------
        ax : plt.Axes
            The Axes object to set the colorbar for.
        vmin : float
            The minimum value of the colorbar.
        vmax : float
            The maximum value of the colorbar.
        cmap : str
            The colormap of the colorbar.

        Returns:
        --------
        cbar : plt.colorbar
            The colorbar object.
        """
        sm = plt.cm.ScalarMappable(cmap=cmap, norm=plt.Normalize(vmin=vmin, vmax=vmax))
        sm._A = []
        cbar = plt.colorbar(sm, ax=ax, orientation="vertical", pad=-0.05, shrink=0.5)

        # set tricks label font family
        for label in cbar.ax.get_yticklabels():
            label.set_fontproperties(self.font)

        cbar.ax.tick_params(labelsize=12)
        cbar.formatter = plt.FuncFormatter(lambda x, _: "{:,.0f}".format(x))
        cbar.locator = MaxNLocator(nbins=6)
        return cbar

    def draw_counties_map(
        self, gdf: gpd.GeoDataFrame = None, col: str = None, cmap: str = None
    ):
        """
        Draw Taiwan counties map.

        This method draws the Taiwan counties map with the given GeoDataFrame and column.

        Parameters:
        -----------
        gdf : gpd.GeoDataFrame
            The GeoDataFrame to plot.
        col : str
            The column to plot.
        cmap : str
            The colormap to use.

        Returns:
        --------
        fig : plt.Figure
            The Figure object.
        ax : plt.Axes
            The Axes object.
        """
        style = self._style_list["default"]
        fig, ax = plt.subplots(
            figsize=(style["width"], style["height"]), dpi=style["dpi"]
        )
        ax.axis("off")

        subset_axes = self._set_subset_map_range(ax)

        if all([gdf is not None, col is not None]):
            cmap = cmap if cmap else "YlGn"
            for axes in subset_axes:
                gdf.plot(ax=axes, column=col, cmap=cmap, legend=False)
                self.county_gdf.boundary.plot(ax=axes, linewidth=0.8, color="black")
            self._colorbar(ax, gdf[col].min(), gdf[col].max(), cmap)
        else:
            for axes in subset_axes:
                self.county_gdf.boundary.plot(ax=axes, linewidth=0.8, color="black")

        return fig, ax

    def default_counties_map(self):
        """Draw default Taiwan counties map."""
        return self.draw_counties_map()

    def draw_towns_map(
        self, gdf: gpd.GeoDataFrame = None, col: str = None, cmap: str = None
    ):
        """Draw Taiwan towns map.

        This method draws the Taiwan towns map with the given GeoDataFrame and column.

        Parameters:
        -----------
        gdf : gpd.GeoDataFrame
            The GeoDataFrame to plot.
        col : str
            The column to plot.
        cmap : str
            The colormap to use.

        Returns:
        --------
        fig : plt.Figure
            The Figure object.
        ax : plt.Axes
            The Axes object.
        """
        style = self._style_list["default"]
        fig, ax = plt.subplots(
            figsize=(style["width"], style["height"]), dpi=style["dpi"]
        )
        ax.axis("off")

        subset_axes = self._set_subset_map_range(ax)

        if all([gdf is not None, col is not None]):
            cmap = cmap if cmap else "YlGn"
            for axes in subset_axes:
                self.town_gdf.boundary.plot(
                    ax=axes, linewidth=0.2, color="black", alpha=0.5, zorder=1
                )
                gdf.plot(ax=axes, column=col, cmap=cmap, legend=False, zorder=2)
                self.county_gdf.boundary.plot(
                    ax=axes, linewidth=0.8, color="black", zorder=3
                )
            self._colorbar(ax, gdf[col].min(), gdf[col].max(), cmap)
        else:
            for axes in subset_axes:
                self.town_gdf.boundary.plot(
                    ax=axes, linewidth=0.2, color="black", alpha=0.5
                )
                self.county_gdf.boundary.plot(ax=axes, linewidth=0.8, color="black")

        return fig, ax

    def default_towns_map(self):
        """Draw default Taiwan towns map."""
        return self.draw_towns_map()
