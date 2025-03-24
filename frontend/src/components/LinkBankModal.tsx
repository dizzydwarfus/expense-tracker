"use client";

import React, { useState } from "react";
import { Modal, Button, Form } from "react-bootstrap";

interface LinkBankModalProps {
  show: boolean;
  onClose: () => void;
}

/**
 * A modal that gathers the parameters for creating an end user agreement and linking
 * a bank account: institution_id, max_historical_days, access_valid_for_days, access_scope, etc.
 */
export default function LinkBankModal({ show, onClose }: LinkBankModalProps) {
  const [institutionId, setInstitutionId] = useState("");
  const [maxHistoricalDays, setMaxHistoricalDays] = useState("");
  const [accessValidForDays, setAccessValidForDays] = useState("");
  const [balances, setBalances] = useState(true);
  const [transactions, setTransactions] = useState(true);
  const [details, setDetails] = useState(true);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    // Build the 'access_scope' array based on checkboxes
    const accessScope = [];
    if (balances) accessScope.push("balances");
    if (transactions) accessScope.push("transactions");
    if (details) accessScope.push("details");

    const body = {
      institution_id: institutionId,
      max_historical_days: maxHistoricalDays,
      access_valid_for_days: accessValidForDays,
      access_scope: accessScope,
    };

    try {
      const resp = await fetch("http://localhost:8000/banks/link_bank", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
        credentials: "include", // include session cookie
      });
      if (!resp.ok) {
        const errorData = await resp.json();
        console.error("Failed to link bank account:", errorData);
        return;
      }
      const data = await resp.json();
      console.log(data);
      // if (data.link) {
      //   window.location.href = data.link;
      // }

      onClose();
    } catch (err) {
      console.error("Error linking bank account:", err);
    }
  };

  return (
    <Modal show={show} onHide={onClose} centered>
      <Modal.Header closeButton>
        <Modal.Title>Link Bank Account</Modal.Title>
      </Modal.Header>
      <Modal.Body>
        <Form onSubmit={handleSubmit}>
          {/* institution_id */}
          <Form.Group className="mb-3">
            <Form.Label>Institution ID</Form.Label>
            <Form.Control
              type="text"
              value={institutionId}
              onChange={(e) => setInstitutionId(e.target.value)}
              required
            />
            <Form.Text>
              E.g., <strong>ING_INGBNL2A</strong> for ING in the Netherlands
            </Form.Text>
          </Form.Group>

          {/* max_historical_days */}
          <Form.Group className="mb-3">
            <Form.Label>Max Historical Days</Form.Label>
            <Form.Control
              type="number"
              value={maxHistoricalDays}
              onChange={(e) => setMaxHistoricalDays(e.target.value)}
              required
            />
            <Form.Text>
              How many days of transaction history do you want? (max. 540 days)
            </Form.Text>
          </Form.Group>

          {/* access_valid_for_days */}
          <Form.Group className="mb-3">
            <Form.Label>Access Valid For (Days)</Form.Label>
            <Form.Control
              type="number"
              value={accessValidForDays}
              onChange={(e) => setAccessValidForDays(e.target.value)}
              required
            />
            <Form.Text>
              After how many days does the end-user agreement expire? (max. 180
              days)
            </Form.Text>
          </Form.Group>

          {/* access_scope checkboxes */}
          <Form.Group className="mb-3">
            <Form.Label>Access Scope</Form.Label>
            <div>
              <Form.Check
                type="checkbox"
                id="balances"
                label="balances"
                checked={balances}
                onChange={() => setBalances((prev) => !prev)}
              />
              <Form.Check
                type="checkbox"
                id="transactions"
                label="transactions"
                checked={transactions}
                onChange={() => setTransactions((prev) => !prev)}
              />
              <Form.Check
                type="checkbox"
                id="details"
                label="details"
                checked={details}
                onChange={() => setDetails((prev) => !prev)}
              />
            </div>
          </Form.Group>

          <div className="d-flex justify-content-end">
            <Button variant="secondary" onClick={onClose} className="mr-2">
              Close
            </Button>
            <Button variant="primary" type="submit">
              Link Account
            </Button>
          </div>
        </Form>
      </Modal.Body>
    </Modal>
  );
}
