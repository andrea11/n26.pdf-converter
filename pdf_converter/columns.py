import enum


class ExportableColumnHeaders(enum.Enum):
    PAYEE = "Payee"
    DATE = "Date"
    AMOUNT = "Amount (EUR)"
    TRANSACTION_TYPE = "Transaction type"
    CATEGORY = "Category"
    IBAN = "IBAN"
    BIC = "BIC"
    NOTE = "Note"
    ORIGINAL_AMOUNT = "Amount (Foreign Currency)"
    ORIGINAL_CURRENCY = "Type Foreign Currency"
    FX_RATE = "Exchange Rate"

    def __str__(self):
        return self.value


class InternalColumnHeaders(enum.Enum):
    ACCOUNT_NAME_OR_ORIGINAL_AMOUNT = "Account number or Amount (Foreign Currency)"
