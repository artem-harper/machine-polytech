from flask import Flask, render_template, jsonify, request
import folium
from geopy.distance import geodesic
import json
from datetime import datetime

app = Flask(__name__)

points = []
routes = []
point_counter = 1

VEHICLES = [
    {"id": 1, "name": "ТС-001", "display_name": "Транспортное средство #1", "color": "#3498db"},
    {"id": 2, "name": "ТС-002", "display_name": "Транспортное средство #2", "color": "#e74c3c"},
    {"id": 3, "name": "ТС-003", "display_name": "Транспортное средство #3", "color": "#2ecc71"}
]

ACTIONS = [
    {"id": 1, "name": "Очистка снега"},
    {"id": 2, "name": "Заправка"},
    {"id": 3, "name": "Техническое обслуживание"}
]


@app.route('/')
def index():
    return render_template('index.html',
                           actions=ACTIONS,
                           vehicles=VEHICLES)


@app.route('/api/points', methods=['GET', 'POST'])
def handle_points():
    global point_counter
    if request.method == 'POST':
        data = request.json
        vehicle_id = data['vehicle_id']

        vehicle_points = [p for p in points if p.get('vehicle_id') == vehicle_id]
        next_number = len(vehicle_points) + 1

        point = {
            'id': point_counter,
            'vehicle_id': vehicle_id,
            'number': next_number,
            'lat': data['lat'],
            'lng': data['lng'],
            'name': f'Точка {next_number}'
        }
        point_counter += 1
        points.append(point)
        return jsonify({'success': True, 'point': point})

    return jsonify(points)


@app.route('/api/points/<int:point_id>', methods=['DELETE'])
def delete_point(point_id):
    global points
    points = [p for p in points if p['id'] != point_id]
    return jsonify({'success': True})


@app.route('/api/vehicles/<int:vehicle_id>/points', methods=['GET'])
def get_vehicle_points(vehicle_id):
    vehicle_points = [p for p in points if p.get('vehicle_id') == vehicle_id]
    vehicle_points.sort(key=lambda x: x['id'])
    return jsonify(vehicle_points)


@app.route('/api/routes', methods=['GET', 'POST'])
def handle_routes():
    if request.method == 'POST':
        data = request.json
        route = {
            'id': len(routes) + 1,
            'vehicle_id': data['vehicle_id'],
            'point_ids': data['point_ids'],
            'segments': data.get('segments', [])
        }
        routes.append(route)
        return jsonify({'success': True, 'route': route})

    return jsonify(routes)


@app.route('/api/routes/<int:route_id>', methods=['PUT', 'DELETE'])
def modify_route(route_id):
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


if __name__ == '__main__':
    app.run(debug=True)