#!/usr/bin/env python3
import csv
import mercantile


def write_tile_data():
    filename = "wms_256_tiles.csv"
    with open(filename, "w", newline="") as data_file:
        writer = csv.writer(data_file)
        for tile in mercantile.tiles(
                -77.59899950, 38.53900095, -76.05800395, 39.63099797,
                range(8, 18)
        ):
            bounds = mercantile.bounds(tile)
            writer.writerow(bounds)


write_tile_data()
