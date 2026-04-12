# Available Domains

## Overview

| Domain | Object Types | Links | Actions |
|--------|-------------|-------|---------|
| supply_chain | 7 | 7 | 3 |
| finance | 6 | 5 | 2 |
| healthcare | 7 | 8 | 2 |
| ecommerce | 6 | 6 | 3 |

## Object Types by Domain

### supply_chain

Supplier, ScProduct, Warehouse, PurchaseOrder, Shipment, Contract, Inventory

### finance

FiCustomer, Account, Transaction, FiProduct, CreditCard, Loan

### healthcare

Patient, Provider, Diagnosis, Medication, Encounter, LabResult, InsuranceClaim

### ecommerce

EcomUser, Merchant, EcomProduct, EcomOrder, Review, Coupon

## Interface Types

- **Auditable** — `created_at: timestamp` — implemented by all 26 object types
- **GeoLocated** — `latitude, longitude, address` — implemented by Warehouse, Provider, Merchant
