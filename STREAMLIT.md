Streamlit tips

- If you see a cached or stale UI, clear Streamlit cache:
  - Windows PowerShell:
    - Remove-Item -Recurse -Force "$env:USERPROFILE\.streamlit\cache" -ErrorAction SilentlyContinue
- To set secrets locally, create `.streamlit/secrets.toml` (ignored by git).
- Run from repo root:
  - streamlit run app.py
