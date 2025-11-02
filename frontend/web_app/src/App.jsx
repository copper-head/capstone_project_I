import React, { useEffect, useState } from "react";

function App() {
  const [apiStatus, setApiStatus] = useState("checking...");
  const [error, setError] = useState("");

  useEffect(() => {
    fetch("/api/health")
      .then((res) => {
        if (!res.ok) throw new Error("API responded with " + res.status);
        return res.json();
      })
      .then((data) => {
        setApiStatus(data.status || JSON.stringify(data));
      })
      .catch((err) => {
        setApiStatus("unavailable");
        setError(err.message);
      });
  }, []);

  return (
    <div style={{ fontFamily: "system-ui, sans-serif", padding: "2rem" }}>
      <h1>React + FastAPI starter</h1>
      <p>
        This is the base web app. Edit <code>src/App.jsx</code> to start building.
      </p>

      <div style={{ marginTop: "1.5rem" }}>
        <h2>Backend status</h2>
        <p>
          API: <strong>{apiStatus}</strong>
        </p>
        {error ? <pre style={{ color: "crimson" }}>{error}</pre> : null}
      </div>
    </div>
  );
}

export default App;