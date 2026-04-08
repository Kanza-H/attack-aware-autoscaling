# Demo website (storefront)

This is the **microservice website** that calls the Gateway. Use it to show Normal vs Blocking.

## Run it

1. Start the backend (Catalog + Gateway). Example:
   ```powershell
   cd ..   # project root
   py run_demo.py
   ```
   (Or start Catalog and Gateway in separate terminals.)

2. Serve this folder. From the **website** folder:
   ```powershell
   cd C:\Users\kanza\OneDrive\Documents\attack-aware-autoscaling\website
   py -m http.server 3000
   ```

3. Open **http://localhost:3000** in your browser.

## Demo flow

- **Normal:** The page loads and shows products. Banner says "NORMAL — Traffic allowed".
- **Blocking:** In the Streamlit dashboard, click "Set API: Blocking". Refresh the website (or click Refresh). The page will show "429 Rate limited" and the banner will say "BLOCKING — Attack defence active". So you're showing a real site that stops serving when defence is on.
- **Back to Normal:** In the dashboard click "Set API: Normal". Refresh the website — products load again.

This is the "actual microservice website" that demonstrates how the API blocking and normal modes work.
