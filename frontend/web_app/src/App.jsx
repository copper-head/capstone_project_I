import { BrowserRouter as Router, Routes, Route, Link, Navigate } from "react-router-dom";
import UploadPage from "./pages/UploadPage.jsx";
import HomePage from "./pages/HomePage";
import React, { useEffect, useState } from "react";

function App() {

  return (
    <Router>
      <div style={{ fontFamily: "sans-serif" }}>
        <main style={{ padding: "20px" }}>
          <nav style={{ marginBottom: 16 }}>
            <Link to="/upload" style={{ marginRight: 12 }}>Guest Upload</Link>
          </nav>
          <Routes>
            <Route path="/" element={<Navigate to="/home" replace />} />
            <Route path="/home" element={<HomePage />} />
            <Route path="/upload" element={<UploadPage />} />
            {/* 404 route */}
            <Route path="*" element={<h2>Page not found</h2>} />
          </Routes>
        </main>
      </div>
    </Router>

  );
}

export default App;