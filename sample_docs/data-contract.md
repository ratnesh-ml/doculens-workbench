# Data contracts

A data contract names the required fields, expected types, and known limits.
It should be checked before training or retrieval begins.

## Leakage

Information that would not be available at prediction time must not enter a
training feature. Time-aware validation is often a better default for logs.
