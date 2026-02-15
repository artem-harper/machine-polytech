from flask import Flask, render_template, jsonify, request
import folium
from geopy.distance import geodesic
import json
from datetime import datetime

app = Flask(__name__)

# Хранилище данных
points = []
routes = []

# Предустановленный транспорт (3 штуки)
VEHICLES = [
    {"id": 1, "name": "ТС-001", "display_name": "Транспортное средство #1", "color": "#3498db"},
    {"id": 2, "name": "ТС-002", "display_name": "Транспортное средство #2", "color": "#e74c3c"},
    {"id": 3, "name": "ТС-003", "display_name": "Транспортное средство #3", "color": "#2ecc71"}
]

# Доступные действия для сегментов маршрута
ACTIONS = [
    {"id": 1, "name": "Очистка снега", "icon": ""},
    {"id": 2, "name": "Заправка", "icon": ""},
    {"id": 3, "name": "Техническое обслуживание", "icon": ""}
]


@app.route('/')
def index():
    """Главная страница"""
    return render_template('index.html',
                           actions=ACTIONS,
                           vehicles=VEHICLES)


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
            'vehicle_id': data.get('vehicle_id')
        }
        points.append(point)
        return jsonify({'success': True, 'point': point})

    return jsonify(points)


@app.route('/api/points/<int:point_id>', methods=['DELETE'])
def delete_point(point_id):
    """Удаление точки"""
    global points
    points = [p for p in points if p['id'] != point_id]
    return jsonify({'success': True})


@app.route('/api/routes', methods=['GET', 'POST'])
def handle_routes():
    """Обработка маршрутов"""
    if request.method == 'POST':
        data = request.json
        route = {
            'id': len(routes) + 1,
            'vehicle_id': data['vehicle_id'],
            'point_ids': data['point_ids'],
            'segments': data.get('segments', [])  # Действия для каждого сегмента
        }
        routes.append(route)
        return jsonify({'success': True, 'route': route})

    # GET - возвращаем все маршруты
    return jsonify(routes)


@app.route('/api/routes/<int:route_id>', methods=['PUT', 'DELETE'])
def modify_route(route_id):
    """Изменение или удаление маршрута"""
    global routes

    if request.method == 'DELETE':
        routes = [r for r in routes if r['id'] != route_id]
        return jsonify({'success': True})

    elif request.method == 'PUT':
        data = request.json
        for route in routes:
            if route['id'] == route_id:
                route.update(data)
                return jsonify({'success': True, 'route': route})

    return jsonify({'success': False}), 404


@app.route('/api/vehicles/<int:vehicle_id>/points', methods=['GET'])
def get_vehicle_points(vehicle_id):
    """Получение точек для конкретного транспорта"""
    vehicle_points = [p for p in points if p.get('vehicle_id') == vehicle_id]
    # Сортируем по ID для правильного порядка
    vehicle_points.sort(key=lambda x: x['id'])
    return jsonify(vehicle_points)


@app.route('/api/vehicles/<int:vehicle_id>/route', methods=['GET'])
def get_vehicle_route(vehicle_id):
    """Получение маршрута для конкретного транспорта"""
    vehicle_route = next((r for r in routes if r['vehicle_id'] == vehicle_id), None)
    if vehicle_route:
        route_points = [p for p in points if p['id'] in vehicle_route['point_ids']]
        route_points.sort(key=lambda x: vehicle_route['point_ids'].index(x['id']))
        return jsonify({
            'route': vehicle_route,
            'points': route_points
        })
    return jsonify(None)


@app.route('/api/start_route', methods=['POST'])
def start_route():
    """Заглушка для кнопки Старт"""
    data = request.json
    return jsonify({'success': True, 'message': 'Маршрут начат'})


if __name__ == '__main__':
    app.run(debug=True)