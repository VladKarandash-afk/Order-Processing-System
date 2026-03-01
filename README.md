# High-Concurrency Order Processing System

## Overview
This project is a robust, database-driven order processing engine designed to handle concurrent transactions in an e-commerce environment. The core focus of this system is maintaining strict **data integrity** and preventing **race conditions** when multiple users attempt to purchase the same limited-stock items simultaneously.

While the frontend is implemented in PHP, the heavy lifting and business logic are entirely encapsulated within the database layer using advanced **PostgreSQL** features.

## Technical Highlights
* **Concurrency Control:** Utilizes PostgreSQL's `FOR UPDATE SKIP LOCKED` mechanism to handle simultaneous inventory requests efficiently without blocking entire tables or causing deadlocks.
* **Stored Procedures:** Business logic (order placement, inventory reservation, and status updates) is implemented using `PL/pgSQL` procedures, minimizing multiple round-trips between the application and the database.
* **ACID Compliance:** Ensures that complex multi-step transactions (e.g., checking stock, reserving an item, creating an order record) either complete entirely or roll back safely.
* **Relational Design:** Normalized database schema preventing data anomalies.

## Database Architecture
The system revolves around several key entities:
* `zamowienie` (Orders): Tracks the lifecycle of a user's order.
* `pozycja_zamowienia` (Order Items): Links specific games/items to an order.
* `kopia_gry` (Inventory Copies): Represents physical copies of items. Statuses transition dynamically from `dostepna` (available) to `zarezerwowana` (reserved).

### The "Skip Locked" Mechanism
The critical part of the system is the `zloz_zamowienie` procedure. When an order is placed, the system dynamically searches for available copies. Using `LIMIT N FOR UPDATE SKIP LOCKED`, it skips rows already locked by other concurrent transactions, securing the exact required amount of stock instantly or failing gracefully if the stock is depleted. 

## Tech Stack
* **Database:** PostgreSQL, PL/pgSQL
* **Frontend/Interface:** PHP, HTML
* **Environment:** Linux/Bash

## Setup & Installation
1. Clone this repository.
2. Initialize the PostgreSQL database by running the provided SQL scripts to create tables and stored procedures:
   ```bash
   psql -U your_user -d your_database -f schema.sql
3. Configure the db.php file with your PostgreSQL credentials.
4. Run the PHP server to access the interface:
   ```bash
   php -S localhost:8000
