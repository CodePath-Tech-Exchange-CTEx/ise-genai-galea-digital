#############################################################################
# data_fetcher.py
#
# This file contains functions to fetch data needed for the app.
#
# You will re-write these functions in Unit 3, and are welcome to alter the
# data returned in the meantime. We will replace this file with other data when
# testing earlier units.
#############################################################################

from google.cloud import bigquery
from datetime import datetime
import random


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


def get_user_workouts(user_id, client=None):
    """
    Fetches a list of workouts for a given user from BigQuery.

    Args:
        user_id (str): The  identifier of the user whose workouts are being retrieved.

    Returns:
        list[dict]: A list of dictionaries, where each dictionary represents a workout.
        Each workout contains:
            - workout_id (str)
            - start_timestamp (str | None)
            - end_timestamp (str | None)
            - start_lat_lng (tuple[float, float] | None)
            - end_lat_lng (tuple[float, float] | None)
            - distance (float)
            - steps (int)
            - calories_burned (float)
    """
    if user_id is None:
        raise ValueError("user_id cannot be None")

    if client is None:
        client = bigquery.Client()

    query = """
        SELECT
            WorkoutId,
            StartTimestamp,
            EndTimestamp,
            StartLocationLat,
            StartLocationLong,
            EndLocationLat,
            EndLocationLong,
            TotalDistance,
            TotalSteps,
            CaloriesBurned
        FROM amier-davis-hu.ISE.Workouts
        WHERE UserId = @user_id
        ORDER BY StartTimestamp DESC
    """

    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("user_id", "STRING", user_id)
        ]
    )

    query_job = client.query(query, job_config=job_config)
    results = query_job.result()
    if not results:
        raise ValueError(f"User {user_id} not found.")

    workouts = []
    for row in results:
        start_lat_lng = None
        if row.StartLocationLat is not None or row.StartLocationLong is not None:
            start_lat_lng = (row.StartLocationLat, row.StartLocationLong)

        end_lat_lng = None
        if row.EndLocationLat is not None and row.EndLocationLong is not None:
            end_lat_lng = (row.EndLocationLat, row.EndLocationLong)

        workouts.append({
            "workout_id": row.WorkoutId,
            "start_timestamp": row.StartTimestamp.strftime("%Y-%m-%d %H:%M:%S") if row.StartTimestamp else None,
            "end_timestamp": row.EndTimestamp.strftime("%Y-%m-%d %H:%M:%S") if row.EndTimestamp else None,
            "start_lat_lng": start_lat_lng,
            "end_lat_lng": end_lat_lng,
            "distance": row.TotalDistance,
            "steps": row.TotalSteps,
            "calories_burned": row.CaloriesBurned,
        })

    return workouts
    

def get_user_profile(user_id, client=None):
    """
    Returns information about the given user from BigQuery.

    Args:
        user_id (str): The unique identifier for the user.
        client (google.cloud.bigquery.Client, optional): An instantiated BigQuery client. 
            If None, a new client will be initialized. Defaults to None.

    Returns:
        dict: A dictionary containing:
            - 'full_name' (str): The user's full name.
            - 'username' (str): The user's handle.
            - 'date_of_birth' (str): The user's birth date.
            - 'profile_image' (str): URL to the user's image.
            - 'friends' (list[str]): A list of friend user_ids.

    Raises:
        ValueError: If user_id is None or if the user is not found.
    """
    if user_id is None:
        raise ValueError("user_id cannot be None")

    if client is None:
        client = bigquery.Client()
    
    query = """
        SELECT 
            Name AS full_name, 
            Username AS username, 
            CAST(DateOfBirth AS STRING) AS date_of_birth, 
            ImageUrl AS profile_image,
            ARRAY(
                SELECT UserId2 FROM `amier-davis-hu.ISE.Friends` WHERE UserId1 = @user_id
                UNION DISTINCT
                SELECT UserId1 FROM `amier-davis-hu.ISE.Friends` WHERE UserId2 = @user_id
            ) AS friends
        FROM `amier-davis-hu.ISE.Users`
        WHERE UserId = @user_id
    """
    
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("user_id", "STRING", user_id)
        ]
    )

    query_job = client.query(query, job_config=job_config)
    results = list(query_job.result())

    if not results:
        raise ValueError(f"User {user_id} not found.")

    row = results[0]
    return {
        'full_name': row.full_name,
        'username': row.username,
        'date_of_birth': row.date_of_birth,
        'profile_image': row.profile_image,
        'friends': list(row.friends)
    }




