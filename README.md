# EduPro Instructor Performance Dashboard

## Folder Structure
```
dashboard/
├── app.py
├── requirements.txt
├── data/
│   ├── Teachers.csv
│   ├── Courses.csv
│   └── Transactions.csv
└── README.md
```

## How to Run (on your local computer)

1. Keep the entire `dashboard` folder on your computer as-is (don't change the structure — the `data/` folder must stay inside it).

2. Open Terminal/Command Prompt and navigate to the folder:
   ```
   cd path/to/dashboard
   ```

3. Install the requirements:
   ```
   pip install -r requirements.txt
   ```

4. Run the dashboard:
   ```
   streamlit run app.py
   ```

5. It will open automatically in your browser (if not, open the `http://localhost:8501` link shown in the terminal).

   > **Windows tip:** If you get `'streamlit' is not recognized`, use this instead:
   > ```
   > python -m pip install -r requirements.txt
   > python -m streamlit run app.py
   > ```

## Running in Google Colab (optional)

Streamlit doesn't run directly inside Colab notebook cells. If you need to, you can use:
```python
!pip install streamlit -q
!wget -q -O - ipv4.icanhazip.com   # note your IP
!streamlit run app.py & npx localtunnel --port 8501
```
But the easiest and most reliable way is to run it locally on your laptop/PC.

## Deploying (free, to share a public link)

On [share.streamlit.io](https://share.streamlit.io) (Streamlit Community Cloud):
1. Push this `dashboard` folder to a GitHub repo (including the data files)
2. Log in to share.streamlit.io using your GitHub account
3. Connect the repo and select `app.py` as the main file
4. Click Deploy — you'll get a free public link

## Updating the Data

If you want to use new data, simply replace the three CSV files inside `data/` (keep the same filenames: `Teachers.csv`, `Courses.csv`, `Transactions.csv`) — or, once the app is open, use the "Upload my own CSV files" checkbox in the sidebar to upload directly.