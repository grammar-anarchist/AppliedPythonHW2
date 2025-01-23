from dataclasses import dataclass
from typing import List, Dict, Any
from datetime import datetime
import asyncpg

from api_requests import water_goal_func, calories_goal_func

DB_CONFIG = {
    'database': 'calories_db',
    'user': 'postgres',
    'password': 'password',
    'host': 'localhost',
    'port': '5432'
}

@dataclass
class Session:
    pool : asyncpg.pool.Pool = None
    
    async def start_session(self):
        if self.pool is None:
            self.pool = await asyncpg.create_pool(**DB_CONFIG)

    async def close_session(self):
        if self.pool is not None:
            await self.pool.close()
            self.pool = None
    
    async def check_user(self, user_id: int, raise_error: bool = False):
        query = "SELECT EXISTS(SELECT 1 FROM users WHERE user_id = $1)"
        
        async with self.pool.acquire() as connection:
            user_exists = await connection.fetchval(query, user_id)

        if raise_error and not user_exists:
            raise ValueError(f"User with ID {user_id} does not exist.")

        return user_exists

    async def get_columns(self, user_id: int, columns: List[str]):
        async with self.pool.acquire() as connection:
            user_data = await connection.fetchrow(
                """
                    SELECT {columns}
                    FROM users
                    WHERE user_id = $1
                """.format(columns=', '.join(columns)),
                user_id
            )
        
        return [user_data[column] for column in columns]
    
    async def update_columns(self, user_id: int, columns: Dict[str, Any]):
        async with self.pool.acquire() as connection:
            await connection.execute(
                """
                    UPDATE users
                    SET {columns},
                        last_logged = CURRENT_TIMESTAMP
                    WHERE user_id = $1
                """.format(columns=', '.join(f"{key} = ${i + 2}" for i, key in enumerate(columns))),
                user_id, *columns.values()
            )
    
    async def create_user(self, user_id: int, weight: int, height: int, age: int, activity: int, city: str, water_goal: int, calorie_goal: int):
        async with self.pool.acquire() as connection:
            await connection.execute("""
                INSERT INTO users (
                    user_id, weight, height, age, activity, city, 
                    water_goal, calorie_goal
                ) VALUES (
                    $1, $2, $3, $4, $5, $6, 
                    $7, $8
                )
            """, 
            user_id, weight, height, age, activity, city, water_goal, calorie_goal
            )

    async def add_user(self, user_id: int, weight: int, height: int, 
                       age: int, activity: int, city: str,
                       water_goal: int, calories_goal: int
        ):
        user_exists = await self.check_user(user_id)

        if user_exists:
            await self.update_columns(user_id, 
                {'weight': weight, 'height': height, 'age': age, 
                'activity': activity, 'city': city, 
                'calorie_goal': calories_goal, 'water_goal': water_goal,
                'logged_water': 0, 'logged_calories': 0, 'burned_calories': 0}
            )
            
        else:
            await self.create_user(
                user_id, weight, height, age, activity, city, water_goal, calories_goal
            )
    
    async def update_water_goal(self, user_id: int):
        weight, city = await self.get_columns(user_id, ['weight', 'city'])

        water_goal = await water_goal_func(weight, city)
        await self.update_columns(user_id, {'water_goal': water_goal, 'logged_water': 0})

        return water_goal

    async def add_water(self, user_id: int, water: int):
        await self.check_user(user_id, raise_error=True)

        logged_water, water_goal, last_logged = await self.get_columns(user_id, 
            ['logged_water', 'water_goal', 'last_logged']
        )

        today = datetime.now().date()
        last_logged_date = last_logged.date()

        if today != last_logged_date:
            water_goal = await self.update_water_goal(user_id)
            logged_water = 0

        logged_water += water
        await self.update_columns(user_id, {'logged_water': logged_water})

        remaining = water_goal - logged_water
        return remaining

    async def add_calories(self, user_id: int, calories: int):
        await self.check_user(user_id, raise_error=True)

        logged_calories, calorie_goal, last_logged = await self.get_columns(user_id, 
            ['logged_calories', 'calorie_goal', 'last_logged']
        )

        today = datetime.now().date()
        last_logged_date = last_logged.date()

        if today != last_logged_date:
            logged_calories = 0

        logged_calories += calories
        await self.update_columns(user_id, {'logged_calories': logged_calories})

        remaining = calorie_goal - logged_calories
        return remaining

    async def log_training(self, user_id: int, water: int, calories: int):
        await self.check_user(user_id, raise_error=True)

        water_goal, burned_calories, last_logged = await self.get_columns(user_id, 
            ['water_goal', 'burned_calories', 'last_logged']
        )

        today = datetime.now().date()
        last_logged_date = last_logged.date()

        if today != last_logged_date:
            water_goal = await self.update_water_goal(user_id)
            burned_calories = 0

        water_goal += water
        burned_calories += calories

        await self.update_columns(user_id, 
            {'water_goal': water_goal, 'burned_calories': burned_calories}
        )

    async def get_progress(self, user_id: int):
        await self.check_user(user_id, raise_error=True)

        return await self.get_columns(user_id, 
            ['calorie_goal', 'logged_calories', 'burned_calories', 'water_goal', 'logged_water']
        )

db = Session()
