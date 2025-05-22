from flask import Flask, request, jsonify, send_from_directory
import os
import csv
from greedy import greedy_algorithm
from genetic import genetic_algorithm
import re
import random

app = Flask(__name__, static_folder='../frontend', static_url_path='/')

# =============== ROUTE HANDLERS ===============
@app.route('/')
def serve_index():
    return send_from_directory(app.static_folder, 'html.html')

@app.route('/api/dataset', methods=['GET'])
def get_dataset():
    return jsonify(dataset)

@app.route('/api/generate-schedule', methods=['POST'])
def generate_schedule():
    try:
        data = request.get_json()
        print("Data yang diterima:", data)
        
        # Convert availability format
        availability = {}
        for day, info in data.get('availability', {}).items():
            duration = info.get('duration', 0) if isinstance(info, dict) else 0
            availability[day] = duration

        # Validate input
        if not any(duration > 0 for duration in availability.values()):
            return jsonify({'error': 'Tidak ada hari dengan durasi latihan yang ditentukan'}), 400

        # Get user preferences
        goal = data.get('goal', 'muscle_building')
        gender = data.get('gender', 'pria')
        
        # Filter workouts based on goal
        filtered_workouts = filter_workouts_by_goal(dataset, goal, gender)
        
        # Use hybrid algorithm (combine greedy + genetic)
        schedule = hybrid_algorithm(filtered_workouts, availability)

        # Format response
        schedule_serializable = format_schedule_response(schedule)

        return jsonify({'schedule': schedule_serializable})

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Terjadi kesalahan: {str(e)}'}), 500

# =============== ALGORITHM FUNCTIONS ===============
def hybrid_algorithm(workouts, availability):
    """Combine greedy and genetic algorithms for optimal results"""
    # Start with greedy solution
    greedy_schedule = greedy_algorithm(workouts, availability)
    
    # Improve with genetic algorithm
    final_schedule = genetic_algorithm(workouts, availability, base_schedule=greedy_schedule)
    
    return final_schedule

def filter_workouts_by_goal(workouts, goal, gender):
    """Filter and prioritize workouts based on user's goal"""
    filtered = []
    
    for workout in workouts:
        if workout['type'] == 'rest':
            filtered.append(workout)
            continue
            
        # Goal-based filtering
        if goal == 'weight_loss':
            # Focus on high-rep, cardio-intensive exercises
            if workout['type'] in ['upper chest', 'lower chest', 'chest isolation', 
                                  'upper', 'lower', 'quadriceps', 'hamstrings', 'calves']:
                # Modify for weight loss (higher reps, lower sets)
                workout_copy = workout.copy()
                workout_copy['sets'] = min(workout['sets'], 3)
                workout_copy['reps'] = max(workout['reps'], 15)
                workout_copy['duration'] = (workout_copy['sets'] * workout_copy['reps']) / 8  # Faster pace
                filtered.append(workout_copy)
                
        elif goal == 'muscle_building':
            # Focus on compound movements and progressive overload
            if workout['type'] in ['upper chest', 'lower chest', 'biceps', 'triceps', 
                                  'upper', 'lower', 'quadriceps', 'hamstrings', 'anterior', 'lateral', 'posterior']:
                # Modify for muscle building (moderate reps, more sets)
                workout_copy = workout.copy()
                workout_copy['sets'] = max(workout['sets'], 4)
                workout_copy['reps'] = min(max(workout['reps'], 8), 12)
                workout_copy['duration'] = (workout_copy['sets'] * workout_copy['reps']) / 10
                filtered.append(workout_copy)
                
        elif goal == 'endurance':
            # Focus on lighter weights, higher volume
            if workout['type'] in ['upper', 'lower', 'quadriceps', 'hamstrings', 'calves', 
                                  'upper chest', 'lower chest', 'biceps', 'triceps']:
                workout_copy = workout.copy()
                workout_copy['sets'] = max(workout['sets'], 4)
                workout_copy['reps'] = max(workout['reps'], 15)
                workout_copy['duration'] = (workout_copy['sets'] * workout_copy['reps']) / 12
                filtered.append(workout_copy)
                
        elif goal == 'strength':
            # Focus on compound movements, lower reps
            if workout['type'] in ['upper chest', 'lower chest', 'upper', 'lower', 
                                  'quadriceps', 'hamstrings', 'anterior']:
                workout_copy = workout.copy()
                workout_copy['sets'] = max(workout['sets'], 5)
                workout_copy['reps'] = min(workout['reps'], 8)
                workout_copy['duration'] = (workout_copy['sets'] * workout_copy['reps']) / 8
                filtered.append(workout_copy)
    
    return filtered

def format_schedule_response(schedule):
    """Format schedule for frontend display"""
    schedule_serializable = {}
    for day, workouts in schedule.items():
        workout_list = []
        for w in workouts:
            workout_list.append({
                'name': w['name'], 
                'type': w['type'], 
                'duration': w['duration'],
                'sets': w.get('sets', 0),
                'reps': w.get('reps', 0)
            })
        
        # Determine day type
        is_rest = len(workout_list) == 1 and workout_list[0]['type'] == 'rest'
        total_duration = sum(w['duration'] for w in workout_list)
        
        schedule_serializable[day] = {
            'day_type': 'Rest Day' if is_rest else f'Workout Day ({total_duration:.1f}h)',
            'workouts': workout_list,
            'total_duration': total_duration
        }

    return schedule_serializable

# =============== UTILITY FUNCTIONS ===============
def extract_first_number(text):
    """Extract first number from string (e.g., '3-4' becomes 3)"""
    match = re.search(r'\d+', str(text))
    return int(match.group()) if match else None

def load_dataset(filename='Workout.csv'):
    """Load workout data from CSV file"""
    workouts = []
    try:
        with open(filename, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                try:
                    sets = extract_first_number(row.get('Sets', ''))
                    reps = extract_first_number(row.get('Reps per Set', ''))

                    # Handle rest day
                    if row.get('Type of Muscle', '').strip().lower() == 'rest':
                        sets = 0
                        reps = 0
                    elif sets is None or reps is None:
                        continue  # Skip invalid entries

                    duration = (sets * reps) / 10 if sets > 0 and reps > 0 else 0

                    workouts.append({
                        'name': row['Workout'],
                        'type': row['Type of Muscle'].strip().lower(),
                        'duration': duration,
                        'sets': sets,
                        'reps': reps
                    })
                except Exception as e:
                    print(f"Skipping row {row.get('Workout', 'Unknown')}: {e}")
    except FileNotFoundError:
        print(f"File {filename} not found!")
    except Exception as e:
        print(f"Error loading dataset: {e}")
    return workouts

# =============== INITIALIZATION ===============
dataset = load_dataset()
print(f"Dataset loaded: {len(dataset)} workouts")

if __name__ == '__main__':
    app.run(debug=True)