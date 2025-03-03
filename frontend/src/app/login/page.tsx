"use client";

import React, { useState } from "react";

export default function LoginPage() {
  const [usernameEmail, setUsernameEmail] = useState("");
  const [password, setPassword] = useState("");
  const [errorMessage, setErrorMessage] = useState(""); // For displaying error info

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMessage(""); // clear any previous errors

    try {
      const resp = await fetch("http://127.0.0.1:5000/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          username_email: usernameEmail,
          password: password,
        }),
        credentials: "include", // If you want to pass cookies for session
      });

      if (!resp.ok) {
        // Attempt to parse error message from the response
        let errorText;
        try {
          // If your backend returns JSON errors
          const data = await resp.json();
          errorText = data.error || JSON.stringify(data);
        } catch {
          // fallback if it's not valid JSON
          errorText = await resp.text();
        }

        console.error("Login error:", errorText);
        setErrorMessage(errorText || "Something went wrong during login.");
        return;
      }

      // If successful
      window.location.href = "/dashboard";
    } catch (err) {
      console.error("Login request failed:", err);
      setErrorMessage(
        "Failed to reach the server. Please check your connection or try again later."
      );
    }
  };

  return (
    <div className="container">
      <h2 className="text-center mt-5">Login</h2>

      {/* Show error if there is one */}
      {errorMessage && (
        <div className="alert alert-danger mt-3" role="alert">
          {errorMessage}
        </div>
      )}

      <form onSubmit={handleSubmit} className="mt-3">
        <div className="form-group mt-4">
          <label>Email or Username</label>
          <input
            type="text"
            className="form-control mt-2"
            value={usernameEmail}
            onChange={(e) => setUsernameEmail(e.target.value)}
            required
          />
        </div>
        <div className="form-group mt-4">
          <label>Password</label>
          <input
            type="password"
            className="form-control mt-2"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
        </div>
        <button type="submit" className="btn btn-light mt-4">
          Login
        </button>
      </form>
    </div>
  );
}
