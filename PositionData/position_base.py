class PositionBase:
    def __init__(self):
        """
        Initialize the GeoData object.
        """
        pass  # Placeholder if you need to initialize anything

    def _export_as_geojson(self, gdf, output_path):
        """
        Export the given GeoDataFrame as a GeoJSON file.

        :param gdf: A GeoDataFrame to be exported.
        :param output_path: Path to save the GeoJSON file.
        """
        # Check if the CRS is EPSG:4326, reproject if not
        if gdf.crs.to_string() != 'EPSG:4326':
            gdf_reprojected = gdf.to_crs(epsg=4326)
        else:
            gdf_reprojected = gdf

        # Export to GeoJSON
        gdf_reprojected.to_file(output_path, driver="GeoJSON")
        print(f"GeoJSON saved to {output_path}")