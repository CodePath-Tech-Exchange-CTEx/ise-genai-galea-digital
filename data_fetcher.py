#############################################################################
# data_fetcher.py
#
# This file contains functions to fetch data needed for the app.
#
# You will re-write these functions in Unit 3, and are welcome to alter the
# data returned in the meantime. We will replace this file with other data when
# testing earlier units.
#############################################################################

import random
from google.cloud import bigquery

users = {
    'user1': {
        'full_name': 'Remi',
        'username': 'remi_the_rems',
        'date_of_birth': '1990-01-01',
        'profile_image': 'https://upload.wikimedia.org/wikipedia/commons/c/c8/Puma_shoes.jpg',
        'friends': ['user2', 'user3', 'user4'],
    },
    'user2': {
        'full_name': 'Blake',
        'username': 'blake',
        'date_of_birth': '1990-01-01',
        'profile_image': 'https://upload.wikimedia.org/wikipedia/commons/c/c8/Puma_shoes.jpg',
        'friends': ['user1'],
    },
    'user3': {
        'full_name': 'Jordan',
        'username': 'jordanjordanjordan',
        'date_of_birth': '1990-01-01',
        'profile_image': 'https://upload.wikimedia.org/wikipedia/commons/c/c8/Puma_shoes.jpg',
        'friends': ['user1', 'user4'],
    },
    'user4': {
        'full_name': 'Gemmy',
        'username': 'gems',
        'date_of_birth': '1990-01-01',
        'profile_image': 'https://upload.wikimedia.org/wikipedia/commons/c/c8/Puma_shoes.jpg',
        'friends': ['user1', 'user3'],
    },
}

def get_user_sensor_data(user_id, workout_id, client=None):
    """
    Fetches timestamped sensor information for a specific workout from BigQuery.

    Args:
        user_id (str): The unique identifier for the user.
        workout_id (str): The unique identifier for the workout session.
        client (google.cloud.bigquery.Client, optional): An instantiated BigQuery client. 
            If None, a new client will be initialized. Defaults to None.


    Returns:
        list[dict]: A list of records representing sensor readings. Each dictionary contains:
            - 'sensor_type' (str): The human-readable name of the sensor (e.g., "Heart Rate").
            - 'timestamp' (str): The string representation of when the data was recorded.
            - 'data' (float): The numeric value of the sensor reading.
            - 'units' (str): The unit of measurement for the reading (e.g., "bpm", "Celsius").

    Raises:
        ValueError: If either user_id or workout_id is None, or if either is not found in the DB.
    """
    if client is None:
        client = bigquery.Client()
    
    if user_id is None or workout_id is None:
        raise ValueError("user_id and workout_id cannot be None")
    
    query = """
        SELECT 
            st.Name AS sensor_type, 
            sd.Timestamp AS timestamp, 
            sd.SensorValue AS data,
            st.Units AS units
        FROM 
            `amier-davis-hu.ISE.SensorData` AS sd
        JOIN 
            `amier-davis-hu.ISE.Workouts` AS w 
            ON sd.WorkoutID = w.WorkoutId
        JOIN 
            `amier-davis-hu.ISE.SensorTypes` AS st 
            ON sd.SensorId = st.SensorId
        WHERE 
            w.UserId = @user_id 
            AND w.WorkoutId = @workout_id
        ORDER BY 
            sd.Timestamp ASC
    """

    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("user_id", "STRING", user_id),
            bigquery.ScalarQueryParameter("workout_id", "STRING", workout_id),
        ]
    )
    
    query_job = client.query(query, job_config=job_config)
    results = query_job.result()

    if not results:
        user_check_query = "SELECT 1 FROM `amier-davis-hu.ISE.Workouts` WHERE UserId = @user_id LIMIT 1"
        user_check_config = bigquery.QueryJobConfig(
            query_parameters=[bigquery.ScalarQueryParameter("user_id", "STRING", user_id)]
        )
        user_exists = list(client.query(user_check_query, job_config=user_check_config).result())

        if not user_exists:
            raise ValueError(f"User {user_id} not found.")
        else:
            raise ValueError(f"Workout {workout_id} not found for user {user_id}.")

    sensor_data = []
    
    for row in results:
        sensor_data.append({
            'sensor_type': row.sensor_type,
            'timestamp': str(row.timestamp),
            'data': row.data,
            'units': row.units
        })
        
    return sensor_data


def get_user_workouts(user_id):
    """Returns a list of user's workouts.

    This function currently returns random data. You will re-write it in Unit 3.
    """
    workouts = []
    for index in range(random.randint(1, 3)):
        random_lat_lng_1 = (
            1 + random.randint(0, 100) / 100,
            4 + random.randint(0, 100) / 100,
        )
        random_lat_lng_2 = (
            1 + random.randint(0, 100) / 100,
            4 + random.randint(0, 100) / 100,
        )
        workouts.append({
            'workout_id': f'workout{index}',
            'start_timestamp': '2024-01-01 00:00:00',
            'end_timestamp': '2024-01-01 00:30:00',
            'start_lat_lng': random_lat_lng_1,
            'end_lat_lng': random_lat_lng_2,
            'distance': random.randint(0, 200) / 10.0,
            'steps': random.randint(0, 20000),
            'calories_burned': random.randint(0, 100),
        })
    return workouts


def get_user_profile(user_id):
    """Returns information about the given user.

    This function currently returns random data. You will re-write it in Unit 3.
    """
    if user_id not in users:
        raise ValueError(f'User {user_id} not found.')
    return users[user_id]


def get_user_posts(user_id):
    """Returns a list of a user's posts.

    This function currently returns random data. You will re-write it in Unit 3.
    """
    content = random.choice([
        'Had a great workout today!',
        'The AI really motivated me to push myself further, I ran 10 miles!',
    ])
    return [{
        'user_id': user_id,
        'post_id': 'post1',
        'timestamp': '2024-01-01 00:00:00',
        'content': content,
        'image': 'image_url',
    }]


def get_genai_advice(user_id):
    """Returns the most recent advice from the genai model.

    This function currently returns random data. You will re-write it in Unit 3.
    """
    advice = random.choice([
        'Your heart rate indicates you can push yourself further. You got this!',
        "You're doing great! Keep up the good work.",
        'You worked hard yesterday, take it easy today.',
        'You have burned 100 calories so far today!',
    ])
    image = random.choice([
        'https://plus.unsplash.com/premium_photo-1669048780129-051d670fa2d1?q=80&w=3870&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D',
        None,
    ])
    return {
        'advice_id': 'advice1',
        'timestamp': '2024-01-01 00:00:00',
        'content': advice,
        'image': image,
    }
