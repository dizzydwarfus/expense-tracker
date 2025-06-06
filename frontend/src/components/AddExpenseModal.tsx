/**
 * ADD_EXPENSE_MODAL.TSX
 *
 * This component creates a new transaction, but now it uses a **dependent dropdown** for
 * Category and Sub-category. We fetch all categories from your Mongo “Categories” collection
 * (where each doc has { _id, name, subCategories: [ ... ] }) and store them in local state.
 * When the user selects a category, we populate subCategory dropdown from that category’s subCategories array.
 */

"use client";

import React, { useEffect, useState } from "react";
import { Modal, Button, Form } from "react-bootstrap";
import { Transaction } from "@/components/interfaces/transaction";
import { CategoryModel } from "@/components/interfaces/category";

interface AddExpenseModalProps {
  show: boolean;
  onClose: () => void;
}

export default function AddExpenseModal({
  show,
  onClose,
}: AddExpenseModalProps) {
  // Basic fields
  const [transactionId, setTransactionId] = useState("");
  const [endToEndId, setEndToEndId] = useState("");
  const [bookingDate, setBookingDate] = useState("");
  const [amount, setAmount] = useState("");
  const [currency, setCurrency] = useState("EUR");
  const [debtorName, setDebtorName] = useState("");
  const [debtorIban, setDebtorIban] = useState("");
  const [creditorName, setCreditorName] = useState("");
  const [creditorIban, setCreditorIban] = useState("");
  const [remittanceInfo, setRemittanceInfo] = useState("");
  const [bankTxCode, setBankTxCode] = useState("");
  const [internalTxId, setInternalTxId] = useState("");
  const [transactionType, setTransactionType] = useState<"expense" | "income">(
    "expense"
  );

  // Dependent dropdown for category & subcategory
  const [categories, setCategories] = useState<CategoryModel[]>([]);
  const [selectedCategory, setSelectedCategory] = useState("");
  const [selectedSubCategory, setSelectedSubCategory] = useState("");
  const [subCategoryOptions, setSubCategoryOptions] = useState<string[]>([]);

  // Fetch categories from the server once
  useEffect(() => {
    (async () => {
      try {
        const resp = await fetch("http://localhost:8000/all_categories");
        // Suppose you have an endpoint that returns an array of categories
        // e.g. [ { _id: "Entertainment", name: "Entertainment", subCategories: ["Games", "Movies"] }, ... ]
        if (!resp.ok) {
          console.error("Failed to fetch categories");
          return;
        }
        const data: CategoryModel[] = await resp.json();
        setCategories(data || []);
      } catch (err) {
        console.error("Error fetching categories:", err);
      }
    })();
  }, []);

  // Whenever the user picks a new category, update the subCategory array
  useEffect(() => {
    const foundCat = categories.find((cat) => cat._id === selectedCategory);
    if (foundCat) {
      setSubCategoryOptions(foundCat.subCategories);
    } else {
      setSubCategoryOptions([]);
    }
    // Reset sub-category if category changes
    setSelectedSubCategory("");
  }, [selectedCategory, categories]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    // Build the transaction doc
    const transactionDoc: Partial<Transaction> = {
      transactionId: transactionId || undefined,
      endToEndId: endToEndId || undefined,
      bookingDate: bookingDate || undefined,
      transactionAmount: {
        amount: parseFloat(amount || "0"),
        currency: currency || "EUR",
      },
      debtorName: debtorName || undefined,
      debtorAccount: debtorIban ? { iban: debtorIban } : undefined,
      creditorName: creditorName || undefined,
      creditorAccount: creditorIban ? { iban: creditorIban } : undefined,
      remittanceInformationUnstructured: remittanceInfo || undefined,
      proprietaryBankTransactionCode: bankTxCode || undefined,
      internalTransactionId: internalTxId || undefined,
      transactionType,
      category: selectedCategory || undefined,
      sub_category: selectedSubCategory || undefined,
    };

    try {
      const resp = await fetch("http://localhost:8000/add_expense", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(transactionDoc),
        credentials: "include",
      });
      if (!resp.ok) {
        const data = await resp.json();
        console.error("Failed to add transaction", data);
        return;
      }
      onClose();
      window.location.reload();
    } catch (err) {
      console.error("Error adding transaction:", err);
    }
  };

  return (
    <Modal show={show} onHide={onClose} centered>
      <Modal.Header closeButton>
        <Modal.Title>Add Transaction</Modal.Title>
      </Modal.Header>
      <Modal.Body>
        <Form onSubmit={handleSubmit}>
          {/* Basic text fields */}
          <Form.Group className="mb-3">
            <Form.Label>transactionId</Form.Label>
            <Form.Control
              type="text"
              value={transactionId}
              onChange={(e) => setTransactionId(e.target.value)}
            />
          </Form.Group>

          <Form.Group className="mb-3">
            <Form.Label>endToEndId</Form.Label>
            <Form.Control
              type="text"
              value={endToEndId}
              onChange={(e) => setEndToEndId(e.target.value)}
            />
          </Form.Group>

          <Form.Group className="mb-3">
            <Form.Label>bookingDate</Form.Label>
            <Form.Control
              type="date"
              value={bookingDate}
              onChange={(e) => setBookingDate(e.target.value)}
            />
          </Form.Group>

          {/* TransactionAmount fields */}
          <Form.Group className="mb-3">
            <Form.Label>Amount</Form.Label>
            <Form.Control
              type="number"
              step="0.01"
              value={amount}
              onChange={(e) => setAmount(e.target.value)}
            />
          </Form.Group>
          <Form.Group className="mb-3">
            <Form.Label>Currency</Form.Label>
            <Form.Control
              type="text"
              value={currency}
              onChange={(e) => setCurrency(e.target.value)}
            />
          </Form.Group>

          {/* Debtor */}
          <Form.Group className="mb-3">
            <Form.Label>Debtor Name</Form.Label>
            <Form.Control
              type="text"
              value={debtorName}
              onChange={(e) => setDebtorName(e.target.value)}
            />
          </Form.Group>
          <Form.Group className="mb-3">
            <Form.Label>Debtor IBAN</Form.Label>
            <Form.Control
              type="text"
              value={debtorIban}
              onChange={(e) => setDebtorIban(e.target.value)}
            />
          </Form.Group>

          {/* Creditor */}
          <Form.Group className="mb-3">
            <Form.Label>Creditor Name</Form.Label>
            <Form.Control
              type="text"
              value={creditorName}
              onChange={(e) => setCreditorName(e.target.value)}
            />
          </Form.Group>
          <Form.Group className="mb-3">
            <Form.Label>Creditor IBAN</Form.Label>
            <Form.Control
              type="text"
              value={creditorIban}
              onChange={(e) => setCreditorIban(e.target.value)}
            />
          </Form.Group>

          {/* Other optional fields */}
          <Form.Group className="mb-3">
            <Form.Label>Remittance Info (Unstructured)</Form.Label>
            <Form.Control
              type="text"
              value={remittanceInfo}
              onChange={(e) => setRemittanceInfo(e.target.value)}
            />
          </Form.Group>

          <Form.Group className="mb-3">
            <Form.Label>Proprietary Bank Tx Code</Form.Label>
            <Form.Control
              type="text"
              value={bankTxCode}
              onChange={(e) => setBankTxCode(e.target.value)}
            />
          </Form.Group>

          <Form.Group className="mb-3">
            <Form.Label>Internal Transaction ID</Form.Label>
            <Form.Control
              type="text"
              value={internalTxId}
              onChange={(e) => setInternalTxId(e.target.value)}
            />
          </Form.Group>

          <Form.Group className="mb-3">
            <Form.Label>Transaction Type (expense or income)</Form.Label>
            <Form.Select
              value={transactionType}
              onChange={(e) =>
                setTransactionType(e.target.value as "expense" | "income")
              }
            >
              <option value="expense">expense</option>
              <option value="income">income</option>
            </Form.Select>
          </Form.Group>

          {/* Category / Sub-category dropdowns */}
          <Form.Group className="mb-3">
            <Form.Label>Category</Form.Label>
            <Form.Select
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
            >
              <option value="">-- Select Category --</option>
              {categories.map((cat) => (
                <option key={cat._id} value={cat._id}>
                  {cat._id}
                </option>
              ))}
            </Form.Select>
          </Form.Group>

          <Form.Group className="mb-3">
            <Form.Label>Sub-category</Form.Label>
            <Form.Select
              value={selectedSubCategory}
              onChange={(e) => setSelectedSubCategory(e.target.value)}
            >
              <option value="">-- Select Sub-category --</option>
              {subCategoryOptions.map((scat) => (
                <option key={scat} value={scat}>
                  {scat}
                </option>
              ))}
            </Form.Select>
          </Form.Group>

          <div className="d-flex justify-content-end">
            <Button variant="secondary" onClick={onClose} className="mr-2">
              Close
            </Button>
            <Button variant="primary" type="submit">
              Add Transaction
            </Button>
          </div>
        </Form>
      </Modal.Body>
    </Modal>
  );
}
