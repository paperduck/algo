
Steps:

- Run MySQL batch script to create stored program that DROPs table.

- Call that stored program, passing in a table name.

- Run MySQL batch script to create stored program that CREATEs table.

- Call that stored program, passing in a table name.

- Run the bash script that loads CSV files into that table.

