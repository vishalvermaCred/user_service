# user_service
This service is used to store the user details while signing up on a website

this service contains 4 APIs in total

**routes information:** 
<br/>
/user/signup
this API stores user details in Postgres
it stores the profile picture in the profile table in Postgres and the rest details in the users table in Postgres

/user/user_details
this API fetches user details in Postgres
it fetches the profile picture from the profile table in Postgres and the rest details from the users table in Postgres with join

/user/signup/v2
this API stores user details in Postgres and MongoDB
it stores the profile picture in the profile_mongo table in MongoDB and the rest details in the users_mongo table in Postgres

/user/user_details/v2
this API fetches user details in Postgres
it fetches the profile picture from the profile_mongo table in MongoDB and the rest details from the users_mongo table in Postgres


**steps to run**
<br/>
create a .env file following the .env_example file
start the uvicorn server by running the command: uvicorn app.server:app
start using the APIs
