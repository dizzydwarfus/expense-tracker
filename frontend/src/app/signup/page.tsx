"use client";

import React, { useState } from "react";

export default function SignupPage() {
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [nickname, setNickname] = useState("");
  const [errorMessage, setErrorMessage] = useState(""); // For displaying error info

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const resp = await fetch("http://localhost:8000/signup", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, email, nickname, password }),
        credentials: "include",
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

        console.error("Signup error:", errorText);
        setErrorMessage(errorText || "Something went wrong during Signup.");
        window.location.href = "/signup";
        return;
      }
      window.location.href = "/login";
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="container">
      <h2 className="text-center mt-5">Sign Up</h2>
      <div className="row justify-content-center">
        <div className="col-lg-5">
          {/* Show error if there is one */}
          {errorMessage && (
            <div className="alert alert-danger mt-3" role="alert">
              {errorMessage}
            </div>
          )}
          <form onSubmit={handleSubmit}>
            <div className="form-group mt-4">
              <label>Username</label>
              <input
                type="text"
                className="form-control mt-2"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                required
              />
            </div>
            <div className="form-group mt-4">
              <label>Nickname</label>
              <input
                type="text"
                className="form-control mt-2"
                value={nickname}
                onChange={(e) => setNickname(e.target.value)}
                required
              />
            </div>
            <div className="form-group mt-4">
              <label>Email address</label>
              <input
                type="email"
                className="form-control mt-2"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
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
            <button type="submit" className="btn btn-primary mt-4">
              Sign Up
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
