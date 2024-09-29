from flask import Flask, request, jsonify, make_response
from collections import defaultdict
import heapq
from datetime import datetime

app = Flask(__name__)

class User:

    def __init__(self):
        self.points = 0
        self.points_per_payer = defaultdict(int)
        self.transactions = []

    def add_transaction(self, payer, points, timestamp):
        if self.points + points >= 0 and self.points_per_payer[payer] + points >= 0:
            self.points += points
            self.points_per_payer[payer] += points
            heapq.heappush(self.transactions, (timestamp, points, payer))
        # reset to 0
        else:
            heapq.heappush(self.transactions, (timestamp, -self.points_per_payer[payer], payer))
            self.points = 0
            self.points_per_payer[payer] = 0

    
    def spend_points(self, points_to_spend):
        spent_points_per_payer = defaultdict(int)

        while points_to_spend != 0:

            # get the oldest transaction
            timestamp, points, payer = heapq.heappop(self.transactions)

            # check if we still have this number of points
            available_points = user.points_per_payer[payer]
            points_able_to_remove = min(points, available_points)
            
            # check if we'll have leftover points to add back to heap
            if points_to_spend < points_able_to_remove:
                points_to_remove = points_to_spend
                heapq.heappush(user.transactions, (timestamp, points_able_to_remove - points_to_remove, payer))
            else:
                points_to_remove = points_able_to_remove

            # remove points accordingly
            self.points -= points_to_remove
            self.points_per_payer[payer] -= points_to_remove
            spent_points_per_payer[payer] -= points_to_remove
            points_to_spend -= points_to_remove


        return spent_points_per_payer
    
user = User()


@app.route('/add', methods=['POST'])
def add_transaction():
    data = request.get_json()

    points = data['points']
    payer = data['payer']
    timestamp = datetime.strptime(data['timestamp'], "%Y-%m-%dT%H:%M:%SZ")

    user.add_transaction(payer, points, timestamp)

    return '', 200


@app.route('/spend', methods=['POST'])
def spend_points():
    data = request.get_json()

    points_to_spend = data['points']

    if points_to_spend > user.points:
        return 'User doesn\'t have enough points', 400

    if points_to_spend < 0:
        return 'Points to spend cannot be negative', 400
    
    spent_points_per_payer = user.spend_points(points_to_spend)
    
    output = []
    for payer, points in spent_points_per_payer.items():
        output.append({'payer': payer, 'points': points})
    
    return jsonify(output), 200


@app.route('/balance', methods=['GET'])
def get_balance():
    return jsonify(user.points_per_payer), 200
    

if __name__ == '__main__':
    app.run()