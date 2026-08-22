import apiClient from "./client";

export async function fetchNearbyTrucks(lat, lng, radiusKm = 3) {
  const response = await apiClient.get("/trucks/nearby/", {
    params: { lat, lng, radius_km: radiusKm },
  });
  return response.data;
}

export async function searchTrucks(query) {
  const response = await apiClient.get("/search/", {
    params: { q: query },
  });
  return response.data;
}

export async function fetchAllTrucks(page = 1) {
  const response = await apiClient.get("/trucks/", {
    params: { page },
  });
  return response.data;
}