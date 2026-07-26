# 🛡️ Automated KYC & Document Verification System

An end-to-end, full-stack AI platform that automates manual data entry from identity cards, application forms, and handwritten documents using Google Gemini Vision AI.

## 📌 Features

- **Automated Multimodal OCR:** Uses Gemini Vision to read and extract entities (Name, DOB, ID Number, Address, Document Type) from uploaded ID photos or document scans.
- **Strict JSON Schema Formatting:** Forces structured data extraction using Gemini's response schema enforcement.
- **Verification Engine:** Flags incomplete records missing essential fields.
- **Local Persistence:** Stores verified records in a lightweight SQLite database (`kyc.db`).
- **Interactive UI Dashboard:** Upload documents, inspect real-time JSON outputs, and view logged database records via Streamlit.

---

## 🛠️ Tech Stack

- **Python:** Core application logic.
- **Flask (Backend API):** Routes uploads, interfaces with Gemini AI, and manages SQLite transactions.
- **Streamlit (Frontend):** Interactive web user interface.
- **SQLite (Database):** Embedded relational database for audit logging.
- **Google Gemini API (`google-genai` SDK):** Vision AI engine for document parsing.

---

## 🚀 Getting Started

### Prerequisites

- Python 3.10+ installed
- A Google Gemini API Key (Get one free at [Google AI Studio](https://aistudio.google.com))

### Installation & Setup

1. **Clone the Repository:**
   ```bash
   git clone [https://github.com/Startriumph/Automated_KYC_Verification.git](https://github.com/Startriumph/Automated_KYC_Verification.git)
   cd Automated_KYC_Verification