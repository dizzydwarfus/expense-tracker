export interface TransactionAmount {
  amount: number;
  currency: string;
}

export interface DebtorAccount {
  iban: string;
}

export interface CreditorAccount {
  iban: string;
}

export interface Transaction {
  id?: string; // alias of _id
  transactionId?: string;
  endToEndId?: string;
  bookingDate?: string; // "YYYY-MM-DD" or undefined if pending
  transactionAmount: TransactionAmount; // { amount: number, currency: string }
  debtorName?: string;
  debtorAccount?: DebtorAccount;
  creditorName?: string;
  creditorAccount?: CreditorAccount;
  remittanceInformationUnstructured?: string;
  proprietaryBankTransactionCode?: string;
  internalTransactionId?: string;
  transactionType?: string; // "expense" or "income"
  category?: string;
  sub_category?: string;
}
