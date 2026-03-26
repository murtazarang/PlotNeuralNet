"""
Morton Architecture Diagram Generator v4
=========================================

Full rewrite with correct dual-critic architecture from actual code.
Layout spec: LAYOUT_SPEC.md

Compile:  pdflatex fig_architecture.tex && pdflatex fig_morton_topo.tex
"""

import os


def generate_architecture_figure():
    return r"""\documentclass[border=4pt, multi, tikz]{standalone}
\usepackage{import}
\subimport{../layers/}{init}
\usetikzlibrary{positioning, 3d, arrows.meta, decorations.pathreplacing,
                 calc, fit, backgrounds}
\usepackage{amsmath}

% === Colors ===
\definecolor{cnnfill}{RGB}{255,213,128}
\definecolor{lstmfill}{RGB}{153,204,179}
\definecolor{fcfill}{RGB}{200,210,230}
\definecolor{actfill}{RGB}{140,170,220}
\definecolor{critfill}{RGB}{230,160,140}
\definecolor{attnfill}{RGB}{190,170,220}
\definecolor{routefill}{RGB}{255,200,120}
\definecolor{mergefill}{RGB}{140,210,160}
\definecolor{scalarfill}{RGB}{210,180,210}
\def\GridFill{rgb:green,4;black,1;white,8}
\def\FieldFill{rgb:blue,4;cyan,1;white,8}
\def\ScalarFill{rgb:red,2;blue,2;white,10}
\definecolor{xrefcol}{RGB}{180,60,60}
\definecolor{edgecol}{RGB}{80,80,80}
\definecolor{spbuscol}{RGB}{50,120,50}
\definecolor{scbuscol}{RGB}{120,50,120}

\begin{document}
\begin{tikzpicture}[
    >=Stealth,
    blk/.style={draw, rounded corners=1.5pt, minimum height=0.40cm,
                font=\sffamily\fontsize{5.5}{6.5}\selectfont,
                inner sep=1.5pt, thick},
    conn/.style={->, thick, draw=edgecol, line width=0.5pt},
    mergebus/.style={-, draw=edgecol, line width=0.7pt},
    spbus/.style={-, dashed, draw=spbuscol, line width=0.6pt},
    scbus/.style={-, densely dotted, draw=scbuscol, line width=0.6pt},
    dimtxt/.style={font=\sffamily\fontsize{4.5}{5}\selectfont\itshape, text=black!50},
    sectitle/.style={font=\sffamily\fontsize{6.5}{7.5}\selectfont\bfseries},
    cattxt/.style={draw, circle, fill=mergefill, inner sep=1pt, minimum size=0.30cm,
                   font=\sffamily\fontsize{5}{5}\selectfont},
]

% =====================================================================
% SHARED ENCODER  (y: 3.2 – 5.5)
% Centered at x=7.5 (midpoint of 0..15 variant span)
% =====================================================================

\node[sectitle, anchor=south] at (7.5, 5.45) {Shared Morton Encoder};

% -- Observation 3D boxes --
\pic[shift={(2.5,4.8,0)}] at (0,0,0) {
    Box={name=ogrid, caption=,
         xlabel={{" "," "," "," "," "," "}},
         fill=\GridFill, opacity=0.6,
         height=8, width={0.6,0.6,0.6,0.6,0.6,0.6}, depth=8, scale=0.06}};
\node[font=\sffamily\fontsize{5}{6}\selectfont, anchor=east, text=black!70]
    (lbl_grid) at ([xshift=-3pt]ogrid-west) {Grid};

\pic[shift={(2.5,4.0,0)}] at (0,0,0) {
    Box={name=ofield, caption=,
         xlabel={{" "," "," "," "," "," "," "}},
         fill=\FieldFill, opacity=0.6,
         height=8, width={0.5,0.5,0.5,0.5,0.5,0.5,0.5}, depth=8, scale=0.06}};
\node[font=\sffamily\fontsize{5}{6}\selectfont, anchor=east, text=black!70]
    (lbl_field) at ([xshift=-3pt]ofield-west) {Field};

\pic[shift={(2.5,3.2,0)}] at (0,0,0) {
    Box={name=oscalar, caption=,
         fill=\ScalarFill, opacity=0.5,
         height=2, width={1.2}, depth=8, scale=0.06}};
\node[font=\sffamily\fontsize{5}{6}\selectfont, anchor=east, text=black!70]
    (lbl_scalar) at ([xshift=-3pt]oscalar-west) {Scalar};



% -- CNN branches --
\node[blk, fill=cnnfill, minimum width=0.8cm] (cnng) at (4.5, 4.8)
    {Conv$_{3\!\times\!3}$ {\scriptsize$\times$2}};

\node[blk, fill=cnnfill, minimum width=0.8cm] (cnnf) at (4.5, 4.0)
    {Conv$_{3\!\times\!3}$ {\scriptsize$\times$2}};

% Flatten
\node[blk, fill=fcfill, minimum width=0.55cm] (flatg) at (5.9, 4.8) {Flat};
\node[blk, fill=fcfill, minimum width=0.55cm] (flatf) at (5.9, 4.0) {Flat};

% spatial_cat
\node[cattxt] (spcat) at (7.0, 4.4) {$\oplus$};

% Spatial LSTM
\node[blk, fill=lstmfill, minimum width=1.0cm, double, double distance=0.5pt]
    (splstm) at (8.2, 4.4) {Sp-LSTM {\tiny$h{=}96$}};

% Scalar branch
\node[blk, fill=scalarfill, minimum width=0.8cm, opacity=0.8] (troute) at (5.2, 3.2)
    {TypeRoute {\tiny 64}};

% scalar_act (ReLU)
\node[blk, fill=fcfill, minimum width=0.55cm] (scact) at (6.5, 3.2) {ReLU};

% Scalar LSTM
\node[blk, fill=lstmfill, minimum width=0.9cm, double, double distance=0.5pt]
    (sclstm) at (8.2, 3.2) {Sc-LSTM {\tiny$h{=}64$}};

% merge_cat
\node[cattxt, minimum size=0.34cm,
      font=\sffamily\fontsize{5.5}{6}\selectfont] (merge) at (9.5, 3.8) {$\oplus$};
\node[dimtxt, anchor=west] at ([xshift=4pt]merge.east) {160};

% -- Encoder connections --
\draw[conn] (ogrid-east) -- node[dimtxt, above=-1pt] {$6{\times}7{\times}7$} (cnng.west);
\draw[conn] (ofield-east) -- node[dimtxt, above=-1pt] {$7{\times}7{\times}7$} (cnnf.west);
\draw[conn] (oscalar-east) -- node[dimtxt, above=-1pt] {62} (troute.west);
\draw[conn] (cnng) -- node[dimtxt, above=-1pt] {24ch} (flatg);
\draw[conn] (cnnf) -- node[dimtxt, above=-1pt] {28ch} (flatf);
\draw[conn] (flatg.east) -| (spcat);
\draw[conn] (flatf.east) -| (spcat);
\draw[conn] (spcat) -- (splstm);
\draw[conn] (troute) -- (scact);
\draw[conn] (scact) -- (sclstm);
\draw[conn] (splstm.east) -| (merge);
\draw[conn] (sclstm.east) -| (merge);

% Encoder background
\begin{scope}[on background layer]
\node[draw=black!15, fill=black!2, rounded corners=3pt, inner sep=4pt,
      fit=(lbl_grid)(ogrid-north)(merge)(lbl_scalar)(oscalar-nearsouthwest)(sclstm)]
      (encbox) {};
\end{scope}

% =====================================================================
% BUS SYSTEM  (y: 1.5 – 3.0)
%
% Three buses drop from encoder:
%   1. merge_cat bus (solid gray) → feeds actor path in all 3 variants
%   2. spatial_cat bus (dashed green) → feeds critic cat in CTDE+SHARED
%   3. scalar_act bus (dotted purple) → feeds critic cat in CTDE+SHARED
%
% Routing: vertical drop from encoder node → horizontal span → vertical
% drops into variant columns. Horizontal buses sit ABOVE critic rows to
% avoid crossing through boxes.
% =====================================================================

% --- Bus anchor points ---
% merge_cat drops from (9.5, 3.5) to horizontal at y=2.3
% spatial_cat drops from (6.8, 4.15) to horizontal at y=2.6
% scalar_act drops from (6.5, 2.95) to horizontal at y=2.0

% Y levels for horizontal runs
\def\mergebusY{2.30}
\def\spbusY{2.55}
\def\scbusY{2.05}

% Merge bus vertical drop
\draw[mergebus] (merge.south) -- (9.5, \mergebusY);
% Merge bus horizontal span (across all 3 variants: x=1.2 to x=12.5)
\draw[mergebus] (1.2, \mergebusY) -- (11.2, \mergebusY);

% spatial_cat bus vertical drop
\draw[spbus] (spcat.south) -- (7.0, \spbusY);
% spatial_cat bus horizontal span (extended left for CTDE routing)
\draw[spbus] (5.7, \spbusY) -- (10.3, \spbusY);

% scalar_act bus vertical drop
\draw[scbus] (scact.south) -- (6.5, \scbusY);
% scalar_act bus horizontal span (extended left for CTDE routing)
\draw[scbus] (5.5, \scbusY) -- (10.1, \scbusY);

% Bus labels (tiny, at left end)
\node[font=\sffamily\fontsize{3.5}{4}\selectfont, text=edgecol, anchor=east]
    at (1.1, \mergebusY) {merge};
\node[font=\sffamily\fontsize{3.5}{4}\selectfont, text=spbuscol, anchor=east]
    at (5.6, \spbusY) {sp};
\node[font=\sffamily\fontsize{3.5}{4}\selectfont, text=scbuscol, anchor=east]
    at (5.4, \scbusY) {sc};

% =====================================================================
% (i) IPPO          x: 0.0 – 4.8
% model_0: merge→Dec→Actions + critic_0 + critic_1
% model_1: MaskRoute(c0, c1, sleep) → V
% =====================================================================

\node[sectitle, text=blue!60!black, anchor=south] at (2.65, 1.55) {\textsc{(i) IPPO}};

% Actor row (y=1.1)
\node[blk, fill=fcfill, minimum width=0.7cm] (idec) at (1.2, 1.1) {Dec {\tiny 128}};
\node[blk, fill=actfill, minimum width=0.75cm] (iact) at (2.5, 1.1) {Act {\tiny 7h}};

% Critic row (y=0.3)
\node[blk, fill=critfill, minimum width=0.55cm] (ic0) at (1.8, 0.3) {$V_\text{a}$};
\node[blk, fill=critfill, minimum width=0.55cm] (ic1) at (2.5, 0.3) {$V_\text{s}$};
\node[blk, fill=routefill, minimum width=0.6cm, opacity=0.8] (irt) at (3.4, 0.3) {Route};
\node[blk, fill=critfill!60, minimum width=0.35cm] (iv) at (4.1, 0.3) {$V$};

% Connections: merge bus → Dec (straight vertical drop)
\draw[conn] (1.2, \mergebusY) -- (idec.north);
\draw[conn] (idec) -- (iact);
\draw[conn] (idec.south) -- ++(0,-0.3) -| (ic0.north);
\draw[conn] (idec.south) -- ++(0,-0.3) -| (ic1.north);
\draw[conn] (ic0.north east) to[out=25,in=155, looseness=0.5] (irt.north west);
\draw[conn] (ic1) -- (irt);
\draw[conn] (irt) -- (iv);



% IPPO background
\begin{scope}[on background layer]
\node[draw=blue!20, fill=blue!3, rounded corners=2pt, inner sep=3pt,
      fit=(idec)(iact)(iv)(ic0)(ic1)(irt)] (ippobox) {};
\end{scope}

% =====================================================================
% (ii) CTDE          x: 5.3 – 9.8
% model_0: merge→Dec→Actions
% model_1: cat(spatial_cat, scalar_act)→CriticFC→c0+c1
% model_2: MaskRoute→V
% =====================================================================

\node[sectitle, text=green!40!black, anchor=south] at (7.7, 1.55) {\textsc{(ii) CTDE}};

% Actor row (y=1.1)
\node[blk, fill=fcfill, minimum width=0.7cm] (cdec) at (6.3, 1.1) {Dec {\tiny 128}};
\node[blk, fill=actfill, minimum width=0.75cm] (cact) at (7.6, 1.1) {Act {\tiny 7h}};

% Critic row (y=0.3)
\node[cattxt, minimum size=0.26cm] (ccat) at (6.0, 0.3) {$\oplus$};
\node[blk, fill=critfill, minimum width=0.7cm] (cfc) at (6.9, 0.3) {CriticFC};
\node[blk, fill=critfill, minimum width=0.50cm] (cc0) at (7.8, 0.55) {$V_\text{a}$};
\node[blk, fill=critfill, minimum width=0.50cm] (cc1) at (7.8, 0.05) {$V_\text{s}$};
\node[blk, fill=routefill, minimum width=0.55cm, opacity=0.8] (crt) at (8.7, 0.3) {Route};
\node[blk, fill=critfill!60, minimum width=0.35cm] (cv) at (9.4, 0.3) {$V$};

% Actor connections (merge bus → straight vertical to Dec)
\draw[conn] (6.3, \mergebusY) -- (cdec.north);
\draw[conn] (cdec) -- (cact);

% Critic bus drops: left of actor boxes, enter cat from left (proper flow)
\draw[spbus, ->] (5.7, \spbusY) -- (5.7, 0.60) -- ($(ccat.north)+(0,0.17)$) -- (ccat.north);
\draw[scbus, ->] (5.5, \scbusY) -- (5.5, 0.3) -- (ccat.west);

% Critic chain
\draw[conn] (ccat) -- (cfc);
\draw[conn] (cfc.east) -- ++(0.15,0) |- (cc0.west);
\draw[conn] (cfc.east) -- ++(0.15,0) |- (cc1.west);
\draw[conn] (cc0.east) -| (crt.north);
\draw[conn] (cc1.east) -| (crt.south);
\draw[conn] (crt) -- (cv);



% CTDE background
\begin{scope}[on background layer]
\node[draw=green!20, fill=green!3, rounded corners=2pt, inner sep=3pt,
      fit=(cdec)(cact)(cv)(cc1)(ccat)(crt)] (ctdebox) {};
\end{scope}

% =====================================================================
% (iii) SHARED       x: 10.3 – 14.8
% model_0: merge→TopoAttn+res→Dec→Actions
% model_1: cat(spatial_cat, scalar_act)→CriticFC→c0+c1
% model_2: MaskRoute→V
% =====================================================================

\node[sectitle, text=violet!60!black, anchor=south] at (12.65, 1.55)
    {\textsc{(iii) Shared}};

% Actor row (y=1.1)
\node[blk, fill=attnfill, minimum width=0.8cm] (sattn) at (11.0, 1.1) {TopoAttn {\tiny 4h}};

\node[draw, circle, fill=mergefill!50, inner sep=0.5pt, minimum size=0.22cm,
      font=\sffamily\fontsize{4.5}{5}\selectfont] (sres) at (11.95, 1.1) {$\!+\!$};

\node[blk, fill=fcfill, minimum width=0.6cm] (sdec) at (12.65, 1.1) {Dec};
\node[blk, fill=actfill, minimum width=0.65cm] (sact) at (13.5, 1.1) {Act {\tiny 7h}};

% Residual skip (branches from merge→TopoAttn input)
\draw[conn, black!40] ([yshift=6pt]sattn.north) -| ([yshift=3pt]sres.north);

% Critic row (y=0.3)
\node[cattxt, minimum size=0.26cm] (scat) at (11.0, 0.3) {$\oplus$};
\node[blk, fill=critfill, minimum width=0.7cm] (sfc) at (11.9, 0.3) {CriticFC};
\node[blk, fill=critfill, minimum width=0.50cm] (sc0) at (12.8, 0.55) {$V_\text{a}$};
\node[blk, fill=critfill, minimum width=0.50cm] (sc1) at (12.8, 0.05) {$V_\text{s}$};
\node[blk, fill=routefill, minimum width=0.55cm, opacity=0.8] (srt) at (13.6, 0.3) {Route};
\node[blk, fill=critfill!60, minimum width=0.35cm] (sv) at (14.3, 0.3) {$V$};

% Actor connections (merge bus → straight vertical to TopoAttn)
\draw[conn] (11.0, \mergebusY) -- (sattn.north);
\draw[conn] (sattn) -- (sres);
\draw[conn] (sres) -- (sdec);
\draw[conn] (sdec) -- (sact);

% Critic bus drops: left of actor boxes, then horizontal into cat
\draw[spbus, ->] (10.2, \spbusY) -- (10.2, 0.60) -- ($(scat.north)+(0,0.17)$) -- (scat.north);
\draw[scbus, ->] (10.0, \scbusY) -- (10.0, 0.3) -- (scat.west);

% Critic chain
\draw[conn] (scat) -- (sfc);
\draw[conn] (sfc.east) -- ++(0.15,0) |- (sc0.west);
\draw[conn] (sfc.east) -- ++(0.15,0) |- (sc1.west);
\draw[conn] (sc0.east) -| (srt.north);
\draw[conn] (sc1.east) -| (srt.south);
\draw[conn] (srt) -- (sv);



% SHARED background
\begin{scope}[on background layer]
\node[draw=violet!20, fill=violet!3, rounded corners=2pt, inner sep=3pt,
      fit=(sattn)(sact)(sv)(sc1)(scat)(srt)] (sharedbox) {};
\end{scope}

% =====================================================================
% Legend (right of encoder, above buses)
% =====================================================================
\node[anchor=south west, font=\sffamily\fontsize{4.5}{5.5}\selectfont,
      text=black!60, inner sep=2pt, draw=black!15, rounded corners=2pt,
      fill=white] at (11.5, 3.6)
    {\begin{tabular}{@{}r@{\,}l@{\quad}r@{\,}l@{}}
     \tikz[baseline=-0.3ex]{\fill[cnnfill] (0,0) rectangle (0.18,0.13);} & Conv
     & \tikz[baseline=-0.3ex]{\fill[critfill] (0,0) rectangle (0.18,0.13);} & Critic \\
     \tikz[baseline=-0.3ex]{\fill[lstmfill] (0,0) rectangle (0.18,0.13);
           \draw[double, double distance=0.3pt] (0,0) rectangle (0.18,0.13);} & LSTM
     & \tikz[baseline=-0.3ex]{\fill[routefill, opacity=0.8] (0,0) rectangle (0.18,0.13);} & Route \\
     \tikz[baseline=-0.3ex]{\fill[attnfill] (0,0) rectangle (0.18,0.13);} & Attn
     & \tikz[baseline=-0.3ex]{\draw[dashed, spbuscol, thick] (0,0.06) -- (0.22,0.06);} & sp\_xref \\
     \tikz[baseline=-0.3ex]{\fill[mergefill] (0.09,0.065) circle (0.07);
           \draw (0.09,0.065) circle (0.07);} & Cat/$+$
     & \tikz[baseline=-0.3ex]{\draw[densely dotted, scbuscol, thick] (0,0.06) -- (0.22,0.06);} & sc\_xref \\
     \end{tabular}};

\end{tikzpicture}
\end{document}
"""


