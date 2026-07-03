const styles = `
  @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;600;700;900&family=Crimson+Text:ital,wght@0,400;0,600;1,400&display=swap');

  * { box-sizing: border-box; margin: 0; padding: 0; }

  :root {
    --ink:        #0a0908;   /* near-black stage */
    --panel:      #150f08;   /* raised panel / box */
    --brass:      #c9a227;   /* muted antique gold — primary accent */
    --brass-hi:   #e8c95a;   /* brighter brass for hover states */
    --parchment:  #e9dcc3;   /* body text */
    --parchment-dim: #8c7c5e; /* secondary / muted text */
    --line:       #2c2213;   /* hairline borders */
    --garnet:     #9c4a3e;   /* sign-out / danger accent */
  }

  body {
    background: var(--ink);
    color: var(--parchment);
    font-family: 'Crimson Text', serif;
  }

  @media (prefers-reduced-motion: reduce) {
    *, *::before, *::after {
      animation-duration: 0.001ms !important;
      animation-iteration-count: 1 !important;
      transition-duration: 0.001ms !important;
    }
  }

  /* ---------- Menu ---------- */

  .menu-root {
    min-height: 100vh;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    position: relative;
    overflow: hidden;
    background: radial-gradient(ellipse at 50% 0%, #1c1408 0%, var(--ink) 72%);
    padding: 2rem 1.5rem;
  }

  /* faint engraved board grid across the whole stage */
  .menu-root::before {
    content: '';
    position: absolute;
    inset: 0;
    background-image:
      linear-gradient(rgba(201,162,39,0.035) 1px, transparent 1px),
      linear-gradient(90deg, rgba(201,162,39,0.035) 1px, transparent 1px);
    background-size: 64px 64px;
    pointer-events: none;
  }

  /* signature element: an oversized, near-invisible knight watermark
     anchored to the corner — reads as engraved stone, not decoration */
  .menu-root::after {
    content: '♞';
    position: absolute;
    right: -4rem;
    bottom: -6rem;
    font-size: 34rem;
    line-height: 1;
    color: rgba(201,162,39,0.035);
    pointer-events: none;
    user-select: none;
  }

  .chess-crown {
    font-size: 3.6rem;
    margin-bottom: 0.5rem;
    filter: drop-shadow(0 0 22px rgba(201,162,39,0.45));
    animation: float 3.2s ease-in-out infinite;
    position: relative;
    z-index: 1;
  }

  @keyframes float {
    0%, 100% { transform: translateY(0px); }
    50% { transform: translateY(-8px); }
  }

  .game-title {
    font-family: 'Cinzel', serif;
    font-size: clamp(2.4rem, 6vw, 3.4rem);
    font-weight: 900;
    letter-spacing: 0.14em;
    color: var(--brass);
    text-shadow: 0 0 30px rgba(201,162,39,0.35), 0 2px 0 #6b5416;
    margin-bottom: 0.3rem;
    text-align: center;
    position: relative;
    z-index: 1;
  }

  .game-subtitle {
    font-family: 'Crimson Text', serif;
    font-style: italic;
    font-size: 1.05rem;
    color: var(--parchment-dim);
    letter-spacing: 0.32em;
    margin-bottom: 2.75rem;
    text-align: center;
    position: relative;
    z-index: 1;
  }

  .divider {
    width: 180px;
    height: 1px;
    background: linear-gradient(90deg, transparent, var(--brass), transparent);
    margin: 0 auto 2.5rem;
    position: relative;
    z-index: 1;
  }

  /* small inlay diamond at the divider's center, echoing a board square */
  .divider::before {
    content: '';
    position: absolute;
    top: 50%;
    left: 50%;
    width: 6px;
    height: 6px;
    background: var(--brass);
    transform: translate(-50%, -50%) rotate(45deg);
    box-shadow: 0 0 8px rgba(201,162,39,0.6);
  }

  .btn-group {
    display: flex;
    flex-direction: column;
    gap: 0.9rem;
    width: min(280px, 84vw);
    position: relative;
    z-index: 1;
  }

  .btn-group.horizontal {
    flex-direction: row;
    width: auto;
    gap: 1.1rem;
    flex-wrap: wrap;
    justify-content: center;
  }

  /* ---------- Buttons ---------- */

  .btn {
    font-family: 'Cinzel', serif;
    font-size: 0.9rem;
    font-weight: 700;
    letter-spacing: 0.14em;
    padding: 0.95rem 1.9rem;
    border: none;
    cursor: pointer;
    position: relative;
    transition: transform 0.22s ease, box-shadow 0.22s ease, background 0.22s ease;
    text-transform: uppercase;
  }

  .btn:focus-visible {
    outline: 2px solid var(--brass-hi);
    outline-offset: 3px;
  }

  .btn-primary {
    background: linear-gradient(160deg, #e2bc4c 0%, #a87f22 45%, #d4af37 100%);
    color: var(--ink);
    clip-path: polygon(8px 0%, 100% 0%, calc(100% - 8px) 100%, 0% 100%);
    box-shadow: 0 4px 18px rgba(201,162,39,0.28), inset 0 1px 0 rgba(255,255,255,0.35);
  }

  .btn-primary:hover {
    transform: translateY(-2px);
    box-shadow: 0 10px 28px rgba(201,162,39,0.42), inset 0 1px 0 rgba(255,255,255,0.4);
    background: linear-gradient(160deg, #f0cd5d 0%, #b98f2c 45%, #e2bc4c 100%);
  }

  .btn-secondary {
    background: rgba(201,162,39,0.03);
    color: var(--brass);
    border: 1px solid rgba(201,162,39,0.55);
    clip-path: polygon(8px 0%, 100% 0%, calc(100% - 8px) 100%, 0% 100%);
  }

  .btn-secondary:hover {
    background: rgba(201,162,39,0.1);
    border-color: var(--brass-hi);
    transform: translateY(-2px);
    box-shadow: 0 4px 20px rgba(201,162,39,0.18);
  }

  .btn-disabled {
    background: transparent;
    color: #4a4035;
    border: 1px solid #241c10;
    clip-path: polygon(8px 0%, 100% 0%, calc(100% - 8px) 100%, 0% 100%);
    cursor: not-allowed;
    opacity: 0.5;
  }

  .btn-back {
    font-family: 'Cinzel', serif;
    font-size: 0.72rem;
    letter-spacing: 0.2em;
    color: #5f5136;
    background: none;
    border: none;
    cursor: pointer;
    margin-top: 2rem;
    text-transform: uppercase;
    transition: color 0.2s ease, gap 0.2s ease;
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }

  .btn-back:hover { color: var(--brass); gap: 0.7rem; }
  .btn-back:focus-visible { outline: 2px solid var(--brass-hi); outline-offset: 3px; }

  /* ---------- Mode selection ---------- */

  .mode-label {
    font-family: 'Cinzel', serif;
    font-size: 1.35rem;
    font-weight: 700;
    color: var(--brass);
    letter-spacing: 0.09em;
    margin-bottom: 0.7rem;
    text-align: center;
  }

  .mode-desc {
    font-family: 'Crimson Text', serif;
    font-style: italic;
    font-size: 0.95rem;
    color: var(--parchment-dim);
    margin-bottom: 2rem;
    text-align: center;
  }

  .coming-soon-badge {
    display: inline-block;
    font-family: 'Cinzel', serif;
    font-size: 0.58rem;
    letter-spacing: 0.2em;
    padding: 0.2rem 0.5rem;
    border: 1px solid #362a16;
    color: #5a4a2a;
    margin-left: 0.5rem;
    vertical-align: middle;
  }

  /* ---------- Game screen ---------- */

  .game-root {
    min-height: 100vh;
    background: radial-gradient(ellipse at 50% 0%, #1c1408 0%, var(--ink) 72%);
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 1.5rem 1rem 3rem;
  }

  .game-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: 0.75rem;
    width: 100%;
    max-width: 700px;
    padding: 0 0.5rem 1rem;
    border-bottom: 1px solid rgba(201,162,39,0.15);
    margin-bottom: 1.5rem;
  }

  .game-header-title {
    font-family: 'Cinzel', serif;
    font-size: 1.15rem;
    font-weight: 700;
    color: var(--brass);
    letter-spacing: 0.1em;
  }

  .game-header-mode {
    font-family: 'Crimson Text', serif;
    font-style: italic;
    font-size: 0.9rem;
    color: var(--parchment-dim);
  }

  .selected-info {
    font-family: 'Crimson Text', serif;
    font-style: italic;
    font-size: 1rem;
    color: #b6a582;
    margin-top: 1rem;
    letter-spacing: 0.04em;
    text-align: center;
  }

  @keyframes fadeIn {
    from { opacity: 0; transform: translateY(14px); }
    to { opacity: 1; transform: translateY(0); }
  }

  .fade-in { animation: fadeIn 0.4s ease forwards; }

  /* ---------- Promotion dialog ---------- */

  .promotion-overlay {
    position: fixed;
    inset: 0;
    background: rgba(5, 4, 2, 0.88);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 100;
    animation: fadeIn 0.2s ease forwards;
    padding: 1.5rem;
  }

  .promotion-box {
    background: var(--panel);
    border: 1px solid var(--brass);
    padding: 2rem 2.25rem;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 1.4rem;
    box-shadow: 0 0 70px rgba(201,162,39,0.16), inset 0 0 0 1px rgba(201,162,39,0.08);
    position: relative;
  }

  /* brass corner ticks — echoes the clip-path notch used on buttons */
  .promotion-box::before,
  .promotion-box::after {
    content: '';
    position: absolute;
    width: 14px;
    height: 14px;
    border: 1px solid var(--brass);
  }
  .promotion-box::before { top: -1px; left: -1px; border-right: none; border-bottom: none; }
  .promotion-box::after  { bottom: -1px; right: -1px; border-left: none; border-top: none; }

  .promotion-title {
    font-family: 'Cinzel', serif;
    font-size: 1.05rem;
    font-weight: 700;
    color: var(--brass);
    letter-spacing: 0.22em;
    text-transform: uppercase;
  }

  .promotion-pieces {
    display: flex;
    gap: 0.9rem;
    flex-wrap: wrap;
    justify-content: center;
  }

  .promotion-piece-btn {
    background: rgba(201,162,39,0.02);
    border: 1px solid var(--line);
    cursor: pointer;
    padding: 0.75rem;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0.5rem;
    transition: background 0.2s ease, border-color 0.2s ease, transform 0.2s ease, box-shadow 0.2s ease;
    clip-path: polygon(8px 0%, 100% 0%, calc(100% - 8px) 100%, 0% 100%);
    min-width: 72px;
  }

  .promotion-piece-btn:hover,
  .promotion-piece-btn:focus-visible {
    background: rgba(201,162,39,0.12);
    border-color: var(--brass);
    transform: translateY(-4px);
    box-shadow: 0 8px 24px rgba(201,162,39,0.22);
    outline: none;
  }

  .promotion-piece-btn img {
    width: 56px;
    height: 56px;
    object-fit: contain;
  }

  .promotion-piece-btn span {
    font-family: 'Cinzel', serif;
    font-size: 0.58rem;
    color: var(--brass);
    letter-spacing: 0.2em;
    text-transform: uppercase;
  }

  /* ---------- Small screens ---------- */

  @media (max-width: 480px) {
    .chess-crown { font-size: 2.8rem; }
    .game-subtitle { letter-spacing: 0.22em; }
    .btn { padding: 0.85rem 1.4rem; font-size: 0.82rem; }
    .promotion-box { padding: 1.5rem 1.25rem; }
    .promotion-piece-btn img { width: 46px; height: 46px; }
  }
  /* ---------- Private match waiting screen ---------- */

  .waiting-spinner {
    width: 84px;
    height: 84px;
    position: relative;
  }

  .waiting-spinner-ring {
    width: 100%;
    height: 100%;
    border-radius: 50%;
    border: 2px solid rgba(201,162,39,0.15);
    border-top-color: var(--brass);
    border-right-color: var(--brass-hi);
    animation: spin 1.1s linear infinite;
  }

  @keyframes spin {
    to { transform: rotate(360deg); }
  }

  .room-code-box {
    margin-top: 2.25rem;
    background: rgba(201,162,39,0.03);
    border: 1px solid var(--line);
    padding: 1.75rem 2.25rem 1.5rem;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 1.25rem;
    clip-path: polygon(10px 0%, 100% 0%, calc(100% - 10px) 100%, 0% 100%);
  }

  .room-code-label {
    font-family: 'Cinzel', serif;
    font-size: 0.62rem;
    letter-spacing: 0.24em;
    text-transform: uppercase;
    color: var(--parchment-dim);
  }

  /* each character sits in its own tile — echoes chessboard squares
     and keeps the code visually separated from the label */
  .room-code-chip {
    display: flex;
    gap: 0.45rem;
  }

  .room-code-char {
    font-family: 'Cinzel', serif;
    font-size: 1.6rem;
    font-weight: 700;
    color: var(--brass);
    text-shadow: 0 0 16px rgba(201,162,39,0.3);
    background: rgba(201,162,39,0.05);
    border: 1px solid rgba(201,162,39,0.3);
    width: 2.4rem;
    height: 2.9rem;
    display: flex;
    align-items: center;
    justify-content: center;
    user-select: all;
  }

  /* alternate tile shading — subtle board-square rhythm */
  .room-code-char:nth-child(even) {
    background: rgba(201,162,39,0.11);
  }

  .room-code-copy-btn {
    padding: 0.55rem 1.6rem;
    font-size: 0.72rem;
    margin-top: 0.15rem;
  }

  @media (max-width: 480px) {
    .waiting-spinner { width: 64px; height: 64px; }
    .room-code-box { padding: 1.35rem 1.25rem 1.2rem; }
    .room-code-chip { gap: 0.3rem; }
    .room-code-char {
      font-size: 1.15rem;
      width: 1.9rem;
      height: 2.3rem;
    }
  }
`;

export default styles;