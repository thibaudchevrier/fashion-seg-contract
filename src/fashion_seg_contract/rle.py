"""Run-length encoding used by the iMaterialist annotations.

Format: space-separated ``start length`` pairs, 1-indexed starts, pixels enumerated in
column-major (Fortran) order, i.e. top-to-bottom then left-to-right. The same format is used for
the ``mask_rle`` of predictions, so training data and model responses are decoded by the same
function.
"""

import numpy as np


def decode(rle: str, height: int, width: int) -> np.ndarray:
    """Decode an RLE string into a boolean mask.

    Parameters
    ----------
    rle : str
        Space-separated ``start length`` pairs, 1-indexed, column-major. Empty for an empty mask.
    height : int
        Mask height in pixels.
    width : int
        Mask width in pixels.

    Returns
    -------
    np.ndarray
        Boolean mask of shape ``(height, width)``.

    Examples
    --------
    >>> decode("1 2 4 1", height=3, width=2).astype(int)
    array([[1, 1],
           [1, 0],
           [0, 0]])
    """
    flat = np.zeros(height * width, dtype=bool)
    values = np.array(rle.split(), dtype=np.int64)
    for start, length in zip(values[::2] - 1, values[1::2], strict=True):
        flat[start : start + length] = True
    return flat.reshape((height, width), order="F")


def encode(mask: np.ndarray) -> str:
    """Encode a 2D mask into an RLE string.

    Parameters
    ----------
    mask : np.ndarray
        Mask of shape ``(height, width)``; non-zero pixels belong to the mask.

    Returns
    -------
    str
        Space-separated ``start length`` pairs, 1-indexed, column-major. Empty for an empty mask.

    Examples
    --------
    >>> encode(np.ones((4, 4), dtype=bool))
    '1 16'
    """
    flat = np.asarray(mask, dtype=bool).flatten(order="F")
    # Pad so that runs touching the borders produce a transition.
    padded = np.concatenate([[False], flat, [False]])
    transitions = np.flatnonzero(padded[1:] != padded[:-1]) + 1
    starts, ends = transitions[::2], transitions[1::2]
    return " ".join(f"{s} {e - s}" for s, e in zip(starts, ends, strict=True))
