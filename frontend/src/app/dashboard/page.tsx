"use client";

import React, { useState } from "react";
import { Button } from "react-bootstrap";
import AddExpenseModal from "@/components/AddExpenseModal";
import EditExpenseModal from "@/components/EditExpenseModal";
import PieChart from "@/components/charts/PieChart";
import StackedBarChart from "@/components/charts/StackedBarChart";

// 1) Define an interface (or type) for your Expense shape
interface Expense {
  id: number;
  description: string;
  category: string;
  sub_category: string;
  date_of_expense: string;
  cost: number;
}

export default function DashboardPage() {
  // 2) Use the Expense type (plus null) for your state
  const [editingExpense, setEditingExpense] = useState<Expense | null>(null);
  const [showAddModal, setShowAddModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);

  // 3) Actually call this function in your JSX to avoid the “unused” error
  const openEditModal = (expense: Expense) => {
    setEditingExpense(expense);
    setShowEditModal(true);
  };

  // Example “dummy” data for charts
  const chartData = {
    categories: ["Food", "Rent", "Utilities"],
    amounts: [150, 800, 120],
    dates: ["May 2023", "June 2023"],
    categoryData: [
      {
        label: "Food",
        data: [100, 50],
        backgroundColor: "rgba(255, 99, 132, 0.2)",
      },
      {
        label: "Rent",
        data: [800, 800],
        backgroundColor: "rgba(54, 162, 235, 0.2)",
      },
      {
        label: "Utilities",
        data: [50, 70],
        backgroundColor: "rgba(255, 206, 86, 0.2)",
      },
    ],
  };

  // Example array of expenses
  const [expenses] = useState<Expense[]>([
    {
      id: 1,
      description: "Groceries",
      category: "Food",
      sub_category: "Other",
      date_of_expense: "2023-05-10",
      cost: 50.0,
    },
    {
      id: 2,
      description: "Electric bill",
      category: "Utilities",
      sub_category: "Other",
      date_of_expense: "2023-05-12",
      cost: 70.0,
    },
  ]);

  return (
    <div className="container">
      <h1>Dashboard</h1>

      <Button onClick={() => setShowAddModal(true)}>Add Expense</Button>

      {/* Example rendering of expense list to show how to use openEditModal */}
      <ul style={{ marginTop: "1rem" }}>
        {expenses.map((exp) => (
          <li key={exp.id}>
            <p>Description: {exp.description}</p>
            <p>Category: {exp.category}</p>
            <p>Cost: {exp.cost}</p>
            <Button variant="info" onClick={() => openEditModal(exp)}>
              Edit
            </Button>
          </li>
        ))}
      </ul>

      <AddExpenseModal
        show={showAddModal}
        onClose={() => setShowAddModal(false)}
      />
      <EditExpenseModal
        show={showEditModal}
        onClose={() => setShowEditModal(false)}
        expense={editingExpense}
      />

      {/* Charts */}
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
    </div>
  );
}
