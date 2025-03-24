"use client";

import React, { useEffect, useState } from "react";
import { Button } from "react-bootstrap";
// import AddExpenseModal from "@/components/AddExpenseModal";
import { EditExpenseModal } from "@/components/EditExpenseModal";
import { Transaction } from "@/components/interfaces/transaction";
import PieChart from "@/components/charts/PieChart";
import StackedBarChart from "@/components/charts/StackedBarChart";
import ImportTransactionsModal from "@/components/ImportTransactionsModal";
import LinkBankModal from "@/components/LinkBankModal";

/**
 * The Flask /dashboard endpoint now returns this structure:
 * {
 *   user: { id: string },
 *   transactions: Array<GoCardlessTransaction>,
 *   chart_data: {
 *     categories: string[],
 *     amounts: number[],
 *     dates: string[],
 *     categoryData: Array<{
 *       label: string,
 *       data: number[],
 *       backgroundColor: string
 *     }>
 *   }
 * }
 *
 * Where each transaction might look like:
 * {
 *   id: string,
 *   transactionId?: string,
 *   bookingDate?: string,
 *   amount: number,
 *   currency: string,
 *   transactionType?: "expense" | "income",
 *   category?: string,
 *   sub_category?: string,
 *   debtorName?: string,
 *   creditorName?: string,
 *   ...
 * }
 */

// Interface for the chart data
interface ChartData {
  categories: string[];
  amounts: number[];
  dates: string[];
  categoryData: {
    label: string;
    data: number[];
    backgroundColor: string;
  }[];
}

export default function DashboardPage() {
  // State for transactions and chart data
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [chartData, setChartData] = useState<ChartData | null>(null);

  // State for modals
  // const [showAddModal, setShowAddModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [editingTransaction, setEditingTransaction] =
    useState<Transaction | null>(null);

  // For any potential errors or loading states
  const [errorMessage, setErrorMessage] = useState("");
  const [loading, setLoading] = useState(true);

  // import modal
  const [showImportModal, setShowImportModal] = useState(false);
  const [showLinkBankModal, setShowLinkBankModal] = useState(false);

  // On component mount, fetch data from the Flask `/dashboard`
  useEffect(() => {
    (async () => {
      try {
        const resp = await fetch("http://localhost:8000/dashboard", {
          method: "GET",
          credentials: "include", // send session cookie
        });

        if (resp.status === 401) {
          // Not logged in, redirect to /login
          window.location.href = "/login";
          return;
        }
        if (!resp.ok) {
          // Some other error, e.g. 500
          const errorText = await resp.text();
          setErrorMessage(`Error fetching dashboard data: ${errorText}`);
          setLoading(false);
          return;
        }

        // Parse the JSON result
        const data = await resp.json();
        // data should look like:
        // {
        //   user: { id: string },
        //   transactions: [...],
        //   chart_data: {
        //     categories: [...],
        //     amounts: [...],
        //     dates: [...],
        //     categoryData: [...],
        //   }
        // }

        // Update states
        setTransactions(data.transactions || []);
        setChartData(data.chart_data || null);
      } catch (err) {
        setErrorMessage(`Failed to reach server: ${err}`);
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  const openEditModal = (txn: Transaction) => {
    setEditingTransaction(txn);
    setShowEditModal(true);
  };

  // If still loading, show a spinner or text
  if (loading) {
    return <div className="container mt-5">Loading Dashboard...</div>;
  }

  // If there's an error, show it
  if (errorMessage) {
    return (
      <div className="container mt-5">
        <h2>Error</h2>
        <p>{errorMessage}</p>
      </div>
    );
  }

  return (
    <div className="container">
      <h1>Dashboard</h1>

      {/* <Button onClick={() => setShowAddModal(true)}>Add Transaction</Button> */}

      {/* Link Bank Account Button => opens the LinkBankModal */}
      <Button
        onClick={() => setShowLinkBankModal(true)}
        style={{ marginRight: "1rem" }}
      >
        Link Bank Account
      </Button>

      <LinkBankModal
        show={showLinkBankModal}
        onClose={() => setShowLinkBankModal(false)}
      />
      <Button
        onClick={async () => {
          try {
            const resp = await fetch(
              "http://localhost:8000/banks/refresh_link",
              {
                method: "POST",
                credentials: "include",
              }
            );
            if (!resp.ok) {
              const data = await resp.json();
              console.error("Failed to refresh link status:", data);
              return;
            }
            const data = await resp.json();
            console.log("Refreshed link status:", data);
            // Possibly reload or update local state
            window.location.reload();
          } catch (err) {
            console.error("Error refreshing link status:", err);
          }
        }}
        style={{ marginRight: "1rem" }}
      >
        Refresh Link Status
      </Button>
      {/* Import Transactions Button */}
      <Button onClick={() => setShowImportModal(true)}>
        Import Transactions
      </Button>

      {/* The Import Transactions modal */}
      <ImportTransactionsModal
        show={showImportModal}
        onClose={() => setShowImportModal(false)}
      />
      {/* Render the transaction list */}
      <ul style={{ marginTop: "1rem" }}>
        {transactions.map((txn) => (
          <li key={txn.id}>
            <p>Transaction ID: {txn.transactionId || "(no ID)"}</p>
            <p>Date: {txn.bookingDate || "(pending)"}</p>
            <p>
              Amount: {txn.transactionAmount.amount}{" "}
              {txn.transactionAmount.currency}
            </p>
            <p>Type: {txn.transactionType}</p>
            <p>Category: {txn.category || "Uncategorized"}</p>
            <p>Sub-category: {txn.sub_category || "(none)"}</p>
            {txn.debtorName && <p>Debtor: {txn.debtorName}</p>}
            {txn.creditorName && <p>Creditor: {txn.creditorName}</p>}
            <Button variant="info" onClick={() => openEditModal(txn)}>
              Edit
            </Button>
          </li>
        ))}
      </ul>

      {/* Modals */}
      {/* <AddExpenseModal
        show={showAddModal}
        onClose={() => setShowAddModal(false)}
      /> */}
      <EditExpenseModal
        show={showEditModal}
        onClose={() => setShowEditModal(false)}
        expense={editingTransaction}
      />

      {/* Charts */}
      {chartData ? (
        <div
          className="charts-row"
          style={{ display: "flex", marginTop: "2rem" }}
        >
          <div
            className="chart-container pie-chart"
            style={{ flex: 0.5, marginRight: "1rem" }}
          >
            <h2>Expenses by Category</h2>
            <div style={{ height: "400px" }}>
              <PieChart
                categories={chartData.categories}
                amounts={chartData.amounts}
              />
            </div>
          </div>
          <div className="chart-container bar-chart" style={{ flex: 0.5 }}>
            <h2>Expenses by Category Over Time</h2>
            <div style={{ height: "400px" }}>
              <StackedBarChart
                dates={chartData.dates}
                categoryData={chartData.categoryData}
              />
            </div>
          </div>
        </div>
      ) : (
        <p>No chart data available.</p>
      )}
    </div>
  );
}
