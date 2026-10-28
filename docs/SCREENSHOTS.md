# Capturing genuine application screenshots

The repository currently does not contain verified UI screenshots captured from a running application. Capture these from the actual application rather than using mockups or generated images.

1. Install dependencies and launch from the repository root with `streamlit run app.py`.
2. Wait for the selected symbol's data and charts to finish loading.
3. Use a consistent browser viewport (for example, 1440 × 900) and hide browser developer tools.
4. Capture each page below and save the PNG files in this folder.

Recommended filenames:

- `01-live-market.png`
- `02-technical-analysis.png`
- `03-predictions.png`
- `04-risk-analysis.png`
- `05-model-performance.png`

Capture checklist:

- Show the dashboard navigation and page title.
- Use AAPL or another symbol with an available local model artifact.
- Ensure charts have loaded; do not use loading spinners, stack traces, or empty states as the primary product image.
- Remove personal information and API credentials from the frame.
- Recheck screenshots after material UI changes.

After capturing, embed the most informative two or three images in the root README using relative Markdown image paths. Keep each screenshot compressed and focused on the application itself.
