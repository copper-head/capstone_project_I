export default function HomePage() {
  return (
    <div
      style={{
        maxWidth: "700px",
        margin: "80px auto",
        textAlign: "center",
        fontFamily: "sans-serif",
      }}
    >
      <h1 style={{ fontSize: "2.5rem", marginBottom: "10px" }}>
        Image ➜ LaTeX Converter
      </h1>

      <p style={{ fontSize: "1.1rem", color: "#555", marginBottom: "40px" }}>
        Upload handwritten math or images and instantly convert them into clean,
        editable LaTeX.
      </p>

      <div style={{ display: "flex", justifyContent: "center", gap: "20px" }}>
        <a
          href="/signup"
          style={{
            padding: "12px 24px",
            backgroundColor: "#007bff",
            color: "white",
            borderRadius: "6px",
            textDecoration: "none",
            fontSize: "1rem",
          }}
        >
          Sign Up
        </a>

        <a
          href="/login"
          style={{
            padding: "12px 24px",
            backgroundColor: "#28a745",
            color: "white",
            borderRadius: "6px",
            textDecoration: "none",
            fontSize: "1rem",
          }}
        >
          Log In
        </a>

        {/* Upload as Guest */}
        <a
          href="/upload"
          style={{
            padding: "12px 24px",
            backgroundColor: "#6c757d",
            color: "white",
            borderRadius: "6px",
            textDecoration: "none",
            fontSize: "1rem",
          }}
        >
          Upload as Guest
        </a>
      </div>
    </div>
  );
}