from flask import Flask, render_template, request, session
import csv
 
app = Flask(__name__)
app.secret_key = "152309410129743"

file_path = 'data/cpu_agenda.csv'
 
@app.route("/")
def home():
    return render_template("index.html")
 
@app.route("/submit", methods=["POST"])
def submit():
    name_selected = request.form.get("name")
    day_selected = request.form.get("day")
    session["name"] = name_selected
    session["day"] = day_selected
    date = False

    name = session["name"]
    day = session["day"]    
 
    html = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
        <meta charset="UTF-8">
        <title>Results</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
 
        <style>
            body {{
                margin: 0;
                padding: 40px;
                min-height: 100vh;
                background: linear-gradient(120deg, #0f2027, #203a43, #2c5364);
                background-size: 300% 300%;
                animation: bgMove 12s ease infinite;
                color: white;
                font-family: Segoe UI, sans-serif;
            }}
    
            @keyframes bgMove {{
                0% {{ background-position: 0% 50%; }}
                50% {{ background-position: 100% 50%; }}
                100% {{ background-position: 0% 50%; }}
            }}
    
            h1 {{
                text-align: center;
                font-size: 3rem;
                margin-bottom: 40px;
                margin-top: 70px;
                letter-spacing: 2px;
            }}
    
            .entry {{
                background: rgba(255,255,255,0.12);
                backdrop-filter: blur(10px);
                border-radius: 16px;
                padding: 20px 24px;
                margin-bottom: 20px;
                box-shadow: 0 15px 35px rgba(0,0,0,0.3);
                animation: slideUp 0.6s ease forwards;
            }}
    
            @keyframes slideUp {{
                from {{
                    opacity: 0;
                    transform: translateY(30px);
                }}
                to {{
                    opacity: 1;
                    transform: translateY(0);
                }}
            }}
    
            .meta {{
                opacity: 0.8;
                margin-bottom: 8px;
            }}
    
            .arrow {{
                display: inline-block;
                animation: pulseArrow 1.5s infinite;
            }}
    
            @keyframes pulseArrow {{
                0%,100% {{ transform: translateX(-2px); opacity: 0.6; }}
                50% {{ transform: translateX(4px); opacity: 1; }}
            }}

            .back-btn {{
                margin-top: 500px;
                position: fixed;
                bottom: 20px;
                left: 20px;
                width: 12.5%;
                padding: 12px;
                border-radius: 30px;
                border: none;
                font-size: 15px;
                cursor: pointer;
                color: #fff;
                background: linear-gradient(135deg, #36d1dc, #5b86e5);
                box-shadow: 0 8px 20px rgba(0,0,0,0.25);
                transition: transform 0.2s ease, box-shadow 0.2s ease;
            }}

            .back-btn:hover {{
                transform: translateY(-2px);
                box-shadow: 0 12px 30px rgba(0,0,0,0.35);
            }}

            .back-btn:active {{
                transform: scale(0.97);
            }}

            .day-nav {{
                position: fixed;
                top: 20px;
                left: 50%;
                transform: translateX(-50%);
                display: flex;
                align-items: center;
                gap: 20px;
                padding: 12px 24px;
                border-radius: 40px;
                background: rgba(255,255,255,0.15);
                backdrop-filter: blur(10px);
                box-shadow: 0 10px 30px rgba(0,0,0,0.3);
                z-index: 1000;
            }}

            .day-nav span {{
                font-size: 1.3rem;
                font-weight: 600;
                letter-spacing: 1px;
            }}

            .day-nav button {{
                background: none;
                border: none;
                color: white;
                font-size: 1.6rem;
                cursor: pointer;
                transition: transform 0.2s ease, opacity 0.2s ease;
            }}

            .day-nav button:hover {{
                transform: scale(1.2);
                opacity: 0.9;
            }}
            
    </style>
        </head>
        <body>
        <div class="day-nav">
            <button onclick="changeDay(-1)">&#10094;</button>
            <span id="current-day">{day_selected}</span>
            <button onclick="changeDay(1)">&#10095;</button>
        </div>

        <h1>{session.get("name")}</h1>
        """

    for line in csv.reader(open("data/cpu_agenda.csv")):
        if line[0] == 'Status':
            if line[3].strip().lower() == day.strip().lower():
                date = True
            else:
                date = False 
        for i in line:
            if i != '' and line[0] == '' and date and line[4].strip().lower() == name.strip().lower():
                html += f"""
                    <div style="text-align: center;" class="entry">
                        <div class="meta">{line[2]}, {line[3]}</div>
                        <div>
                            {line[5]}
                            <span class="arrow">&#10230;</span>
                            {line[6]}
                        </div>
                    </div>
                    """
                break
    html += """
    <button type="button" class="back-btn" onclick="history.back()">⬅ Back</button>
    </body>
    <script>
        const days = ["monday", "tuesday", "wednesday", "thursday", "friday"];
        let currentDay = "{day_selected}".toLowerCase();

        function changeDay(direction) {
            let index = days.indexOf(currentDay);
            index = (index + direction + days.length) % days.length;
            const newDay = days[index];

            // Make a POST request via fetch to update session, then reload
            fetch("/change_day", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ day: newDay })
            }).then(() => window.location.reload());
        }
    </script>
    </html>
    """
    return html
 
@app.route("/change_day", methods=["POST"])
def change_day():
    data = request.get_json()
    new_day = data.get("day")
    if new_day:
        session["day"] = new_day
    return "", 204
       
 
if __name__ == "__main__":
    app.run(debug=True)