CREATE TABLE bg (
    bg_id int PRIMARY KEY,
    title text,
    description text,
    released int,
    rating double precision,
    num_ratings int,
    min_playtime int,
    max_playtime int,
    min_players int,
    max_players int,
    expansion_of int REFERENCES bg(bg_id)
);

CREATE TABLE ratingsperplayer (
    bg_id int REFERENCES bg(bg_id),
    players int,
    rating double precision,
    PRIMARY KEY (bg_id, players)
);

CREATE TABLE users (
    email text PRIMARY KEY,
    password text,
    name text
);

CREATE TABLE publishers (
    pub_id int PRIMARY KEY,
    publisher text,
    description text
);

CREATE TABLE mechanics (
    mech_id int PRIMARY KEY,
    mechanic text,
    description text
);

CREATE TABLE families (
    fam_id int PRIMARY KEY,
    family text,
    description text
);

CREATE TABLE categories (
    cat_id int PRIMARY KEY,
    category text,
    description text
);

CREATE TABLE people (
    p_id int PRIMARY KEY,
    name text
);

CREATE TABLE publishersrel (
    bg_id int REFERENCES bg(bg_id),
    pub_id int REFERENCES publishers(pub_id),
    PRIMARY KEY (bg_id, pub_id)
);

CREATE TABLE mechanicsrel (
    bg_id int REFERENCES bg(bg_id),
    mech_id int REFERENCES mechanics(mech_id),
    PRIMARY KEY (bg_id, mech_id)
);

CREATE TABLE familiesrel (
    bg_id int REFERENCES bg(bg_id),
    fam_id int REFERENCES families(fam_id),
    PRIMARY KEY (bg_id, fam_id)
);

CREATE TABLE categoriesrel (
    bg_id int REFERENCES bg(bg_id),
    cat_id int REFERENCES categories(cat_id),
    PRIMARY KEY (bg_id, cat_id)
);

CREATE TABLE artistrel (
    bg_id int REFERENCES bg(bg_id),
    p_id int REFERENCES people(p_id),
    PRIMARY KEY (bg_id, p_id)
);

CREATE TABLE designerrel (
    bg_id int REFERENCES bg(bg_id),
    p_id int REFERENCES people(p_id),
    PRIMARY KEY (bg_id, p_id)
);

CREATE TABLE owns (
    bg_id int REFERENCES bg(bg_id),
    email text REFERENCES users(email),
    PRIMARY KEY (bg_id, email)
);

CREATE TABLE played (
    bg_id int REFERENCES owns(bg_id),
    email text REFERENCES owns(email),
    session_id int,
    date date,
    time_played int,
    players int,
    winner text,
    PRIMARY KEY (bg_id, email, session_id)
);
