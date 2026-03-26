# Architecture Figure Layout Specification

## Target: IEEE RA-L double-column (~7in / 504pt wide)
## Achieved: 505 x 191 pt (7.0 x 2.7 in) ✓

## Actual Architecture (from code)

### Shared Encoder (all 3 variants use this)
```
Grid(6×7×7) → CNN(24ch) → Flat ─┐
                                  ├→ spatial_cat → Spatial LSTM(h=96) ─┐
Field(7×7×7) → CNN(28ch) → Flat ─┘                                     ├→ merge_cat(160)
                                                                        │
Scalar(62) → TypeRoute(64) → ReLU(scalar_act) → Scalar LSTM(h=64) ────┘
```

### IPPO (model_0 only, model_1 = MaskRoute)
```
model_0: merge_cat → Dec(128) → ReLU → Actions(7h) + critic_0 + critic_1
model_1: MaskRoute(critic_0, critic_1, sleep_slice) → critic_routed → V
```

### CTDE (model_0 = actor, model_1 = critic, model_2 = MaskRoute)
```
model_0: merge_cat → Dec(128) → ReLU → Actions(7h)
model_1: cat(spatial_cat, scalar_act) → CriticFC(128) → ReLU → critic_0 + critic_1
model_2: MaskRoute(critic_0, critic_1, sleep_slice) → critic_routed → V
```
**Key**: model_1 reads PRE-LSTM outputs (spatial_cat + scalar_act) via cross-model refs

### SHARED (model_0 = attn+actor, model_1 = critic, model_2 = MaskRoute)
```
model_0: merge_cat → TopoAttn(4h) + residual → Dec(128) → ReLU → Actions(7h)
model_1: cat(spatial_cat, scalar_act) → CriticFC(128) → ReLU → critic_0 + critic_1
model_2: MaskRoute(critic_0, critic_1, sleep_slice) → critic_routed → V
```
**Key**: model_1 identical to CTDE. model_0 adds topology-masked attention.

---

## Layout Grid System

### Coordinate System
- X: left-to-right (0 = left margin)
- Y: top-to-bottom (higher Y = higher on page)
- Total width target: ~16cm (≈ 7in at 72dpi)

### Vertical Zones
| Zone | Y range | Content |
|------|---------|---------|
| Encoder | 3.5 – 5.5 | Shared Morton Encoder |
| Bus | 2.0 – 3.0 | Vertical drop + horizontal distribution bus |
| Variants | -0.5 – 1.5 | Three variant columns (IPPO / CTDE / SHARED) |
| Legend | 4.0 – 5.5 | Far right, at encoder height |

### Horizontal Zones (3 equal columns for variants)
| Column | X range | Width | Content |
|--------|---------|-------|---------|
| IPPO | 0.0 – 4.5 | 4.5 | Simplest (actor+critic in model_0) |
| CTDE | 5.0 – 9.5 | 4.5 | Actor(m0) + Critic(m1) + Route(m2) |
| SHARED | 10.0 – 14.5 | 4.5 | Attn+Actor(m0) + Critic(m1) + Route(m2) |
| Legend | 15.0 – 17.0 | 2.0 | Color key |

### Encoder Layout (centered above variants, X ~ 2.5 – 12.5)
| Element | X | Y | Size |
|---------|---|---|------|
| Grid 3D box | 3.0 | 4.8 | scale=0.06 |
| Field 3D box | 3.0 | 4.0 | scale=0.06 |
| Scalar 3D box | 3.0 | 3.2 | scale=0.06 |
| CNN(grid) | 4.8 | 4.8 | 0.8cm wide |
| CNN(field) | 4.8 | 4.0 | 0.8cm wide |
| Flat(grid) | 5.9 | 4.8 | 0.55cm |
| Flat(field) | 5.9 | 4.0 | 0.55cm |
| spatial_cat ⊕ | 6.8 | 4.4 | circle 0.32cm |
| Sp-LSTM | 7.8 | 4.4 | 1.0cm, double |
| TypeRoute | 5.0 | 3.2 | 0.8cm |
| scalar_act ReLU | 5.9 | 3.2 | (implicit) |
| Sc-LSTM | 7.8 | 3.2 | 0.9cm, double |
| merge_cat ⊕ | 9.0 | 3.8 | circle 0.36cm |
| Encoder title | centered | 5.3 | "Shared Morton Encoder" |

### Bus Routing (CRITICAL - user spec)

**Concept**: From encoder, ONE vertical bus drops down. Then TWO horizontal buses span across the critic columns. Individual vertical drops from horizontal bus to each critic node.

