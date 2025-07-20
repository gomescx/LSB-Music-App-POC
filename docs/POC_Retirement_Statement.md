# 📘 POC Retirement and Transition to MVP

## Executive Summary

The current Streamlit-based POC for the **LSB Music App** has successfully delivered its initial objective: validate that a lightweight local app can streamline the process of creating Biodanza sessions using the LSB catalogue. The proof of concept allowed rapid prototyping, reduced manual effort in playlist/session creation, and demonstrated value in real-life scenarios with a single facilitator.

However, the development of better User Interface is proving expensive. Some recent solutions such as checking with the user if they really want to abandon their changes, are not simply implemented with Strieamlit. As we struggle to address some bugs, and implement transition to a multi-user MVP with enhanced searchability, cross-referencing, the limitations of the POC’s architecture have become apparent. Further investment in the current Streamlit-based frontend would yield diminishing returns and lead to increasing technical debt.

Therefore, we made a strategic decision to **retire the POC and initiate MVP development on a modern full-stack architecture based on FastAPI (backend) and React (frontend)**. This will ensure flexibility, performance, and long-term maintainability.

---

## Technical Rationale and Approach

### 🔧 What Stays

We are **not starting from scratch**. The POC has produced valuable code and structural knowledge that will directly inform the MVP, particularly:

- **Data model design** (as seen in the SQLite schema and the `queries.py` logic)
- **Business rules** around music/exercise relationships and session logic
- **Prototype UI interactions** that guided user needs

These insights will be **selectively refactored** and transferred into the new stack.

### ✂️ What Gets Rewritten

- The Streamlit-based UI components will be **entirely rebuilt in React** to allow modern, flexible interaction patterns (e.g., filtering, sorting, real-time previews).
- Session management, currently bound to Streamlit session state, will be decoupled and implemented in FastAPI as REST endpoints.
- The current flat logic structure will be **modularized** using service layers and Pydantic models for cleaner backend boundaries.

### ⚙️ Why FastAPI + React?

| Challenge                       | Streamlit Limitation              | FastAPI + React Solution                |
|-------------------------------|----------------------------------|-----------------------------------------|
| Cross-filtering across entities | No native relational state        | React + REST enables deep filtering UI  |
| Responsive multi-tab UI         | Awkward state control             | React components with scoped states     |
| Multi-user sharing and auth     | Not supported                     | FastAPI integrates easily with JWT/OAuth |
| Custom export paths / handling  | Needs workarounds                 | Full filesystem and API control         |
| Maintainable UX code            | Large monolithic files            | React modularity by design              |

### 🚧 Transition Plan

- The POC will remain archived in its current Git repo and may be referred to during MVP development.
- A new MVP Epic and corresponding Git repository will be initialized under a clean architecture from the first vertical slice.
- Where applicable, utility scripts (e.g., for data loading, export) will be extracted and reused or re-implemented as microservices or API endpoints.

---

## Status

📦 POC Final Commit: `feat: Export Session to Word & Playlist`  
📅 Retired: **May 2025**  
🚀 MVP Start: **July 2025**, under separate Epic and Repo

---

## Contact

For questions regarding the MVP transition, contact the current Product Owner and Delivery Manager:  
**Claudio Gomes** — itadmin@biocentrica.com.au

