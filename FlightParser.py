
from flask import Flask, render_template, request, send_file
import io
import plotly.graph_objects as go
import plotly.offline as po

app = Flask(__name__)

def extract_records(lines, ssr_code):

    #gets lines that have flight data and the ssr_code entered by user
    matches = [
        line for line in lines
        if line.startswith("T") and line[44:48] == ssr_code
    ]

    #appends each line from the search result to display in result
    parsed = []
    for line in matches:
        parsed.append({
            "SSR": line[44:48],
            "Time": line[7:19].strip(),
            "Track": line[29:34].strip(),
            "Level": line[51:54].strip(),
            "X": line[75:82].strip(),
            "Y": line[83:92].strip()
        })

    return parsed


@app.route("/", methods=["GET", "POST"])
def index():
    #gets inputs
    if request.method == "POST":
        ssr_code = request.form.get("ssr")
        file = request.files.get("file")

        #errors
        if not file:
            return render_template("index.html", error="Please upload a file.")

        if len(ssr_code) != 4:
            return render_template("index.html", error="SSR code must be 4 characters.")

        #reads file into lines
        lines = file.read().decode("utf-8").splitlines()

        #calls extract_records on the lines
        records = extract_records(lines, ssr_code)

        if not records:
            return render_template("index.html", error=f"No records found for SSR {ssr_code}")


        graph_html = make_flight_path(records)
        return render_template("index.html", records=records, ssr=ssr_code, graph=graph_html)   

    return render_template("index.html")

def make_flight_path(records):
    #extracts coordiantes as floats
    xs = [float(r["X"]) for r in records]
    ys = [float(r["Y"]) for r in records]

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=xs,
        y=ys,
        mode="lines+markers",
        line=dict(color="blue"),
        marker=dict(size=6),
        name="Flight Path"
    ))

    fig.update_layout(
        title="Flight Path (X/Y Coordinates)",
        xaxis_title="X Coordinate",
        yaxis_title="Y Coordinate",
        width=700,
        height=500
    )

    #return HTML <div> containing the graph
    return po.plot(fig, output_type="div", include_plotlyjs=False)


if __name__ == "__main__":
    app.run(debug=True)