**Bus lines**:
1. **merge_cat bus** (solid, edgecol): vertical drop from merge_cat(9.0, 3.8) down to y=1.5, then horizontal split to each variant's actor input
2. **pre-LSTM bus** (dashed, xrefcol): Two sub-buses for cross-model critic input
   - **spatial_cat line** (dashed red, thicker): drops from spatial_cat(6.8, 4.4) down to y=2.2, runs horizontally to CTDE+SHARED critic_cat positions, then drops into each
   - **scalar_act line** (dotted red, thinner): drops from scalar_act area(5.9, 3.2) down to y=1.9, runs horizontally to CTDE+SHARED critic_cat positions, then drops into each

**Bus Y levels**:
| Bus | Y level | Style | Purpose |
|-----|---------|-------|---------|
| merge→actor | 1.5 | solid gray | Feed merge_cat to all 3 actor paths |
| spatial_cat→critic | 2.2 | dashed red | Pre-LSTM spatial to CTDE/SHARED critics |
| scalar_act→critic | 1.9 | dotted red | Pre-LSTM scalar to CTDE/SHARED critics |

### Variant Column Layouts

#### IPPO (X: 0.0 – 4.5, centered at 2.25)
| Element | X | Y | Notes |
|---------|---|---|-------|
| Title "(i) IPPO" | 0.2 | 1.4 | sectitle |
| Dec(128) | 1.2 | 0.8 | from merge bus |
| Actions(7h) | 2.5 | 1.1 | actor output |
| critic_0 (Vₐ) | 2.3 | 0.2 | awake critic |
| critic_1 (Vₛ) | 3.0 | 0.2 | sleep critic |
| MaskRoute | 3.8 | 0.2 | sleep_slice routing |
| V | 4.3 | 0.2 | final value |
| bg box | fit all | | blue tint |

#### CTDE (X: 5.0 – 9.5, centered at 7.25)
| Element | X | Y | Notes |
|---------|---|---|-------|
| Title "(ii) CTDE" | 5.2 | 1.4 | sectitle |
| **Actor row (model_0)** | | 1.1 | |
| Dec(128) | 6.0 | 1.1 | from merge bus |
| Actions(7h) | 7.3 | 1.1 | actor output |
| **Critic row (model_1)** | | 0.2 | |
| cat ⊕ | 6.0 | 0.2 | from pre-LSTM buses |
| CriticFC(128) | 6.8 | 0.2 | |
| critic_0 (Vₐ) | 7.6 | 0.4 | |
| critic_1 (Vₛ) | 7.6 | 0.0 | |
| MaskRoute | 8.4 | 0.2 | model_2 |
| V | 9.0 | 0.2 | |
| bg box | fit all | | green tint |

#### SHARED (X: 10.0 – 14.5, centered at 12.25)
| Element | X | Y | Notes |
|---------|---|---|-------|
| Title "(iii) Shared" | 10.2 | 1.4 | sectitle |
| **Actor row (model_0)** | | 1.1 | |
| TopoAttn(4h) | 11.0 | 1.1 | topology-masked |
| +res ⊕ | 11.8 | 1.1 | residual add |
| Dec(128) | 12.4 | 1.1 | |
| Actions(7h) | 13.2 | 1.1 | actor output |
| **Critic row (model_1)** | | 0.2 | |
| cat ⊕ | 11.0 | 0.2 | from pre-LSTM buses |
| CriticFC(128) | 11.8 | 0.2 | |
| critic_0 (Vₐ) | 12.6 | 0.4 | |
| critic_1 (Vₛ) | 12.6 | 0.0 | |
| MaskRoute | 13.4 | 0.2 | model_2 |
| V | 14.0 | 0.2 | |
| bg box | fit all | | violet tint |

### Legend (X: 15.0, Y: 4.0 – 5.5)
At encoder height to avoid widening figure at bottom.

---

## Color Palette
| Color | RGB | Use |
|-------|-----|-----|
| cnnfill | 255,213,128 | Conv layers |
| lstmfill | 153,204,179 | LSTM cells |
| fcfill | 200,210,230 | Linear/Dec |
| actfill | 140,170,220 | Action heads |
| critfill | 230,160,140 | Critic heads |
| attnfill | 190,170,220 | Attention |
| routefill | 255,200,120 | MaskRoute |
| mergefill | 140,210,160 | Cat/merge ops |
| xrefcol | 180,60,60 | Cross-model refs |
| edgecol | 80,80,80 | Normal connections |

## Line Styles
| Style | TikZ | Purpose |
|-------|------|---------|
| conn | solid, edgecol, 0.5pt | Normal data flow |
| merge-bus | solid, edgecol, 0.7pt | merge_cat distribution |
| spatial-bus | dashed, xrefcol, 0.6pt | spatial_cat xref |
| scalar-bus | densely dotted, xrefcol, 0.6pt | scalar_act xref |
