import React, { createContext, useState, useEffect } from "react";
import axios from "axios";

  export const AuthContext = createContext();

  export const AuthProvider = ({ children }) => {
    const [user, setUser] = useState(null);
    const [accessToken, setAccessToken] = useState(localStorage.getItem("access"));
    const [loading, setLoading] = useState(true);

  // ✅ Cargar sesión si hay token guardado
  useEffect(() => {
    if (accessToken) {
      axios
        .get("http://localhost:8000/api/profile/", {
          headers: { Authorization: `Bearer ${accessToken}` },
        })
        .then((res) => {
          setUser(res.data);
        })
        .catch(() => {
          logout();
        })
        .finally(() => setLoading(false));
    } else {
      setLoading(false);
    }
  }, []);

  // ✅ Login
  const login = async (username, password) => {
    try {
      const response = await axios.post("http://localhost:8000/api/login/", {
        username,
        password,
      });
      const { access, refresh } = response.data;
      localStorage.setItem("access", access);
      localStorage.setItem("refresh", refresh);
      setAccessToken(access);
      // Obtener info del usuario
      const userResponse = await axios.get("http://localhost:8000/api/profile/", {
        headers: { Authorization: `Bearer ${access}` },
      });
      setUser(userResponse.data);
      return true;
    } catch (err) {
      console.error("Error en login:", err);
      return false;
    }
  };

  // ✅ Logout
  const logout = () => {
    localStorage.removeItem("access");
    localStorage.removeItem("refresh");
    setAccessToken(null);
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, login, logout, accessToken, loading }}>
      {children}
    </AuthContext.Provider>
  );
};
