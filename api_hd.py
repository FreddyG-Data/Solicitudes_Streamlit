from flask import Flask, request, jsonify
import pyodbc
from datetime import datetime

app = Flask(__name__)

# Conexión a SQL Anywhere
conn = pyodbc.connect("DSN=Systemclub;UID=Santiago;PWD=1203f", autocommit=True)

@app.route('/usuarios', methods=['GET'])
def get_usuarios():
    try:
        cursor = conn.cursor()
        query = """
            SELECT nombre_usuario, doc_empleado
            FROM dba.usuarios
            WHERE activo = 'S'
            ORDER BY nombre_usuario
        """
        cursor.execute(query)
        rows = cursor.fetchall()

        usuarios = []
        for row in rows:
            if row.doc_empleado:
                usuarios.append({
                    "nombre": row.nombre_usuario,
                    "documento": row.doc_empleado
                })
            else:
                usuarios.append({
                    "nombre": row.nombre_usuario,
                    "documento": ""  # Permitimos que el frontend lo solicite
                })

        return jsonify(usuarios)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/solicitudes', methods=['POST'])
def crear_solicitud():
    try:
        data = request.get_json()

        usuario_doc = data.get("documento")
        asunto = data.get("asunto")
        descripcion = data.get("descripcion")

        if not usuario_doc or not asunto or not descripcion:
            return jsonify({"error": "Faltan datos requeridos"}), 400

        now = datetime.now()
        fecha = now.strftime("%Y-%m-%d")
        hora = now.strftime("%H:%M:%S")

        cursor = conn.cursor()

        # Obtener nuevo consecutivo
        cursor.execute("SELECT MAX(consecutivo) FROM dba.hd_solicitudes WHERE id_empresa = '01'")
        max_consec = cursor.fetchone()[0] or 0
        nuevo_consec = max_consec + 1

        # Insertar la solicitud
        insert_query = """
            INSERT INTO dba.hd_solicitudes (
                id_empresa, consecutivo, fecha, hora, asunto, descripcion, estado,
                area_destino_ini, area_destino_fin, categoria_ini, categoria_fin, usuario_solicita, usuario_registro
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """

        cursor.execute(insert_query, (
            '01', nuevo_consec, fecha, hora, asunto, descripcion, 'P',
            '022', '022', 4, 4, usuario_doc, usuario_doc
        ))

        return jsonify({"mensaje": "Solicitud registrada correctamente"}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route('/solicitudes', methods=['GET'])
def obtener_solicitudes():
    try:
        cursor = conn.cursor()
        query = """
            SELECT consecutivo, fecha, hora, asunto, descripcion, estado, usuario_solicita
            FROM dba.hd_solicitudes
            WHERE id_empresa = '01'
            ORDER BY fecha DESC, hora DESC
        """
        cursor.execute(query)
        rows = cursor.fetchall()

        solicitudes = []
        for row in rows:
            solicitudes.append({
                "consecutivo": row.consecutivo,
                "fecha": row.fecha.strftime("%Y-%m-%d"),
                "hora": row.hora.strftime("%H:%M:%S"),
                "asunto": row.asunto,
                "descripcion": row.descripcion,
                "estado": row.estado,
                "documento": row.usuario_solicita
            })

        return jsonify(solicitudes)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)