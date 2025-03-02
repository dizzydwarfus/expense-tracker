"use client";

import React, { useState } from "react";

export default function LoginPage() {
  const [usernameEmail, setUsernameEmail] = useState("");
  const [password, setPassword] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const resp = await fetch("http://localhost:5000/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username_email: usernameEmail, password }),
        credentials: "include", // If you want to pass cookies for session
      });
      if (!resp.ok) {
        // handle error
        return;
      }
      window.location.href = "/dashboard";
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="container">
      <h2 className="text-center mt-5">Login</h2>
      <form onSubmit={handleSubmit} className="mt-3">
        <div className="form-group">
          <label>Email or Username</label>
          <input
            type="text"
            className="form-control"
            value={usernameEmail}
            onChange={(e) => setUsernameEmail(e.target.value)}
            required
          />
        </div>
        <div className="form-group">
          <label>Password</label>
          <input
            type="password"
            className="form-control"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
        </div>
        <button type="submit" className="btn btn-light">
          Login
        </button>
      </form>
    </div>
  );
}