def get_user_posts(user_id, client=None):
    """
    Returns a list of a user's posts from BigQuery.

    Args:
        user_id (str): The unique identifier for the user.
        client (google.cloud.bigquery.Client, optional): An instantiated BigQuery client. 
            If None, a new client will be initialized. Defaults to None.

    Returns:
        list[dict]: A list of posts. Each dictionary contains:
            - 'user_id' (str): The ID of the author.
            - 'post_id' (str): The unique ID of the post.
            - 'timestamp' (str): When the post was created.
            - 'content' (str): The text content (may be None).
            - 'image' (str): The image URL associated with the post.

    Raises:
        ValueError: If user_id is None.
    """
    if user_id is None:
        raise ValueError("user_id cannot be None")

    if client is None:
        client = bigquery.Client()
    
    query = """
        SELECT 
            AuthorId AS user_id, 
            PostId AS post_id, 
            CAST(Timestamp AS STRING) AS timestamp, 
            Content AS content, 
            ImageUrl AS image
        FROM `amier-davis-hu.ISE.Posts`
        WHERE AuthorId = @user_id
        ORDER BY Timestamp DESC
    """
    
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("user_id", "STRING", user_id)
        ]
    )

    query_job = client.query(query, job_config=job_config)
    results = query_job.result()

    posts = []
    for row in results:
        posts.append({
            'user_id': row.user_id,
            'post_id': row.post_id,
            'timestamp': row.timestamp,
            'content': row.content,
            'image': row.image
        })
    
    return posts

def get_genai_advice(user_id, model=None):
    """Returns the most recent advice from the genai model.

    This function currently returns random data. You will re-write it in Unit 3.
    """
    content = None
    username = get_username(user_id)

    try:
        if model is None:
            import vertexai
            from vertexai.generative_models import GenerativeModel

            vertexai.init(project="lena-diouf-hu", location="us-central1")
            model = GenerativeModel("gemini-2.5-flash")

        prompt = f"""
        You are a supportive fitness coach.
        Give one short, motivating and practical fitness insight for user {username}.
        Keep it under 50 words. Do not use markdown.
        """

        response = model.generate_content(prompt)
        content = response.text.strip() if getattr(response, "text", None) else None

    except Exception as e:
        print(f"Vertex AI failed, using fallback: {e}")

    if not content:
        content = random.choice([
            "Your heart rate indicates you can push yourself further. You got this!",
            "You're doing great! Keep up the good work.",
            "You worked hard yesterday, take it easy today.",
            "You have burned 100 calories so far today!",
        ])

    image = None
    if random.random() < 0.5:
        image = "https://plus.unsplash.com/premium_photo-1669048780129-051d670fa2d1?q=80&w=3870&auto=format&fit=crop"

    return {
        "advice_id": f"advice_{user_id}_{int(datetime.now().timestamp())}",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "content": content,
        "image": image,
    }



def get_username(user_id, client=None):
    if client is None:
        client = bigquery.Client()

    query = f"""
        SELECT Username
        FROM amier-davis-hu.ISE.Users
        WHERE UserId = @user_id
        LIMIT 1
    """

    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("user_id", "STRING", user_id)
        ]
    )

    results = client.query(query, job_config=job_config).result()

    for row in results:
        return row.Username

    return "User"

