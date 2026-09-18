from typing import List, Dict, Any, Optional


def pixel_to_geojson_polygon(
    x: int,
    y: int,
    width: int,
    height: int,
    image_width: int,
    image_height: int,
    label: str = "detected_feature",
    confidence: float = 0.9,
    affine_transform: Optional[List[float]] = None,
    crs: str = "EPSG:4326"
) -> Dict[str, Any]:
    """
    Transforms pixel bounding coordinates [x, y, w, h] into standard GeoJSON Feature Polygon.
    If GeoTIFF affine transform is supplied ([a, b, c, d, e, f]), maps to real geographic coordinates.
    Otherwise, maps to normalized [0, 1000] relative spatial coordinate grid.
    """
    if affine_transform and len(affine_transform) >= 6:
        a, b, c, d, e, f = affine_transform[:6]
        # x_geo = a * px + b * py + c
        # y_geo = d * px + e * py + f
        x_min_geo = a * x + b * y + c
        y_max_geo = d * x + e * y + f
        x_max_geo = a * (x + width) + b * (y + height) + c
        y_min_geo = d * (x + width) + e * (y + height) + f

        coords = [[
            [round(x_min_geo, 6), round(y_max_geo, 6)],
            [round(x_max_geo, 6), round(y_max_geo, 6)],
            [round(x_max_geo, 6), round(y_min_geo, 6)],
            [round(x_min_geo, 6), round(y_min_geo, 6)],
            [round(x_min_geo, 6), round(y_max_geo, 6)]
        ]]
    else:
        # Normalized relative bounds (0 to 1000)
        norm_x_min = round((x / max(1, image_width)) * 1000, 1)
        norm_y_min = round((y / max(1, image_height)) * 1000, 1)
        norm_x_max = round(((x + width) / max(1, image_width)) * 1000, 1)
        norm_y_max = round(((y + height) / max(1, image_height)) * 1000, 1)

        coords = [[
            [norm_x_min, norm_y_min],
            [norm_x_max, norm_y_min],
            [norm_x_max, norm_y_max],
            [norm_x_min, norm_y_max],
            [norm_x_min, norm_y_min]
        ]]

    return {
        "type": "Feature",
        "geometry": {
            "type": "Polygon",
            "coordinates": coords
        },
        "properties": {
            "label": label,
            "confidence": round(confidence, 3),
            "pixel_box": {"x": x, "y": y, "width": width, "height": height},
            "crs": crs
        }
    }


def regions_to_geojson_feature_collection(
    regions: List[Dict[str, Any]],
    image_width: int,
    image_height: int,
    affine_transform: Optional[List[float]] = None,
    crs: str = "EPSG:4326"
) -> Dict[str, Any]:
    """Wraps a list of detected regions into a standard GeoJSON FeatureCollection."""
    features = []
    for reg in regions:
        x = reg.get("x", 0)
        y = reg.get("y", 0)
        w = reg.get("width", 0)
        h = reg.get("height", 0)
        label = reg.get("label", "region")
        conf = reg.get("confidence", 0.9)

        feat = pixel_to_geojson_polygon(
            x=x, y=y, width=w, height=h,
            image_width=image_width, image_height=image_height,
            label=label, confidence=conf,
            affine_transform=affine_transform, crs=crs
        )
        features.append(feat)

    return {
        "type": "FeatureCollection",
        "features": features,
        "crs": {
            "type": "name",
            "properties": {"name": crs}
        }
    }