def generate_topology_figure():
    return r"""\documentclass[border=6pt, multi, tikz]{standalone}
\usetikzlibrary{positioning, arrows.meta, calc, fit, backgrounds,
                 decorations.pathreplacing}
\usepackage{amsmath, amssymb}

% ── Colour palette ──
\definecolor{liftcol}{RGB}{245,155,50}
\definecolor{senscol}{RGB}{70,170,70}
\definecolor{mortedge}{RGB}{31,119,180}
\definecolor{knnedge}{RGB}{140,90,180}
\definecolor{gridln}{RGB}{195,195,195}
\definecolor{gridfl}{RGB}{244,244,244}
\definecolor{hilight}{RGB}{255,230,180}
\definecolor{edgecol}{RGB}{100,100,100}

\begin{document}
\begin{tikzpicture}[
    >=Stealth,
    % Grid cell
    gc/.style={draw=gridln, minimum size=0.82cm, inner sep=0pt,
               font=\sffamily\fontsize{6}{7}\selectfont\color{black!40},
               fill=gridfl, anchor=center},
    % Agent circle
    ag/.style={circle, draw, line width=0.7pt, minimum size=0.40cm,
               inner sep=0pt, font=\sffamily\fontsize{5.5}{6}\selectfont\bfseries},
    lift/.style={ag, fill=liftcol!50, draw=liftcol!70!black},
    sens/.style={ag, fill=senscol!50, draw=senscol!70!black},
    % Titles
    ptitle/.style={font=\sffamily\fontsize{7.5}{9}\selectfont\bfseries},
    stxt/.style={font=\sffamily\fontsize{5.5}{6.5}\selectfont, text=black!60},
    mtxt/.style={font=\sffamily\fontsize{5}{6}\selectfont\itshape, text=black!50},
]

% ══════════════════════════════════════════════════════════════
% (a)  Morton Z-Order  ·  4×4 example
% ══════════════════════════════════════════════════════════════
\node[ptitle, anchor=south west] at (-0.2, 3.65)
    {(a)\enspace Morton Z-Order};

% ── Grid cells  (row, col) → Z-index ──
\foreach \r/\c/\z in {
    0/0/0,  0/1/1,  0/2/4,  0/3/5,
    1/0/2,  1/1/3,  1/2/6,  1/3/7,
    2/0/8,  2/1/9,  2/2/12, 2/3/13,
    3/0/10, 3/1/11, 3/2/14, 3/3/15}
{   \node[gc] (c\r\c) at (\c*0.82, 2.8-\r*0.82) {\z}; }

% ── Z-curve (thin, background) ──
\begin{scope}[on background layer]
\draw[edgecol!30, line width=0.6pt,
      dash pattern=on 2.5pt off 1.5pt,
      rounded corners=0.6pt]
    (c00.center) -- (c01.center) -- (c10.center) -- (c11.center)
    -- (c02.center) -- (c03.center) -- (c12.center) -- (c13.center)
    -- (c20.center) -- (c21.center) -- (c30.center) -- (c31.center)
    -- (c22.center) -- (c23.center) -- (c32.center) -- (c33.center);
\end{scope}

% ── Highlight L₁'s Hamming neighbours ──
\begin{scope}[on background layer]
\node[gc, fill=hilight] at (c01.center) {1};   % L₁
\node[gc, fill=hilight!60] at (c11.center) {3}; % S₁ (d=1)
\node[gc, fill=hilight!30] at (c30.center) {10}; % S₂ (d=2)
\end{scope}

% ── Agents ──
\node[lift] (aL1) at (c01.center) {L\textsubscript{1}};
\node[sens] (aS1) at (c11.center) {S\textsubscript{1}};
\node[lift] (aL2) at (c22.center) {L\textsubscript{2}};
\node[sens] (aS2) at (c30.center) {S\textsubscript{2}};

% ── Adjacency edges from L₁  (width ∝ attention weight) ──
\draw[mortedge, line width=1.6pt, opacity=0.7, ->, >=Stealth]
    (aL1.south) -- (aS1.north);  % d_H=1, w=.368
\draw[mortedge, line width=0.9pt, opacity=0.5, ->, >=Stealth]
    (aL1.south west) .. controls +(-0.3,-0.7) and +(0.3,0.5) .. (aS2.north east);
\draw[mortedge, line width=0.4pt, opacity=0.35, ->, >=Stealth]
    (aL1.south east) .. controls +(0.5,-0.5) and +(-0.3,0.5) .. (aL2.north west);

% ══════════════════════════════════════════════════════════════
% (b)  Hamming Neighbour Selection  (K=4)
% ══════════════════════════════════════════════════════════════
\node[ptitle, anchor=south west] at (3.8, 3.65)
    {(b)\enspace Hamming Neighbours\; ($K{=}4$)};

\node[stxt, anchor=west, font=\sffamily\fontsize{5.5}{6.5}\selectfont\bfseries] at (4.0, 3.15)
    {Z-codes ($Q{=}16$, 4-bit):};

% Agent codes table
\node[lift, minimum size=0.30cm] at (4.2, 2.70) {\tiny L\textsubscript{1}};
\node[stxt, anchor=west, font=\sffamily\fontsize{6}{7}\selectfont]
    at (4.5, 2.70) {\texttt{0001}\enspace(Z{=}1)};

\node[sens, minimum size=0.30cm] at (4.2, 2.35) {\tiny S\textsubscript{1}};
\node[stxt, anchor=west, font=\sffamily\fontsize{6}{7}\selectfont]
    at (4.5, 2.35) {\texttt{00\textbf{1}1}\enspace(Z{=}3)};

\node[lift, minimum size=0.30cm] at (4.2, 2.00) {\tiny L\textsubscript{2}};
\node[stxt, anchor=west, font=\sffamily\fontsize{6}{7}\selectfont]
    at (4.5, 2.00) {\texttt{\textbf{11}0\textbf{0}}\enspace(Z{=}12)};

\node[sens, minimum size=0.30cm] at (4.2, 1.65) {\tiny S\textsubscript{2}};
\node[stxt, anchor=west, font=\sffamily\fontsize{6}{7}\selectfont]
    at (4.5, 1.65) {\texttt{\textbf{1}0\textbf{1}0}\enspace(Z{=}10)};

% Distance table
\node[stxt, anchor=west, font=\sffamily\fontsize{5.5}{6.5}\selectfont\bfseries] at (4.0, 1.15)
    {Hamming distances from L\textsubscript{1}\,:};

\node[stxt, anchor=north west] at (4.0, 0.90) {%
    \renewcommand{\arraystretch}{1.15}%
    \begin{tabular}{|l|c|c|}
    \hline
    & $d_H$ & $w_j{=}e^{-d_H}$ \\
    \hline
    S\textsubscript{1} & 1 & .368 \\
    \hline
    S\textsubscript{2} & 2 & .135 \\
    \hline
    L\textsubscript{2} & 3 & .050 \\
    \hline
    \end{tabular}};

% ══════════════════════════════════════════════════════════════
% (c)  Blackboard Modes  ·  bb0 – bb5
% ══════════════════════════════════════════════════════════════
\node[ptitle, anchor=south west] at (-0.2, -0.85)
    {(c)\enspace Blackboard Modes};

% --- helper y-levels ---
\def\bbLabelY{-1.25}
\def\bbSubY{-1.50}
\def\bbAgentY{-2.00}

% ── bb0  Isolated ──
\def\bx{0.5}
\node[stxt, font=\sffamily\fontsize{5.5}{6.5}\selectfont\bfseries]
    at (\bx, \bbLabelY) {bb0};
\node[stxt] at (\bx, \bbSubY) {Isolated};
\node[lift, minimum size=0.32cm] at (\bx-0.3, \bbAgentY) {\tiny L};
\node[sens, minimum size=0.32cm] at (\bx,     \bbAgentY) {\tiny S};
\node[lift, minimum size=0.32cm] at (\bx+0.3, \bbAgentY) {\tiny L};

% ── bb1  Morton(L) ──
\def\bx{1.8}
\node[stxt, font=\sffamily\fontsize{5.5}{6.5}\selectfont\bfseries]
    at (\bx, \bbLabelY) {bb1};
\node[stxt] at (\bx, \bbSubY) {Morton(L)};
\node[lift, minimum size=0.32cm] (b1a) at (\bx-0.3, \bbAgentY) {\tiny L};
\node[sens, minimum size=0.32cm]       at (\bx,     \bbAgentY) {\tiny S};
\node[lift, minimum size=0.32cm] (b1b) at (\bx+0.3, \bbAgentY) {\tiny L};
\draw[mortedge, line width=0.6pt, <->]
    (b1a.north) to[out=60,in=120] (b1b.north);

% ── bb2  Morton(All) ──
\def\bx{3.2}
\node[stxt, font=\sffamily\fontsize{5.5}{6.5}\selectfont\bfseries]
    at (\bx, \bbLabelY) {bb2};
\node[stxt] at (\bx, \bbSubY) {Morton(All)};
\node[lift, minimum size=0.32cm] (b2a) at (\bx-0.45, \bbAgentY) {\tiny L};
\node[sens, minimum size=0.32cm] (b2b) at (\bx-0.15, \bbAgentY) {\tiny S};
\node[lift, minimum size=0.32cm] (b2c) at (\bx+0.15, \bbAgentY) {\tiny L};
\node[sens, minimum size=0.32cm] (b2d) at (\bx+0.45, \bbAgentY) {\tiny S};
% adjacent arcs (short)
\draw[mortedge, line width=0.5pt, <->]
    (b2a.north) to[out=55,in=125, looseness=0.9] (b2b.north);
\draw[mortedge, line width=0.5pt, <->]
    (b2b.north) to[out=55,in=125, looseness=0.9] (b2c.north);
\draw[mortedge, line width=0.5pt, <->]
    (b2c.north) to[out=55,in=125, looseness=0.9] (b2d.north);
% cross arcs (tall)
\draw[mortedge, line width=0.5pt, <->]
    (b2a.north) to[out=70,in=110, looseness=1.5] (b2c.north);
\draw[mortedge, line width=0.5pt, <->]
    (b2b.north) to[out=70,in=110, looseness=1.5] (b2d.north);

% ── bb3  KNN(L) ──
\def\bx{4.7}
\node[stxt, font=\sffamily\fontsize{5.5}{6.5}\selectfont\bfseries]
    at (\bx, \bbLabelY) {bb3};
\node[stxt] at (\bx, \bbSubY) {KNN(L)};
\node[lift, minimum size=0.32cm] (b3a) at (\bx-0.3, \bbAgentY) {\tiny L};
\node[sens, minimum size=0.32cm]       at (\bx,     \bbAgentY) {\tiny S};
\node[lift, minimum size=0.32cm] (b3b) at (\bx+0.3, \bbAgentY) {\tiny L};
\draw[knnedge, line width=0.6pt, dashed, <->]
    (b3a.north) to[out=60,in=120] (b3b.north);

% ── bb4  KNN(All) ──
\def\bx{6.1}
\node[stxt, font=\sffamily\fontsize{5.5}{6.5}\selectfont\bfseries]
    at (\bx, \bbLabelY) {bb4};
\node[stxt] at (\bx, \bbSubY) {KNN(All)};
\node[lift, minimum size=0.32cm] (b4a) at (\bx-0.45, \bbAgentY) {\tiny L};
\node[sens, minimum size=0.32cm] (b4b) at (\bx-0.15, \bbAgentY) {\tiny S};
\node[lift, minimum size=0.32cm] (b4c) at (\bx+0.15, \bbAgentY) {\tiny L};
\node[sens, minimum size=0.32cm] (b4d) at (\bx+0.45, \bbAgentY) {\tiny S};
% adjacent arcs (short)
\draw[knnedge, line width=0.5pt, dashed, <->]
    (b4a.north) to[out=55,in=125, looseness=0.9] (b4b.north);
\draw[knnedge, line width=0.5pt, dashed, <->]
    (b4b.north) to[out=55,in=125, looseness=0.9] (b4c.north);
\draw[knnedge, line width=0.5pt, dashed, <->]
    (b4c.north) to[out=55,in=125, looseness=0.9] (b4d.north);
% cross arcs (tall)
\draw[knnedge, line width=0.5pt, dashed, <->]
    (b4a.north) to[out=70,in=110, looseness=1.5] (b4c.north);
\draw[knnedge, line width=0.5pt, dashed, <->]
    (b4b.north) to[out=70,in=110, looseness=1.5] (b4d.north);

% ── bb5  Global ──
\def\bx{7.5}
\node[stxt, font=\sffamily\fontsize{5.5}{6.5}\selectfont\bfseries]
    at (\bx, \bbLabelY) {bb5};
\node[stxt] at (\bx, \bbSubY) {Global};
\begin{scope}[on background layer]
\draw[draw=gridln, fill=gridfl, rounded corners=2pt]
    ({\bx-0.42}, {\bbAgentY-0.30}) rectangle ({\bx+0.42}, {\bbAgentY+0.30});
\end{scope}
\node[lift, minimum size=0.26cm] at ({\bx-0.15}, {\bbAgentY+0.10}) {\tiny L};
\node[sens, minimum size=0.26cm] at ({\bx+0.15}, {\bbAgentY+0.10}) {\tiny S};
\node[lift, minimum size=0.26cm] at ({\bx-0.15}, {\bbAgentY-0.14}) {\tiny L};
\node[sens, minimum size=0.26cm] at ({\bx+0.15}, {\bbAgentY-0.14}) {\tiny S};

% ── Legend (beside panel c title) ──
\node[stxt, anchor=west] at (3.5, -0.85) {%
    \tikz[baseline=-0.3ex]{\draw[mortedge, line width=0.6pt, <->] (0,0)--(0.35,0);}
    \,Morton\quad
    \tikz[baseline=-0.3ex]{\draw[knnedge, line width=0.6pt, dashed, <->] (0,0)--(0.35,0);}
    \,KNN};

\end{tikzpicture}
\end{document}
"""


if __name__ == "__main__":
    outdir = os.path.dirname(__file__)

    for name, gen in [
        ("fig_architecture", generate_architecture_figure),
        ("fig_morton_topo", generate_topology_figure),
    ]:
        path = os.path.join(outdir, f"{name}.tex")
        with open(path, "w") as f:
            f.write(gen())
        print(f"Generated: {path}")

    print("\nCompile: pdflatex fig_architecture.tex && pdflatex fig_morton_topo.tex")
