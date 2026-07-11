# API Contracts - Full Details

## **Endpoints Principales**

## Endpoint 1: POST /auth/oauth/token
**Request JSON**
```json
{
  "grant_type": "client_credentials",
  "client_id": "psip-app-001-123456",
  "client_secret": "sk_live_8f3k9x2m7p4q9w2e5r7t8y9u0i",
  "scope": "payments:transfer payments:collect accounts:info consents:manage",
  "idempotencyKey": "auth-20260607123456789"
}
```
**Response Success**
```json
{
  "access_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "Bearer",
  "expires_in": 3600,
  "scope": "payments:transfer payments:collect accounts:info consents:manage",
  "issued_at": "2026-06-07T15:30:00Z"
}
```
**Response Error**
```json
{
  "errorCode": "AUTH-001",
  "errorMessage": "Client authentication failed",
  "details": {"reason": "Invalid client_id or client_secret"}
}
```
---
## Endpoint 2: POST /consents
**Request JSON**
```json
{
  "consentId": "CONS-uuid-123e4567-e89b-12d3-a456-426614174000",
  "tappId": "usuario@tapp",
  "debtorAccount": {"alias": "usuario123", "bankCode": "009"},
  "creditor": {"name": "Tienda XYZ", "alias": "tienda@merchant.tapp"},
  "amount": {"value": 100.50, "currency": "PEN"},
  "purpose": "CPTR",
  "validUntil": "2026-06-30T23:59:59Z",
  "scopes": ["accounts:balance", "accounts:transactions", "payments:transfer"],
  "idempotencyKey": "consent-20260607123456789",
  "transRemarks": "Autorización para agregación de cuentas y pagos"
}
```
**Response Success**
```json
{
  "consentId": "CONS-uuid-123e4567-e89b-12d3-a456-426614174000",
  "status": "AWAITING_AUTHORISATION",
  "authUrl": "https://pc-bank.example.com/authorize?consentId=CONS-uuid-...&redirect_uri=...",
  "createdAt": "2026-06-07T15:30:00Z",
  "expiresAt": "2026-06-30T23:59:59Z"
}
```
**Response Error**
```json
{
  "errorCode": "CONS-003",
  "errorMessage": "Invalid Tapp ID",
  "status": "RJCT"
}
```
---
## Endpoint 3: POST /payments
**Request JSON**
```json
{
  "consentId": "CONS-uuid-123e4567-e89b-12d3-a456-426614174000",
  "sourceTappId": "usuario123@tapp",
  "destinationTappId": "amigo456@tapp",
  "amount": {"value": 85.50, "currency": "PEN"},
  "transRemarks": "Pago de almuerzo compartido",
  "transType": "PAY",
  "transRefId": "REF-20260607124567",
  "addInfo1": "Categoría: Comida",
  "addInfo2": "",
  "addInfo3": "",
  "addInfo4": "",
  "addInfo5": "",
  "addInfo6": "",
  "addInfo7": "",
  "addInfo8": "",
  "addInfo9": "",
  "addInfo10": "",
  "idempotencyKey": "pay-push-20260607124567890"
}
```
**Response Success**
```json
{
  "transId": "TAPP-PAY-9876543210ABCDEF12345",
  "transRRN": "701524566521",
  "transAmount": 85.50,
  "transAuthDateTime": "2026-06-07T12:45:22Z",
  "transStatus": "S",
  "transMessage": "Payment Successful",
  "sourceTappId": "usuario123@tapp",
  "destinationTappId": "amigo456@tapp",
  "respCode": "00",
  "addInfo1": "Categoría: Comida"
}
```
**Response Error**
```json
{
  "errorCode": "PAY-402",
  "errorMessage": "Insufficient balance or invalid consent",
  "details": {"reason": "Consent does not include payments:transfer scope"}
}
```
---
## Endpoint 4: POST /accounts (or GET /accounts/{consentId})
**Request JSON (POST)**
```json
{
  "consentId": "CONS-uuid-123e4567-e89b-12d3-a456-426614174000",
  "tappId": "usuario123@tapp",
  "accountAlias": "usuario123",
  "bankCode": "009",
  "queryType": "balance", // "balance" | "transactions" | "both"
  "transactionFrom": "2026-05-01T00:00:00Z",
  "transactionTo": "2026-06-07T23:59:59Z",
  "page": 1,
  "limit": 50,
  "idempotencyKey": "acct-20260607123456789"
}
```
**Response Success (both)**
```json
{
  "consentId": "CONS-uuid-123e4567-e89b-12d3-a456-426614174000",
  "accountAlias": "usuario123",
  "bankCode": "009",
  "accountStatus": "ACTIVE",
  "balance": {"value": 2450.75, "currency": "PEN", "availableBalance": 2380.50},
  "lastUpdated": "2026-06-07T15:45:22Z",
  "transactions": [
    {
      "transId": "TAPP-TRAN-987654321",
      "transRRN": "701524566521",
      "amount": -150.00,
      "currency": "PEN",
      "transDate": "2026-06-06T10:23:15Z",
      "transType": "DEBIT",
      "description": "Pago en Tienda XYZ",
      "status": "S"
    }
  ],
  "page": 1,
  "totalPages": 5,
  "totalRecords": 234
}
```
**Response Error**
```json
{
  "errorCode": "ACCT-403",
  "errorMessage": "Consent expired or insufficient permissions",
  "status": "RJCT",
  "details": {"consentId": "CONS-uuid-...", "reason": "Consent does not include accounts:balance scope"}
}
```
---
## Endpoint 5: POST /aliases/validate
**Request JSON**
```json
{
  "refNo": "12837",
  "tappId": "dynamic-part123@tapp",
  "transRemarks": "Validación pre-pago de prueba",
  "transAmount": 100.00,
  "transId": "TAPP527498730B1B1BC3E053142433823107",
  "transRRN": "717215233641",
  "payeeTappId": "merchant-tiendaxyz@tapp",
  "source": "PSIP-APP",
  "pgMerchantId": "HSB000000000001",
  "addInfo1": "Referencia interna 456",
  "addInfo2": "",
  "addInfo3": "",
  "addInfo4": "",
  "addInfo5": "",
  "addInfo6": "",
  "addInfo7": "",
  "addInfo8": "",
  "addInfo9": "",
  "addInfo10": "",
  "idempotencyKey": "val-20260607123456789"
}
```
**Response Success**
```json
{
  "transStatus": "S",
  "transMessage": "Success",
  "refNo": "12837",
  "transRRN": "717215233641",
  "accountDetails": {"tappId": "dynamic-part123@tapp", "accountStatus": "Success", "name": "Juan Pérez López"},
  "pgMerchantId": "HSB000000000001",
  "addInfo1": "Referencia interna 456"
}
```
**Response Error**
```json
{
  "transStatus": "F",
  "transMessage": "Tapp ID no encontrado o inactivo",
  "refNo": "12837",
  "transRRN": "",
  "accountDetails": {},
  "errorCode": "ALIAS-404"
}
```
---
## Endpoint 6: POST /collects
**Request JSON**
```json
{
  "pgMerchantId": "HSB000000000001",
  "meOrderNo": "ORD-20260607123456",
  "payerTappId": "usuario123@tapp",
  "payerName": "Juan Pérez López",
  "transAmount": 50.00,
  "transRemarks": "Pago de producto electrónico",
  "expiryMinutes": 1110,
  "transType": "COLLECT",
  "addInfo1": "SKU-ABC123",
  "addInfo2": "",
  "addInfo3": "",
  "addInfo4": "",
  "addInfo5": "",
  "addInfo6": "",
  "addInfo7": "",
  "addInfo8": "",
  "addInfo9": "",
  "addInfo10": "",
  "idempotencyKey": "collect-20260607123456789"
}
```
**Response Success**
```json
{
  "meOrderNo": "ORD-20260607123456",
  "transId": "TAPP9DA3B8AC7A7454290D9D956D2C3D17E",
  "transRRN": "707520002012",
  "transAmount": 50.00,
  "transAuthDateTime": "2026-06-07T15:35:22Z",
  "collStatus": "I",
  "collStatusDesc": "Transaction Initiated",
  "payerTappId": "usuario123@tapp",
  "payeeTappId": "merchant-tiendaxyz@tapp",
  "addInfo1": "SKU-ABC123"
}
```
**Response Error**
```json
{
  "meOrderNo": "ORD-20260607123456",
  "collStatus": "F",
  "collStatusDesc": "Invalid Payer Tapp ID",
  "errorCode": "COLL-001"
}
```
---
## Endpoint 7: POST /payments/{transId}/confirm
**Request JSON**
```json
{
  "refNo": "2394829",
  "transId": "TAPP4521EDFDF113434131442134D34D34FF",
  "transRRN": "701245124574",
  "transAmount": 100.00,
  "transAuthDateTime": "2026-06-07T15:45:22Z",
  "respCode": "00",
  "transStatus": "S",
  "transMessage": "Success",
  "transType": "PAY",
  "payerTappId": "usuario123@tapp",
  "payeeTappId": "merchant-tiendaxyz@tapp",
  "transRemarks": "Pago de producto electrónico",
  "transRefId": "1495085619883943",
  "addInfo4": "CREDIT",
  "pgMerchantId": "HSB000000000001",
  "orderId": "ORD-20260607123456"
}
```
**Response Success (Merchant)**
```json
{
  "refNo": "2394829",
  "transRRN": "701245124574",
  "confStatus": "S",
  "confMessage": "SUCCESS",
  "confId": "CONF-98765432109876543210",
  "pgMerchantId": "HSB000000000001",
  "addInfo1": ""
}
```
**Response Error (Merchant)**
```json
{
  "confStatus": "F",
  "confMessage": "Error en registro contable",
  "errorCode": "CONF-500"
}
```
---

