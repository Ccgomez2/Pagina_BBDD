from flask import Flask, request, jsonify
import json
import paho.mqtt.publish as publish

app = Flask(__name__)
from flask_cors import CORS
CORS(app)

bd = {
    "pedidos": [],
    "contadores": {
        "fresa": 0, "vainilla": 0, "chocolate": 0, "defectuosos": 0
    }
}

@app.route("/pedido", methods=["POST"])
def recibir_pedido():
    data = request.json
    nombre = data.get("nombre")
    sabor = data.get("sabor")
    cantidad = data.get("cantidad")

    if not nombre or not sabor or not cantidad:
        return jsonify({"error": "Faltan campos obligatorios"}), 400

    bd["pedidos"].append({"nombre": nombre, "sabor": sabor, "cantidad": cantidad})
    bd["contadores"][sabor] += cantidad

    mensaje = json.dumps({"evento": "nuevo_pedido", "sabor": sabor, "cantidad": cantidad})
    publish.single("richi5/giirob/pr2/enviar/web", mensaje, hostname="broker.emqx.io", port=1883)

    return jsonify({"ok": True, "mensaje": "Pedido recibido"})

@app.route("/estado", methods=["GET"])
def estado():
    return jsonify({
        "pedidos": {
            "fresa": sum(p["cantidad"] for p in bd["pedidos"] if p["sabor"] == "fresa"),
            "vainilla": sum(p["cantidad"] for p in bd["pedidos"] if p["sabor"] == "vainilla"),
            "chocolate": sum(p["cantidad"] for p in bd["pedidos"] if p["sabor"] == "chocolate")
        },
        "hechos": bd["contadores"]
    })

@app.route("/", methods=["GET"])
def home():
    return "Servidor de Bollikaos funcionando 🥐"

if __name__ == "__main__":
    import os
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))

