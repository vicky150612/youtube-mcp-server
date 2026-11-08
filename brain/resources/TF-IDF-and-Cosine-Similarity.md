---
title: TF-IDF and Cosine Similarity
type: research
aliases:
  - Video Similarity Algorithms
tags:
  - research
  - youtube-mcp
  - similarity
  - text
sources:
  - "https://scikit-learn.org/stable/modules/feature_extraction.html"
  - "https://scikit-learn.org/stable/modules/metrics.html#cosine-similarity"
author:
  - Person 3
created: 2026-11-07
---

# TF-IDF and Cosine Similarity

## Overview

TF-IDF is a way to turn text into weighted numerical features; cosine similarity compares the direction of two such vectors. Together they provide an explainable baseline for comparing the text metadata of videos or channels. They measure lexical overlap, not full semantic meaning.

## Key Concepts

- **Term frequency (TF):** How often a term appears in a document. In a simple count representation, a document is represented by one feature per vocabulary term.
- **Document frequency (DF):** The number of documents in a corpus that contain a term.
- **Inverse document frequency (IDF):** A weight that reduces the influence of terms appearing in many documents and increases the relative importance of rarer terms. Scikit-learn's default smoothed IDF is `log((1 + n) / (1 + df(t))) + 1`, where `n` is the number of documents and `df(t)` is the number containing term `t`.
- **Vectorization:** Tokenize text, map terms to vocabulary features, and create one numerical feature vector per document. The document collection forms a matrix; text vectors are often sparse because most documents contain only a small portion of the corpus vocabulary.
- **Cosine similarity:** The L2-normalized dot product, `x · y / (||x|| ||y||)`, which measures the angle-based similarity of two vectors. Scikit-learn notes it is commonly used with TF-IDF document vectors.

## Important Findings

- Bag-of-words vectorization records token counts and ignores word order. N-grams can retain some local word-order information, at the cost of a larger vocabulary.
- TF-IDF combines within-document term frequency with corpus-wide inverse document frequency. Scikit-learn's default transformer smooths IDF and L2-normalizes the resulting vectors.
- A video can be represented as a text document assembled from its available title, description and tags; channels can be represented from available channel text and associated metadata. Treat field selection, normalization and weighting as design choices rather than fixed properties of TF-IDF.
- The methods are corpus- and preprocessing-dependent. They can miss synonyms or related concepts with little shared vocabulary, overweight noisy/repeated phrases, and provide little signal when metadata is missing or empty. Removing stop words can help in some cases but can also remove informative terms; scikit-learn cautions that stop-word lists are task-dependent.

## Relevance to Our Project

The following is a project application, not a decision that this algorithm has been selected:

1. Retrieve candidate metadata through the official YouTube provider, separately from ranking.
2. Build text representations from available titles, descriptions and tags, handling absent fields without inventing content.
3. Fit or apply a consistent TF-IDF vocabulary to the source and candidates, calculate cosine similarity, and rank candidates by score.
4. Evaluate field weighting, stop-word/tokenization choices and candidate discovery with fixtures before choosing a production method.

This is a candidate approach for `FR-01` and `FR-02`; it does not rely on a YouTube related-video or related-channel endpoint. The final feature set, weights, candidate strategy and evaluation method remain open. Identical inputs and preprocessing should yield deterministic rankings under `NFR-10`, with unit coverage under `TQ-01`.

## Related Requirements

`FR-01`, `FR-02`, `NFR-07`, `NFR-10`, `TQ-01`. Requirement source: [SRS](../../docs/srs.md).

## Sources

- **Feature extraction** — scikit-learn documentation. https://scikit-learn.org/stable/modules/feature_extraction.html (accessed 2026-11-07; documentation version shown as stable).
- **Pairwise metrics, affinities and kernels — Cosine similarity** — scikit-learn documentation. https://scikit-learn.org/stable/modules/metrics.html#cosine-similarity (accessed 2026-11-07; documentation version shown as stable).

## Related Notes

- [[YouTube-Video-Resource|YouTube Video Resource]]
- [[YouTube-Channel-Resource|YouTube Channel Resource]]
- [[YouTube-Data-API|YouTube Data API]]
- [[YouTube-API-Quota-Management|YouTube API Quota Management]]
