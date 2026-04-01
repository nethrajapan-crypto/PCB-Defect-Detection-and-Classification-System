#!/usr/bin/env python3
"""Compute class co-occurrence matrices and save heatmap images."""
import json
import os
from collections import Counter
import numpy as np
import matplotlib.pyplot as plt

IN_JSON = "dataset_annotations.json"
OUT_DIR = "analysis"

def load_data(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def compute_cooccurrence(data, classes):
    # cooccurrence by image: count images where class i and j both appear
    idx = {c: i for i, c in enumerate(classes)}
    M = np.zeros((len(classes), len(classes)), dtype=int)
    for img, objs in data.items():
        present = set(o['class'] for o in objs)
        for a in present:
            for b in present:
                M[idx[a], idx[b]] += 1
    return M

def compute_count_matrix(data, classes):
    # total object counts per class (diagonal) and pairwise image co-counts
    idx = {c: i for i, c in enumerate(classes)}
    N = np.zeros((len(classes), len(classes)), dtype=int)
    # diagonal: total objects
    counts = Counter()
    for objs in data.values():
        for o in objs:
            counts[o['class']] += 1
    for c in classes:
        N[idx[c], idx[c]] = counts[c]
    return N

def plot_heatmap(mat, classes, title, out_path, normalize=False):
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    if normalize:
        mat = mat.astype(float)
        # normalize by number of images for co-occurrence
        denom = np.max(mat) if np.max(mat) > 0 else 1
        mat = mat / denom

    fig, ax = plt.subplots(figsize=(8, 6))
    im = ax.imshow(mat, cmap='viridis')
    ax.set_xticks(np.arange(len(classes)))
    ax.set_yticks(np.arange(len(classes)))
    ax.set_xticklabels(classes, rotation=45, ha='right')
    ax.set_yticklabels(classes)
    ax.set_title(title)
    for i in range(mat.shape[0]):
        for j in range(mat.shape[1]):
            txt = f"{mat[i,j]:.0f}" if not normalize else f"{mat[i,j]:.2f}"
            ax.text(j, i, txt, ha='center', va='center', color='white', fontsize=8)
    fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)

def main():
    if not os.path.exists(IN_JSON):
        print(f"Missing {IN_JSON}")
        return
    data = load_data(IN_JSON)
    # Determine classes (keep deterministic order)
    classes = sorted({o['class'] for objs in data.values() for o in objs})
    print("Classes:", classes)

    co = compute_cooccurrence(data, classes)
    plot_heatmap(co, classes, 'Class Co-occurrence (by image)', os.path.join(OUT_DIR, 'cooccurrence_counts.png'))
    plot_heatmap(co, classes, 'Class Co-occurrence (normalized)', os.path.join(OUT_DIR, 'cooccurrence_normalized.png'), normalize=True)

    counts = compute_count_matrix(data, classes)
    plot_heatmap(counts, classes, 'Per-class Object Counts', os.path.join(OUT_DIR, 'per_class_counts.png'))

    print(f"Saved heatmaps to {OUT_DIR}/")

if __name__ == '__main__':
    main()
