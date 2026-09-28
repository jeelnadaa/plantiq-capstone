# PlantIQ — Low Level Design & Implementation Document Directory
## UE23CS441A Capstone Project Phase – 3

This directory contains the complete, modularized Low-Level Design (LLD) documentation for the **PlantIQ** platform, structured in strict conformance with the PES University Capstone Phase 3 template (`UE23CS441A _LOW LEVEL DESIGN & IMPLEMENTATION DOCUMENT.docx`).

---

### Master Document Index Table

| Section No. | Section Title | Module | File Path | Diagram Included |
| :--- | :--- | :--- | :--- | :---: |
| **Title Page** | Project Title, Student & Guide Details, University Metadata | COMMON | [00_common.md](file:///d:/end-capstone-project/cleaned/docs/lld/00_common.md) | N |
| **1.1** | Overview | COMMON | [00_common.md](file:///d:/end-capstone-project/cleaned/docs/lld/00_common.md) | N |
| **1.2** | Purpose | COMMON | [00_common.md](file:///d:/end-capstone-project/cleaned/docs/lld/00_common.md) | N |
| **1.3** | Scope | COMMON | [00_common.md](file:///d:/end-capstone-project/cleaned/docs/lld/00_common.md) | N |
| **2.0** | Design Constraints, Assumptions, and Dependencies | COMMON | [00_common.md](file:///d:/end-capstone-project/cleaned/docs/lld/00_common.md) | N |
| **3.1** | Master Class Diagram & System Decomposition | COMMON | [00_common.md](file:///d:/end-capstone-project/cleaned/docs/lld/00_common.md) | **Y (Mermaid)** |
| **3.2** | Module 1: Leaf Pathology Computer Vision Diagnostic Module | Module 1 | [01_leaf_pathology_cnn.md](file:///d:/end-capstone-project/cleaned/docs/lld/01_leaf_pathology_cnn.md) | **Y (Use Case, Class, Sequence)** |
| **3.3** | Module 2: 3-Stage Hybrid RAG Knowledge Retrieval Module | Module 2 | [02_hybrid_rag_advisory.md](file:///d:/end-capstone-project/cleaned/docs/lld/02_hybrid_rag_advisory.md) | **Y (Use Case, Class, Sequence)** |
| **3.4** | Module 3: Multimodal Agronomic Advisory & Linguistic Routing Module | Module 3 | [03_multimodal_chat_routing.md](file:///d:/end-capstone-project/cleaned/docs/lld/03_multimodal_chat_routing.md) | **Y (Use Case, Class, Sequence)** |
| **3.5** | Module 4: Precision Microclimate Risk Engine & Spatial Marketplace Module | Module 4 | [04_microclimate_marketplace.md](file:///d:/end-capstone-project/cleaned/docs/lld/04_microclimate_marketplace.md) | **Y (Use Case, Class, Sequence)** |
| **3.6** | Packaging and Deployment Diagram | COMMON | [05_packaging_deployment.md](file:///d:/end-capstone-project/cleaned/docs/lld/05_packaging_deployment.md) | **Y (Mermaid)** |
| **App. A** | Definitions, Acronyms and Abbreviations | Appendices | [99_appendices.md](file:///d:/end-capstone-project/cleaned/docs/lld/99_appendices.md) | N |
| **App. B** | References & Design Standards | Appendices | [99_appendices.md](file:///d:/end-capstone-project/cleaned/docs/lld/99_appendices.md) | N |
| **App. C** | Record of Change History | Appendices | [99_appendices.md](file:///d:/end-capstone-project/cleaned/docs/lld/99_appendices.md) | N |
| **App. D** | Forward & Backward Traceability Matrix | Appendices | [99_appendices.md](file:///d:/end-capstone-project/cleaned/docs/lld/99_appendices.md) | N |

---

### Document Conventions & Verification Summary
- **Source of Truth**: All class definitions, typed attributes, method signatures, parameters, exceptions, and pseudo-code reflect the code in `backend/app/` and `frontend/`.
- **Mermaid Syntax**: All diagrams conform to standard Mermaid v10+ syntax and are validated for rendering in Mermaid Live Editor and Markdown readers.
- **Academic Standard**: Adheres strictly to the PES University UE23CS441A Capstone Phase 3 template specifications.
