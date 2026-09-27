"""Contract of the fashion segmentation model: response schema, RLE masks, class labels.

Shared by the producer (fashion-seg-train, which packages the model) and its consumers
(fashion-serving). Depends on numpy only; ``validate`` needs the ``validate`` extra.
"""
