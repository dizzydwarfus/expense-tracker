import "bootstrap/dist/css/bootstrap.min.css";
import "@/globals.css";

import { ReactNode } from "react";

export const metadata = {
  title: "Expense Tracker",
  description: "An expense tracking application",
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
