#!/usr/bin/env python3
"""
NeuroCap – generate_brain_mesh.py
==================================
Zero external dependencies (pure Python stdlib).
Works on Python 3.6+ including 3.14.

Generates a high-resolution procedural brain mesh with organised coronal gyri,
cerebellum folia, and correct hemisphere separation.  The result is saved as
Frontend/public/brain_mesh.json and loaded automatically by Brain3D.jsx.

Usage (from any directory):
    python app/Frontend/scripts/generate_brain_mesh.py

Expected runtime: < 10 seconds on a modern PC.
Output size:      ~ 2-4 MB
"""

import math
import json
from pathlib import Path

TAU = math.tau          # 2π

# ── Displacement functions ────────────────────────────────────────────────────

def gyri(theta, phi):
    """
    Multi-frequency coronal gyri using cylindrical angle θ.
    Ridges run AROUND the brain, not randomly — matches anatomy.
    phi  = polar angle (0 = top, π = bottom)
    theta = azimuthal angle around y-axis
    """
    return (
        math.sin(5.5 * phi + math.sin(2.8 * theta) * 0.90) * 0.048 +
        math.sin(5.5 * phi + 2.10 + math.cos(3.3 * theta) * 0.80) * 0.030 +
        math.sin(9.2 * phi + math.cos(5.1 * theta + 0.80) * 0.95) * 0.018 +
        math.sin(9.2 * phi + 1.80 + math.sin(6.0 * theta) * 0.70) * 0.013 +
        math.sin(15. * phi + math.cos(8.5 * theta + 1.50) * 1.10) * 0.006
    )

def folia(theta, phi):
    """Tight parallel horizontal stripes — characteristic cerebellum texture."""
    return (
        math.cos(20 * phi + math.sin(theta * 4) * 0.4) * 0.018 +
        math.cos(28 * phi + math.cos(theta * 5) * 0.3) * 0.010
    )

# ── Mesh builders ─────────────────────────────────────────────────────────────

def make_hemisphere(nu, nv, flip_x=False, disp_fn=gyri):
    """
    Parameterised sphere with gyri displacement, brain proportions,
    and inferior (bottom) surface flattening.

    Returns (flat_vertices, flat_face_indices, vertex_count).
    """
    sign_x = -1.0 if flip_x else 1.0
    verts  = []

    for i in range(nu + 1):
        phi    = math.pi * i / nu
        sin_p  = math.sin(phi)
        cos_p  = math.cos(phi)

        for j in range(nv):
            theta  = TAU * j / nv
            sin_t  = math.sin(theta)
            cos_t  = math.cos(theta)
            r      = 1.0 + disp_fn(theta, phi)

            # Brain proportions:  width 0.93, height 0.86, depth 0.93
            x = round(r * 0.93 * sign_x * sin_p * cos_t, 5)
            y = round(r * 0.86          * cos_p,          5)
            z = round(r * 0.93          * sin_p * sin_t,  5)

            # Flatten inferior surface
            if y < -0.24:
                y = round(-0.24 + (y + 0.24) * 0.28, 5)

            verts.extend([x, y, z])

    # Quad mesh → two triangles per quad
    faces = []
    for i in range(nu):
        for j in range(nv):
            a  =  i      * nv + j
            b  =  i      * nv + (j + 1) % nv
            c  = (i + 1) * nv + j
            d  = (i + 1) * nv + (j + 1) % nv
            faces.extend([a, b, c,  b, d, c])

    n_verts = (nu + 1) * nv
    return verts, faces, n_verts


def make_cerebellum(nu=40, nv=40):
    """
    Cerebellum with horizontal folia.  Already positioned at the
    correct location (back-bottom of the brain).
    """
    verts = []

    for i in range(nu + 1):
        phi   = math.pi * i / nu
        sin_p = math.sin(phi)
        cos_p = math.cos(phi)

        for j in range(nv):
            theta = TAU * j / nv
            r     = 1.0 + folia(theta, phi)

            x = round(r * 1.36 * 0.42 * sin_p * math.cos(theta), 5)
            y = round(r * 0.55 * 0.42 * cos_p  - 0.80,           5)
            z = round(r * 0.96 * 0.42 * sin_p * math.sin(theta) - 0.52, 5)

            verts.extend([x, y, z])

    faces = []
    for i in range(nu):
        for j in range(nv):
            a  =  i      * nv + j
            b  =  i      * nv + (j + 1) % nv
            c  = (i + 1) * nv + j
            d  = (i + 1) * nv + (j + 1) % nv
            faces.extend([a, b, c,  b, d, c])

    return verts, faces, (nu + 1) * nv


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    NU, NV   = 88, 88    # 89×88 ≈ 7 832 vertices / hemisphere
    OFFSET_X = 0.13      # gap between hemispheres (creates interhemispheric fissure)

    print(f"Left  hemisphere  {NU}×{NV} rings …")
    lh_v, lh_f, n_lh = make_hemisphere(NU, NV, flip_x=True)
    # Shift left hemisphere to the left
    for k in range(0, len(lh_v), 3):
        lh_v[k] -= OFFSET_X

    print(f"Right hemisphere  {NU}×{NV} rings …")
    rh_v, rh_f, n_rh = make_hemisphere(NU, NV, flip_x=False)
    # Shift right hemisphere to the right
    for k in range(0, len(rh_v), 3):
        rh_v[k] += OFFSET_X

    print("Cerebellum …")
    cb_v, cb_f, n_cb = make_cerebellum(40, 40)

    # Offset face indices for each sub-mesh
    rh_f_off = [idx + n_lh        for idx in rh_f]
    cb_f_off = [idx + n_lh + n_rh for idx in cb_f]

    all_verts = lh_v + rh_v + cb_v
    all_faces = lh_f + rh_f_off + cb_f_off

    n_total_verts = n_lh + n_rh + n_cb
    n_total_tris  = len(all_faces) // 3

    # ── Save ──────────────────────────────────────────────────────────────────
    out_path = Path(__file__).resolve().parent.parent / "public" / "brain_mesh.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)

    print(f"Saving {n_total_verts:,} vertices, {n_total_tris:,} triangles …")
    with open(out_path, "w") as f:
        json.dump(
            {"vertices": all_verts, "faces": all_faces, "n_left": n_lh},
            f,
            separators=(",", ":"),
        )

    size_kb = out_path.stat().st_size / 1024
    print()
    print(f"✓  Saved : {out_path}")
    print(f"   Size  : {size_kb:,.0f} KB")
    print(f"   Verts : {n_total_verts:,}  (left {n_lh:,}  right {n_rh:,}  cerebellum {n_cb:,})")
    print(f"   Tris  : {n_total_tris:,}")
    print()
    print("Refresh the browser — Brain3D loads the high-res mesh automatically.")


if __name__ == "__main__":
    main()
