from flask import Flask, render_template_string, request, redirect, session
import requests, threading

app = Flask(__name__)
app.secret_key = "alshifa-final-2026"

ULTRA_INSTANCE = "instance110839"
ULTRA_TOKEN = "c8a9v7x5k2"
MY_CONTACT_NUMBER = "923001234567"

patients_db = []
current_token = {"Dr. Ahmed": 1000, "Dr. Sara": 1000, "Dr. Ali": 1000}
token_counter = 1000

def send_whatsapp(phone, text):
    if ULTRA_INSTANCE == "instance110839":
        print(f"DEMO MSG to {phone}: {text}")
        return True
    try:
        url = f"https://api.ultramsg.com/{ULTRA_INSTANCE}/messages/chat"
        requests.post(url, data={"token": ULTRA_TOKEN, "to": phone, "body": text}, timeout=10)
        return True
    except: return False

def schedule_alerts(patient):
    threading.Timer(20, lambda: send_whatsapp(patient['phone'], f"Al-Shifa: {patient['name']} Token {patient['token']} 20 min me ane wala hai.")).start()
    threading.Timer(40, lambda: send_whatsapp(patient['phone'], f"Al-Shifa ALERT: {patient['name']} Token {patient['token']} sirf 5 min me hai!")).start()

# ====== PATIENT PORTAL (Mobile walon ke liye) ======
PATIENT_HTML = """
<!DOCTYPE html><html><head><title>Al-Shifa - Patient Portal</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>body{font-family:Arial;background:#eef2f7;padding:10px}.box{background:white;padding:20px;border-radius:14px;max-width:800px;margin:auto;box-shadow:0 4px 15px #0001}input{padding:12px;border-radius:8px;border:1px solid #ccc;width:100%}table{width:100%;border-collapse:collapse;margin-top:15px}th,td{padding:10px;border-bottom:1px solid #eee}th{background:#198754;color:white}#toast{position:fixed;top:50%;left:50%;transform:translate(-50%,-50%);background:#198754;color:white;padding:20px 30px;border-radius:12px;display:none;z-index:9999}.wa-float{position:fixed;bottom:20px;right:20px;background:#25D366;width:62px;height:62px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:34px;text-decoration:none}</style>
</head><body>
<div id="toast"></div>
<a href="https://wa.me/{{my_no}}" target="_blank" class="wa-float">💬</a>
<div class="box">
<h2>🏥 Al-Shifa - Patient Portal</h2>
<p>Apna Naam / Token Search Karein</p>
<input id="search" placeholder="Search... Ahmed / C-1001" onkeyup="filterTable()">
<table id="tbl"><tr><th>Token</th><th>Name</th><th>Doctor</th><th>Status</th><th>Now Running</th></tr>
{% for p in patients|reverse %}<tr><td>{{p.token}}</td><td>{{p.name}}</td><td>{{p.doctor}}</td><td>{{p.status}}</td><td>{{current[p.doctor]}}</td></tr>{% endfor %}
</table>
<div style="margin-top:20px;padding:12px;background:#f8f9fa;border-radius:8px"><b>Contact Us:</b> <a href="https://wa.me/{{my_no}}" target="_blank">💬 WhatsApp: {{my_no}}</a></div>
<p><a href="/reception">Reception Login?</a></p>
</div>
<script>function filterTable(){let q=document.getElementById('search').value.toLowerCase();let rows=document.getElementById('tbl').getElementsByTagName('tr');for(let i=1;i<rows.length;i++){rows[i].style.display=rows[i].innerText.toLowerCase().includes(q)?"":"none";}}</script>
</body></html>
"""

