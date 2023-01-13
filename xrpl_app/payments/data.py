from pydantic import BaseModel


class TransactionMeta(BaseModel):
    TransactionResult: str


class Amount(BaseModel):
    issuer: str
    currency: str
    value: str


class TransactionData(BaseModel):
    Account: str
    Amount: str | Amount
    Destination: str
    DestinationTag: int | None
    Fee: str
    TransactionType: str
    hash: str
    ledger_index: int


class XRPTransaction(BaseModel):
    meta: TransactionMeta
    tx: TransactionData
    validated: bool
    _transaction_success: str = "tesSUCCESS"
    _payment_type: str = "Payment"

    @property
    def is_successful(self) -> bool:
        return self.meta.TransactionResult == self._transaction_success

    @property
    def is_validated(self) -> bool:
        return self.validated

    @property
    def is_it_payment(self) -> bool:
        return self.tx.TransactionType == self._payment_type

    @property
    def hash(self) -> str:
        return self.tx.hash

    @property
    def source(self) -> str:
        return self.tx.Account

    @property
    def destination(self) -> str:
        return self.tx.Destination

    @property
    def destination_tag(self) -> int | None:
        return self.tx.DestinationTag

    @property
    def fee(self) -> str:
        return self.tx.Fee

    @property
    def amount(self) -> str | Amount:
        return self.tx.Amount

    @property
    def ledger_index(self) -> int:
        return self.tx.ledger_index

    @property
    def amount_value(self) -> str:
        if isinstance(self.tx.Amount, Amount):
            return self.tx.Amount.value
        else:
            return self.tx.Amount
