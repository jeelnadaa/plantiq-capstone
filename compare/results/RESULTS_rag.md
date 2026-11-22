## Module 2 (RAG)

75 questions (English + Kannada) for retrieval.

### Retrieval

|                                       |   recall@1 |   recall@3 |   recall@5 |   recall@10 |   hit@3 |   ndcg@3 |   mrr@10 |
|:--------------------------------------|-----------:|-----------:|-----------:|------------:|--------:|---------:|---------:|
| Selva Kumar et al. (dense, LangChain) |      0.293 |      0.500 |      0.567 |       0.640 |   0.507 |    0.390 |    0.408 |
| Dense only                            |      0.520 |      0.707 |      0.800 |       0.880 |   0.707 |    0.578 |    0.625 |
| BM25 only                             |      0.373 |      0.627 |      0.733 |       0.853 |   0.627 |    0.513 |    0.524 |
| Dense+BM25 (RRF)                      |      0.560 |      0.707 |      0.827 |       0.907 |   0.707 |    0.627 |    0.660 |
| RRF + rerank                          |      0.613 |      0.893 |      0.933 |       0.933 |   0.893 |    0.764 |    0.743 |
| Full PlantIQ (+topic, MMR)            |      0.613 |      0.867 |      0.920 |       0.960 |   0.867 |    0.758 |    0.743 |
| Full PlantIQ, router offline          |      0.533 |      0.787 |      0.827 |       0.853 |   0.787 |    0.679 |    0.656 |

### Generation (same LLM for every system)

|                                          |   faithfulness |   correctness |   relevance |   unsupported doses |   answers with doses |   words |
|:-----------------------------------------|---------------:|--------------:|------------:|--------------------:|---------------------:|--------:|
| PlantIQ hybrid RAG                       |          0.992 |         0.944 |       0.972 |               0.000 |                0.519 |  60.074 |
| Selva Kumar et al. (dense LangChain RAG) |          0.990 |         0.824 |       0.917 |               0.000 |                0.259 |  27.167 |
| LLM, no retrieval                        |        nan     |         0.611 |       1.000 |               0.204 |                0.204 |  43.833 |