# ====== RECEPTION PORTAL (Aapke laptop ke liye) ======
RECEPTION_HTML = """
<!DOCTYPE html><html><head><title>Al-Shifa - Reception Portal</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>body{font-family:Arial;background:#eef2f7;padding:10px}.box{background:white;padding:20px;border-radius:14px;max-width:1050px;margin:auto}input,select{padding:12px;border-radius:8px;border:1px solid #ccc;width:100%;margin:6px 0}button{padding:10px 18px;border:none;border-radius:8px;background:#0d6efd;color:white}table{width:100%;border-collapse:collapse;margin-top:15px}th,td{padding:10px;border-bottom:1px solid #eee}th{background:#0d6efd;color:white}#toast{position:fixed;top:50%;left:50%;transform:translate(-50%,-50%);background:#198754;color:white;padding:20px 30px;border-radius:12px;display:none;z-index:9999;font-size:18px;text-align:center}</style>
</head><body>
<div id="toast"></div>
<div class="box">
<h2>🏥 Al-Shifa - Reception Portal (Private)</h2>
{% if not session.get('logged') %}
<form method="post" action="/login"><input name="user" placeholder="reception"><input name="pass" type="password" placeholder="admin123"><button>Login</button></form>
{% else %}
<h3>New Token Book - Auto WhatsApp</h3>
<form method="post" action="/book"><input name="name" placeholder="Patient Name" required><input name="phone" placeholder="923001234567" required><select name="doctor"><option>Dr. Ahmed</option><option>Dr. Sara</option><option>Dr. Ali</option></select><button>Book & Auto Send</button></form><hr>
<input id="search" placeholder="Search..." onkeyup="filterTable()">
<table id="tbl"><tr><th>Token</th><th>Name</th><th>Doctor</th><th>Status</th><th>Running</th><th>Next</th></tr>
{% for p in patients|reverse %}<tr><td>{{p.token}}</td><td>{{p.name}}</td><td>{{p.doctor}}</td><td>{{p.status}}</td><td>{{current[p.doctor]}}</td><td><a href="/next/{{p.doctor}}"><button>Next</button></a></td></tr>{% endfor %}
</table>
<a href="/logout">Logout</a> | <a href="/patient">Patient View Dekho</a>
{% endif %}
</div>
<script>function filterTable(){let q=document.getElementById('search').value.toLowerCase();let rows=document.getElementById('tbl').getElementsByTagName('tr');for(let i=1;i<rows.length;i++){rows[i].style.display=rows[i].innerText.toLowerCase().includes(q)?"":"none";}}
function showToast(m){let t=document.getElementById('toast');t.innerText=m;t.style.display='block';setTimeout(()=>{t.style.display='none'},5000);}
{% if toast %}showToast("{{toast}}");{% endif %}
</script>
</body></html>
"""

@app.route("/")
def home():
    # Auto Detect: Mobile hai to Patient portal par bhejo
    ua = request.headers.get('User-Agent','').lower()
    is_mobile = 'android' in ua or 'iphone' in ua or 'mobile' in ua
    if is_mobile:
        return redirect("/patient")
    return render_template_string(PATIENT_HTML, patients=patients_db, current=current_token, my_no=MY_CONTACT_NUMBER)

@app.route("/patient")
def patient_portal():
    return render_template_string(PATIENT_HTML, patients=patients_db, current=current_token, my_no=MY_CONTACT_NUMBER)

@app.route("/reception")
def reception_portal():
    return render_template_string(RECEPTION_HTML, patients=patients_db, current=current_token, toast=request.args.get("toast",""))

@app.route("/login", methods=["POST"])
def login():
    if request.form.get("user")=="reception" and request.form.get("pass")=="admin123":
        session["logged"]=True
    return redirect("/reception")

@app.route("/book", methods=["POST"])
def book():
    global token_counter
    token_counter+=1
    token=f"C-{token_counter}"
    name=request.form.get("name"); phone=request.form.get("phone"); doctor=request.form.get("doctor")
    patient={"token":token,"name":name,"phone":phone,"doctor":doctor,"status":"Waiting"}
    patients_db.append(patient)
    send_whatsapp(phone, f"Assalam o Alaikum {name}, Al-Shifa: Token {token} book hogaya. Doctor {doctor}. Abhi Token {current_token[doctor]} chal raha hai.")
    schedule_alerts(patient)
    return redirect(f"/reception?toast=Token {token} ko WhatsApp chala gaya hai ✅")

@app.route("/next/<doctor>")
def next_q(doctor):
    current_token[doctor]+=1
    for p in patients_db:
        if p["doctor"]==doctor and p["status"]=="Waiting":
            p["status"]="Next - 20 min"
            send_whatsapp(p["phone"], f"Al-Shifa: {p['name']} Token {p['token']} 20 min me ane wala hai.")
            break
    return redirect(f"/reception?toast={doctor} ka Next - Alert bhej diya ✅")

@app.route("/logout")
def logout():
    session.clear(); return redirect("/reception")

if __name__=="__main__":
    app.run(host="0.0.0.0", port=5000)
