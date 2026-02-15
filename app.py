from flask import Flask, render_template, jsonify, request
import folium
from geopy.distance import geodesic
import json
from datetime import datetime

app = Flask(__name__)

# Хранилище данных
points = []
vehicles = []

# Доступные действия на точках
ACTIONS = [
    {"id": 1, "name": "Очистка снега"},
    {"id": 2, "name": "Заправка"},
    {"id": 3, "name": "Техническое обслуживание"}
]


@app.route('/')
def index():
    """Главная страница"""
    return render_template('index.html',
                           actions=ACTIONS)


@app.route('/api/points', methods=['GET', 'POST'])
def handle_points():
    """Обработка точек маршрута"""
    if request.method == 'POST':
        data = request.json
        point = {
            'id': len(points) + 1,
            'lat': data['lat'],
            'lng': data['lng'],
            'name': data.get('name', f'Точка {len(points) + 1}'),
            'vehicle_id': data.get('vehicle_id'),  # ID транспорта, к которому привязана точка
            'actions': data.get('actions', [])
        }
        points.append(point)
        return jsonify({'success': True, 'point': point})

    return jsonify(points)


@app.route('/api/points/<int:point_id>', methods=['PUT', 'DELETE'])
def modify_point(point_id):
    """Изменение или удаление точки"""
    global points

    if request.method == 'DELETE':
        points = [p for p in points if p['id'] != point_id]
        return jsonify({'success': True})

    elif request.method == 'PUT':
        data = request.json
        for point in points:
            if point['id'] == point_id:
                point.update(data)
                return jsonify({'success': True, 'point': point})

    return jsonify({'success': False}), 404


@app.route('/api/vehicles', methods=['GET', 'POST'])
def handle_vehicles():
    """Обработка транспорта"""
    if request.method == 'POST':
        data = request.json
        vehicle = {
            'id': len(vehicles) + 1,
            'name': data.get('name', f'Транспорт {len(vehicles) + 1}')
        }
        vehicles.append(vehicle)
        return jsonify({'success': True, 'vehicle': vehicle})

    return jsonify(vehicles)


@app.route('/api/vehicles/<int:vehicle_id>', methods=['DELETE'])
def delete_vehicle(vehicle_id):
    """Удаление транспорта"""
    global vehicles, points

    # Удаляем транспорт
    vehicles = [v for v in vehicles if v['id'] != vehicle_id]

    # Удаляем все точки, привязанные к этому транспорту
    points = [p for p in points if p.get('vehicle_id') != vehicle_id]

    return jsonify({'success': True})


@app.route('/api/vehicles/<int:vehicle_id>/points', methods=['GET'])
def get_vehicle_points(vehicle_id):
    """Получение точек для конкретного транспорта"""
    vehicle_points = [p for p in points if p.get('vehicle_id') == vehicle_id]
    return jsonify(vehicle_points)


@app.route('/api/start_route', methods=['POST'])
def start_route():
    """Заглушка для кнопки Старт"""
    data = request.json
    return jsonify({'success': True, 'message': 'Маршрут начат'})


if __name__ == '__main__':
    app.run(debug=True)