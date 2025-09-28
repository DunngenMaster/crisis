export type LngLat = [number, number];

export async function getRouteGeoJSON(
  start: LngLat,
  end: LngLat,
  profile: "driving-traffic" | "driving" | "walking" | "cycling" = "driving-traffic"
) {
  const token = import.meta.env.VITE_MAPBOX_TOKEN as string;
  const url =
    `https://api.mapbox.com/directions/v5/mapbox/${profile}/` +
    `${start[0]},${start[1]};${end[0]},${end[1]}?overview=full&geometries=geojson&annotations=duration&access_token=${token}`;
  const res = await fetch(url);
  if (!res.ok) throw new Error("Directions API failed");
  const data = await res.json();
  const route = data.routes?.[0]?.geometry;
  if (!route) throw new Error("No route");
  return {
    type: "Feature",
    properties: {},
    geometry: route
  } as GeoJSON.Feature;
}
