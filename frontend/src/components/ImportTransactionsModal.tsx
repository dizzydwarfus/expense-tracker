"use client";

import React, { useState } from "react";
import { Modal, Button, Form } from "react-bootstrap";

interface ImportTransactionsModalProps {
  show: boolean;
  onClose: () => void;
}

export default function ImportTransactionsModal({
  show,
  onClose,
}: ImportTransactionsModalProps) {
  const [dateFrom, setDateFrom] = useState("");
  const [dateTo, setDateTo] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const resp = await fetch("http://localhost:8000/banks/import", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ date_from: dateFrom, date_to: dateTo }),
        credentials: "include",
      });
      if (!resp.ok) {
        const errorData = await resp.json();
        console.error("Failed to import transactions", errorData);
        return;
      }
      // If success, close modal and maybe reload to see new data
      onClose();
      window.location.reload();
    } catch (err) {
      console.error("Error importing transactions:", err);
    }
  };

  return (
    <Modal show={show} onHide={onClose} centered>
      <Modal.Header closeButton>
        <Modal.Title>Import Transactions</Modal.Title>
      </Modal.Header>
      <Modal.Body>
        <Form onSubmit={handleSubmit}>
          <Form.Group className="mb-3">
            <Form.Label>Date From</Form.Label>
            <Form.Control
              type="date"
              value={dateFrom}
              onChange={(e) => setDateFrom(e.target.value)}
              required
            />
          </Form.Group>
          <Form.Group className="mb-3">
            <Form.Label>Date To</Form.Label>
            <Form.Control
              type="date"
              value={dateTo}
              onChange={(e) => setDateTo(e.target.value)}
              required
            />
          </Form.Group>

          <div className="d-flex justify-content-end">
            <Button variant="secondary" onClick={onClose} className="mr-2">
              Close
            </Button>
            <Button variant="primary" type="submit">
              Import
            </Button>
          </div>
        </Form>
      </Modal.Body>
    </Modal>
  );
}
