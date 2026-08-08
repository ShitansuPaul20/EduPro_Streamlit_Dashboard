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

## Kaise chalayein (Local computer pe)

1. Is poori `dashboard` folder ko apne computer pe rakho (structure mat badlo — `data/` folder andar hi hona chahiye).

2. Terminal/Command Prompt kholo, folder mein jao:
   ```
   cd path/to/dashboard
   ```

3. Requirements install karo:
   ```
   pip install -r requirements.txt
   ```

4. Dashboard run karo:
   ```
   streamlit run app.py
   ```

5. Browser mein automatically khul jayega (agar nahi khule, toh terminal mein diya gaya `http://localhost:8501` link kholo).

## Google Colab mein chalana ho toh (optional)

Colab mein Streamlit directly nahi chalta. Agar zaroorat pade toh:
```python
!pip install streamlit -q
!wget -q -O - ipv4.icanhazip.com   # apna IP note karo
!streamlit run app.py & npx localtunnel --port 8501
```
Lekin sabse aasan tarika hai apne laptop/PC pe local run karna.

## Deploy karna ho (free, sabko link se dikhana ho)

[share.streamlit.io](https://share.streamlit.io) (Streamlit Community Cloud) pe:
1. Is `dashboard` folder ko GitHub repo mein daal do (data files sahit)
2. share.streamlit.io pe login karo (GitHub se)
3. Repo connect karo, `app.py` select karo
4. Deploy — free public link mil jayega

## Data Update karni ho

Agar naya data use karna hai, bas `data/` folder ki teeno CSV files replace kar do (same naam rakhna: `Teachers.csv`, `Courses.csv`, `Transactions.csv`) — ya app khulne ke baad sidebar mein "Upload my own CSV files" checkbox se directly upload kar sakte ho.
