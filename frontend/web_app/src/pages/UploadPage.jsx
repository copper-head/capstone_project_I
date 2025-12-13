import { useState } from "react";

export default function UploadPage() {
  const [file, setFile] = useState(null);
  const [status, setStatus] = useState("");
  const [isUploading, setIsUploading] = useState(false);

  const handleFileChange = (event) => {
    setFile(event.target.files[0]);
    setStatus("");
  };

  const handleUpload = async () => {
    if (!file) {
      setStatus("Please select a file first.");
      return;
    }

    const formData = new FormData();
    formData.append("file", file); // "file" must match what your backend expects

    try {
      setIsUploading(true);
      setStatus("Uploading...");

      // use the dev server proxy (see `vite.config.js`) so we avoid CORS and
      // can switch backend location without changing the client code.
      const response = await fetch("/api/upload", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        const text = await response.text();
        throw new Error(text || `Upload failed with status ${response.status}`);
      }

      setStatus("✅ File uploaded successfully!");
    } catch (err) {
      console.error(err);
      setStatus(`❌ Upload failed: ${err.message}`);
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div
      style={{
        maxWidth: "500px",
        margin: "40px auto",
        padding: "20px",
        border: "1px solid #ddd",
        borderRadius: "8px",
        fontFamily: "sans-serif",
      }}
    >
      <h1 style={{ textAlign: "center" }}>Upload a File</h1>

      <div style={{ marginTop: "20px" }}>
        <input
          type="file"
          onChange={handleFileChange}
          disabled={isUploading}
        />
      </div>

      {file && (
        <p style={{ marginTop: "10px" }}>
          Selected: <strong>{file.name}</strong> ({Math.round(file.size / 1024)} KB)
        </p>
      )}

      <button
        onClick={handleUpload}
        disabled={isUploading}
        style={{
          marginTop: "20px",
          padding: "10px 20px",
          borderRadius: "4px",
          border: "none",
          cursor: isUploading ? "not-allowed" : "pointer",
        }}
      >
        {isUploading ? "Uploading..." : "Upload"}
      </button>

      {status && (
        <p style={{ marginTop: "15px" }}>
          {status}
        </p>
      )}
    </div>
  );
}