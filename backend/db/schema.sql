CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    password_salt VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE tokens (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id) ON DELETE CASCADE,
    token VARCHAR(255) UNIQUE NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE image_batches (
    id SERIAL PRIMARY KEY,
    batch_name VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE images (
    id SERIAL PRIMARY KEY,
    file_path VARCHAR(255) NOT NULL,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
);

CREATE TABLE tex_codes (
    id SERIAL PRIMARY KEY,
    code TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE user_image_map (
    user_id INT,
    image_id INT,
    PRIMARY KEY (user_id, image_id),
);

CREATE TABLE batch_image_map (
    batch_id INT,
    image_id INT,
    PRIMARY KEY (batch_id, image_id),
);

CREATE TABLE user_batches_map (
    user_id INT,
    batch_id INT,
    PRIMARY KEY (user_id, batch_id),
);

CREATE TABLE user_tex_map (
    user_id INT,
    tex_code_id INT,
    PRIMARY KEY (user_id, tex_code_id),
);