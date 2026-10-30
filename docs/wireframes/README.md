# Wireframes · Swing Trading Dashboard

A low-fidelity, clickable wireframe of the dashboard. It goes with [PRD v1.2](../03-prd.md) and uses sample data only (the tickers are fictional).

| File | What it is |
| --- | --- |
| [prototype.html](prototype.html) | Clickable prototype in a single self-contained file. It needs no network or build step: download it and open it in any browser. |
| [dashboard.png](dashboard.png) | Main page at release v1.0, default parameters, all modules OK |
| [momentum-screen-b.png](momentum-screen-b.png) | Momentum Screen B (RS + Ichimoku, weekly): New and Pending signals grouped by sector, with entry at the signal candle high and exit at its low ([Spec 4](../04-signal-spec/04-rs-ichimoku.md)) |
| [value-long-term.png](value-long-term.png) | Value – Long Term: options, interest coverage, 10-year growth, PEG and Debt/EBITDA rules, largest market cap first ([Spec 1](../04-signal-spec/01-value-long-term.md)) |
| [archive.png](archive.png) | Snapshot archive: open a past refresh by date |
| [states.png](states.png) | One section in six states (ok, partial, unavailable, fewer than 3, coming soon, risk-off) |

GitHub shows the HTML file as source code rather than running it. To try the prototype, download the file (**Raw → Save as**) and open it locally.

## Using the prototype

The dark bar at the top holds the **prototype controls**. They aren't part of the product; they let you switch scenarios:

- **Dashboard / Archive / States**: switch screens. You can also open a screen directly with `#dashboard`, `#archive` or `#states` at the end of the address.
- **Release**: `v0.1 MVP`, `v0.2`, `v0.3` or `v1.0`. Unbuilt sections show "Coming soon", so you can compare the week-6 MVP with the full product.
- **Module status**: set each module to `ok`, `partial`, `unavailable` or `fewer than 3`.
- **Regime, FOMC flag, Market holiday**: show the matching banners and warnings.

These parts of the page itself respond to clicks and typing:

- Momentum Screen A / B tabs and the PE Re-rating list tabs
- **Stock selection parameters**: market cap at least ($B), plus Screen A's RS minimum, PE change % and Value – Long Term's PEG limit in each section's parameter panel. Screen B responds to the market-cap filter only; its RS length field is shown but not wired. Tables, tab counts and empty states update as you type.
- **Position sizing**: Capital ($) and Risk per trade (%). Entry, Exit (SL) and Quantity recalculate, and positions larger than capital are flagged.
- Hovering an underlined indicator or market tile shows a plain-language definition.
- The Archive link and snapshot list

Fields marked *not wired in wireframe* show the intended control but don't change the sample data.

## Screen to requirement map

| Area | PRD requirements |
| --- | --- |
| Page order, coming-soon sections | DASH-FR-02 |
| FOMC / jobs flag, Economic Data table, yield curve | ECON-FR-01 to 08 |
| Hover definitions | DASH-FR-07, NFR-12 |
| "Since your last visit" strip | DASH-FR-05 |
| COT placeholder | COT-FR-01 |
| Regime banner with DXY and MOVE | REG-FR-01, REG-FR-02 |
| Sector rotation chart and table | SECT-FR-01, SECT-FR-02 |
| Stock selection parameters | PARAM-FR-01 to 06 |
| Momentum screens, entry / exit / quantity, sizing inputs | MOM-FR-01 to 07 (Screen B per PRD v1.2 and Spec 4) |
| Value · PE Re-rating | PER-FR-01 to 05 |
| Value · Long Term | VLT-FR-01 to 05 |
| Earnings flags | EARN-FR-01 |
| Confluence list | CONF-FR-01 |
| Past-picks tracker | TRACK-FR-01 |
| AI summary, "why flagged" | AI-FR-01 to 03 |
| Section states | PLAT-FR-02, PLAT-FR-06, PLAT-FR-07, MOM-FR-05 |
| Archive, snapshot details, disclaimer | ARCH-FR-01, ARCH-FR-02, ARCH-FR-04, NFR-14 |

## Notes

- All numbers are sample values for layout only. The real formulas and thresholds belong in `docs/04-signal-spec.md`.
- The rotation chart uses our own RS-Ratio / RS-Momentum, defined in the signal spec (Q12). It doesn't use the proprietary "RRG" or "JdK" names.
- $50,000 at 1% is a sample sizing default. Real capital is never committed (NFR-15).
- A Figma redraw will go in `docs/wireframes/figma/` later.

*Personal research project, not investment advice.*
