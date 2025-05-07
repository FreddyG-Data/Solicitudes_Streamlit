from flask import Flask, request, jsonify
import pyodbc
from datetime import datetime

app = Flask(__name__)

conn = pyodbc.connect("DSN=Systemclub;UID=Santiago;PWD=1203f", autocommit=True)

@app.route('/usuarios', methods=['GET'])
def get_usuarios():
    try:
        cursor = conn.cursor()
        query = """
            SELECT nombre_usuario, doc_empleado
            FROM dba.usuarios
            WHERE activo = 'S'
        """
        cursor.execute(query)
        rows = cursor.fetchall()

        usuarios = []
        for row in rows:
            usuarios.append({
                "nombre": row.nombre_usuario,
                "documento": row.doc_empleado or ""
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

        cursor.execute("SELECT MAX(consecutivo) FROM dba.hd_solicitudes WHERE id_empresa = '01'")
        max_consec = cursor.fetchone()[0] or 0
        nuevo_consec = max_consec + 1

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
            SELECT s.consecutivo, s.fecha, s.hora, s.asunto, s.descripcion, s.estado, s.usuario_solicita, u.nombre_usuario
            FROM dba.hd_solicitudes s
            LEFT JOIN dba.usuarios u ON s.usuario_solicita = u.doc_empleado
            WHERE s.id_empresa = '01'
            ORDER BY s.fecha DESC, s.hora DESC
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
                "documento": row.usuario_solicita,
                "nombre": row.nombre_usuario or "Sin nombre"
            })

        return jsonify(solicitudes)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/solicitudes/<int:consecutivo>', methods=['PUT'])
def actualizar_estado(consecutivo):
    try:
        data = request.get_json()
        nuevo_estado = data.get("estado")
        usuario_modifica = data.get("usuario")  # Documento del que hace el cambio

        if not nuevo_estado or not usuario_modifica:
            return jsonify({"error": "Datos incompletos"}), 400

        now = datetime.now()
        fecha = now.strftime("%Y-%m-%d")
        hora = now.strftime("%H:%M:%S")

        cursor = conn.cursor()
        update_query = """
            UPDATE dba.hd_solicitudes
            SET estado = ?, fecha = ?, hora = ?, usuario_registro = ?
            WHERE id_empresa = '01' AND consecutivo = ?
        """
        cursor.execute(update_query, (nuevo_estado, fecha, hora, usuario_modifica, consecutivo))

        return jsonify({"mensaje": "Estado actualizado correctamente"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)