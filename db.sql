CREATE TABLE users(
    id SERIAL NOT NULL,
    full_name VARCHAR(50) NOT NULL,
    email VARCHAR(50),
    username VARCHAR(50) UNIQUE NOT NULL,
    mobile INT,
    user_id VARCHAR PRIMARY KEY
);

CREATE TABLE profile(
    user_id VARCHAR ,
    profile_picture BYTEA NOT NULL,
    CONSTRAINT frgn_key FOREIGN KEY(user_id) REFERENCES users(user_id)
);
