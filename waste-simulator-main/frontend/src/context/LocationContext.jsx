import React, { createContext, useContext, useState, useEffect } from "react";
import { locationService } from "../api/services";

const LocationContext = createContext(null);

export const LocationProvider = ({ children }) => {
  const [locations, setLocations] = useState([]);
  const [selectedLocation, setSelectedLocation] = useState(null);
  const [loading, setLoading] = useState(false);

  const fetchLocations = async () => {
    setLoading(true);
    try {
      const res = await locationService.list();
      setLocations(res.data);
      if (res.data.length > 0 && !selectedLocation) {
        setSelectedLocation(res.data[0]);
      }
    } catch (err) {
      console.error("Failed to load locations:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchLocations();
  }, []);

  const selectLocationById = (id) => {
    const found = locations.find((l) => l.id === parseInt(id, 10));
    if (found) setSelectedLocation(found);
  };

  return (
    <LocationContext.Provider
      value={{
        locations,
        selectedLocation,
        setSelectedLocation,
        selectLocationById,
        refreshLocations: fetchLocations,
        loading,
      }}
    >
      {children}
    </LocationContext.Provider>
  );
};

export const useLocation = () => useContext(LocationContext);
