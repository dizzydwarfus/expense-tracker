"use client"; // So you can use client-side features, if needed

import Link from "next/link";
import React from "react";

export default function Home() {
  return (
    <div className="container text-center" style={{ marginTop: "5rem" }}>
      <h1>Welcome to the Expense Tracker</h1>
      <Link className="btn btn-light mt-3" href="/login">
        Log In
      </Link>
      <Link className="btn btn-light mt-3 ml-2" href="/signup">
        Sign Up
      </Link>
    </div>
  );
}
