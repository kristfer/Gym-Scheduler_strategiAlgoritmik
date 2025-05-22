# =============== GREEDY SCHEDULING ALGORITHM ===============

def greedy_algorithm(workouts, availability):
    """
    Greedy algorithm for workout scheduling
    Assigns workouts to days based on available time, prioritizing longer workouts first
    """
    days = ['Senin', 'Selasa', 'Rabu', 'Kamis', 'Jumat', 'Sabtu', 'Minggu']
    schedule = {day: [] for day in days}

    # Separate active workouts from rest
    active_workouts = [w for w in workouts if w['type'] != 'rest']
    rest_workout = next((w for w in workouts if w['type'] == 'rest'), None)
    
    # Sort workouts by duration (longest first)
    sorted_workouts = sorted(active_workouts, key=lambda w: w['duration'], reverse=True)

    # Schedule workouts for each day
    for day in days:
        available_time = availability.get(day, 0)
        
        # No time available - assign rest day
        if available_time <= 0:
            if rest_workout:
                schedule[day].append(rest_workout)
            continue
            
        # Fit workouts into available time
        used_workouts = []
        for workout in sorted_workouts:
            if workout in used_workouts:
                continue
                
            if workout['duration'] <= available_time:
                schedule[day].append(workout)
                available_time -= workout['duration']
                used_workouts.append(workout)
                
        # If no workouts scheduled, add rest day
        if not schedule[day] and rest_workout:
            schedule[day].append(rest_workout)
            
    return schedule