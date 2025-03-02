"use client";

import React, { useState } from "react";
import { Modal, Button, Form } from "react-bootstrap";

interface AddExpenseModalProps {
  show: boolean;
  onClose: () => void;
}

/**
 * A fully React-based modal for adding an expense.
 * No jQuery needed – uses React-Bootstrap's <Modal>.
 */
export default function AddExpenseModal({
  show,
  onClose,
}: AddExpenseModalProps) {
  const [description, setDescription] = useState("");
  const [category, setCategory] = useState("");
  const [subCategory, setSubCategory] = useState("");
  const [date, setDate] = useState("");
  const [cost, setCost] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const resp = await fetch("http://localhost:5000/add_expense", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          expenseDescription: description,
          expenseCategory: category,
          expenseSubCategory: subCategory,
          expenseDate: date,
          expenseCost: cost,
        }),
        credentials: "include",
      });
      if (!resp.ok) {
        // handle error
        console.error("Failed to add expense");
        return;
      }
      // If success, close modal and reload or refetch
      onClose();
      window.location.reload();
    } catch (err) {
      console.error("Error adding expense:", err);
    }
  };

  return (
    <Modal show={show} onHide={onClose} centered>
      <Modal.Header closeButton>
        <Modal.Title>Add Expense</Modal.Title>
      </Modal.Header>
      <Modal.Body>
        <Form onSubmit={handleSubmit}>
          <Form.Group className="mb-3">
            <Form.Label>Description</Form.Label>
            <Form.Control
              type="text"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              required
            />
          </Form.Group>

          <Form.Group className="mb-3">
            <Form.Label>Category</Form.Label>
            <Form.Control
              type="text"
              value={category}
              onChange={(e) => setCategory(e.target.value)}
              required
            />
          </Form.Group>

          <Form.Group className="mb-3">
            <Form.Label>Sub-category</Form.Label>
            <Form.Control
              type="text"
              value={subCategory}
              onChange={(e) => setSubCategory(e.target.value)}
            />
          </Form.Group>

          <div className="row">
            <div className="col">
              <Form.Group className="mb-3">
                <Form.Label>Date</Form.Label>
                <Form.Control
                  type="date"
                  value={date}
                  onChange={(e) => setDate(e.target.value)}
                />
              </Form.Group>
            </div>
            <div className="col">
              <Form.Group className="mb-3">
                <Form.Label>Cost</Form.Label>
                <Form.Control
                  type="number"
                  step="0.01"
                  value={cost}
                  onChange={(e) => setCost(e.target.value)}
                />
              </Form.Group>
            </div>
          </div>

          <div className="d-flex justify-content-end">
            <Button variant="secondary" onClick={onClose} className="mr-2">
              Close
            </Button>
            <Button variant="primary" type="submit">
              Add Expense
            </Button>
          </div>
        </Form>
      </Modal.Body>
    </Modal>
  );
}
