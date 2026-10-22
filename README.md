# Lumme: Privacy-First Community Safety & Emergency Response App

**Lumme** is a lightweight, mobile-first safety and emergency response web application designed for South African environments. Built to combat gender-based violence (GBV) and community security threats, Lumme bridges the gap between fast emergency dispatches and strict data privacy.

## Key Features
* **Instant SOS Panic Trigger:** One-touch emergency dispatch that instantly logs GPS coordinates (`latitude`, `longitude`) and timestamps.
* **Database Concurrency Resilience:** Powered by SQLite with Write-Ahead Logging (WAL) and `busy_timeout` configurations to handle simultaneous emergency requests seamlessly without locking errors.
* **POPIA Section 24 Compliance:** Features built-in data privacy controls and a secure user-initiated erasure endpoint (`/api/user/delete-data`) that permanently purges all personal identifiers and alert logs upon request.
* **Low-Data & Mobile Optimized:** Lightweight Flask backend paired with responsive dark-mode styling tailored for budget mobile devices and low-connectivity environments.

## Tech Stack
* **Backend:** Python, Flask, SQLite
* **Frontend:** HTML5, CSS3, JavaScript
* **Security & Compliance:** CSP headers, parameterized SQL queries, regex input sanitization, POPIA right-to-erasure workflows
.
