import React, { createContext, useContext, useState, useEffect } from "react";
import { locationService } from "../api/services";
import { useAuth } from "./AuthContext";

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
      if (res.data && res.data.length > 0) {
        setSelectedLocation((prev) => {
          if (prev) {
            const found = res.data.find((l) => l.id === prev.id);
            if (found) return found;
          }
          return res.data[0];
        });
      }
    } catch (err) {
      console.error("Failed to load locations:", err);
    } finally {
      setLoading(false);
    }
  };

  const { token, user } = useAuth();

  useEffect(() => {
    if (token) {
      fetchLocations();
    } else {
      setLocations([]);
      setSelectedLocation(null);
    }
  }, [token, user?.id]);

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
