# Dataset

The original notebook streamed the CSV straight from a Google Drive share
link every time it ran. That's fine for Colab, but it's not reproducible
for a pipeline (the link's permissions or availability could change, and
there's no version history).

For now, download the CSV once and place it at `data/fossil_data.csv`
(this matches `config.yaml`'s `data.raw_path`). The link is in the original
notebook, or ask the project owner for it.