## **Endpoints Opcionales/Administrativos**

## Endpoint 8: POST /payments/status
**Request JSON**
```json
{
  "pgMerchantId": "HSB000000000001",
  "meRefNo": "41542145156",
  "transRRN": "701524566521",
  "meOrderNo": "ORD-20260607123456"
}
```
**Response Success**
```json
{
  "meOrderNo": "ORD-20260607123456",
  "transAmount": 100.00,
  "transAuthDateTime": "2026-06-07T15:45:22Z",
  "transStatus": "S",
  "transMessage": "Payment Successful",
  "respCode": "00",
  "transRRN": "701524566521",
  "transId": "TAPP89DA3B8AC7A7454290D9D956D2C3D17E",
  "payerTappId": "usuario123@tapp",
  "payeeTappId": "merchant-tiendaxyz@tapp",
  "transApprNo": "451254",
  "addInfo1": "SKU-ABC123"
}
```
**Response Error**
```json
{
  "transStatus": "E",
  "transMessage": "Transaction not found",
  "errorCode": "STATUS-404"
}
```
---
## Endpoint 9: POST /refunds
**Request JSON**
```json
{
  "pgMerchantId": "HSB000000000001",
  "newMeOrderNo": "REF-20260607130000",
  "orgTransId": "TAPP4521EDFDF113434131442134D34D34FF",
  "orgTransRRN": "701245124574",
  "transRemarks": "Reembolso por producto defectuoso",
  "refundAmount": 50.00,
  "orgMeOrderNo": "ORD-20260607123456",
  "addInfo1": "Motivo: DEV-001",
  "addInfo2": "",
  "addInfo3": "",
  "addInfo4": "",
  "addInfo5": "",
  "addInfo6": "",
  "addInfo7": "",
  "addInfo8": "",
  "addInfo9": "",
  "addInfo10": "",
  "idempotencyKey": "refund-20260607130000123"
}
```
**Response Success**
```json
{
  "newMeOrderNo": "REF-20260607130000",
  "orgTransId": "TAPP4521EDFDF113434131442134D34D34FF",
  "newTransId": "TAPP-REF-9876543210ABCDEF",
  "refundAmount": 50.00,
  "transAuthDateTime": "2026-06-07T13:05:45Z",
  "respCode": "00",
  "refundStatus": "S",
  "refundMessage": "Success",
  "addInfo1": "Motivo: DEV-001"
}
```
**Response Error**
```json
{
  "refundStatus": "F",
  "refundMessage": "Original transaction not refundable",
  "errorCode": "REF-003"
}
```
---
## Endpoint 10: POST /participants/register
**Request JSON**
```json
{
  "participantId": "PSIP-MIFINTECH-001",
  "legalName": "Mi Fintech SAC",
  "taxId": "20601234567",
  "contactEmail": "tech@mitfintech.pe",
  "contactPhone": "+51987654321",
  "redirectUris": ["https://mitfintech.pe/callback", "https://app.mitfintech.pe/auth"],
  "publicKey": "-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA...\n-----END PUBLIC KEY-----",
  "allowedScopes": ["payments:transfer", "payments:collect", "accounts:balance"],
  "webhookUrl": "https://mitfintech.pe/webhooks/tapp",
  "idempotencyKey": "onboard-20260607123456789"
}
```
**Response Success**
```json
{
  "participantId": "PSIP-MIFINTECH-001",
  "status": "REGISTERED",
  "createdAt": "2026-06-07T15:40:00Z",
  "webhookUrl": "https://mitfintech.pe/webhooks/tapp"
}
```
**Response Error**
```json
{
  "errorCode": "ONBOARD-001",
  "errorMessage": "Invalid redirect URI or missing required fields",
  "status": "RJCT"
}
```
---

*All endpoints require the standard headers:* `Authorization: Bearer <JWT-access-token>`, `X-Idempotency-Key`, `Content-Type: application/json`, `Accept: application/json`, `X-Tapp-Version: 1.0`.

*Standard error format:*
```json
{
  "errorCode": "RJCT",
  "errorMessage": "Invalid Tapp ID or insufficient permissions",
  "details": {"field": "tappId", "reason": "Not registered"}
}
```
