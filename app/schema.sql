CREATE DATABASE slackbot OWNER root;

CREATE TABLE users (
  slack_user_id   varchar(15) PRIMARY KEY,
  synapse_user_id varchar(30) UNIQUE NOT NULL,
  debit_node_id   varchar(30) UNIQUE NOT NULL,
  savings_node_id varchar(30) UNIQUE NOT NULL
);

CREATE TABLE recurring_transactions (
  id            serial PRIMARY KEY,
  amount        integer NOT NULL,
  periodicity   decimal NOT NULL,
  slack_user_id varchar(15) NOT NULL REFERENCES users(slack_user_id)
);
