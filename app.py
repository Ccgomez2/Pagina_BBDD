from flask import Flask, request, jsonify
import json, os
import paho.mqtt.publish as publish

app = Flask(__name__)
DB_PATH = "database.json"

def cargar_bd():
    if not os.path.exists(DB_PATH):
        return {"pedidos": [], "contadores": {"fresa": 0, "vainilla": 0, "chocolate": 0, "defectuosos": 0}}
    with open(DB_PATH, "r") as f:
        return json.load(f)

def guardar_bd(data):
    with open(DB_PATH, "w") as f:
        json.dump(data, f)

@app.route("/pedido", methods=["POST"])
def recibir_pedido():
    data = request.json
    nombre = data.get("nombre")
    sabor = data.get("sabor")
    cantidad = data.get("cantidad")

    if not nombre or not sabor or not cantidad:
        return jsonify({"error": "Faltan campos obligatorios"}), 400

    bd = cargar_bd()
    bd["pedidos"].append({"nombre": nombre, "sabor": sabor, "cantidad": cantidad})
    bd["contadores"][sabor] += cantidad
    guardar_bd(bd)

    # MQTT
    mensaje = json.dumps({"evento": "nuevo_pedido", "sabor": sabor, "cantidad": cantidad})
    publish.single("richi5/giirob/pr2/enviar/web", mensaje, hostname="broker.emqx.io", port=1883)

    return jsonify({"ok": True, "mensaje": "Pedido recibido"})

@app.route("/estado", methods=["GET"])
def estado():
    bd = cargar_bd()
    return jsonify(bd["contadores"])

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
