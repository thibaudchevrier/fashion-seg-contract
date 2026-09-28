"""Contract of the fashion segmentation model: request, response schema, RLE masks, class labels.

Shared by the producer (fashion-seg-train, which packages the model) and its consumers
(fashion-serving). Depends on numpy only; ``schema.validate`` needs the ``validate`` extra.
"""
