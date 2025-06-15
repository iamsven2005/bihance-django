#!/usr/bin/env bash

# Exit on any error 
set -e

# Install postgreSQL (on WSL side)
sudo apt update -y
sudo apt install postgresql-client -y 
sudo apt autoremove -y 


# Extract out database details, given database connection string
parse_pg_uri () {
    # Read from the first argument
    local uri="$1"

    : ' 
        SYNTAX GUIDE: 
        # or ## means removing the shortest/longest match of <pattern> 
        From the start

        % or %% means removing the shortest/longest match of <pattern> 
        From the end
    ' 
    # Remove the "postgresql://" prefix 
    local without_scheme=${uri#*://}

    # "user:pass@host:port"  
    local creds_and_host=${without_scheme%%/*}

    # "db?opts"
    local db_and_opts=${without_scheme#*/}

    # db
    DB_NAME=${db_and_opts%%\?*}                 

    # "user:pass"            
    local creds_part=${creds_and_host%@*}

    # "host:port"
    local host_part=${creds_and_host#*@}

    # user
    DB_USER=${creds_part%%:*}

    # pass
    DB_PASSWORD=${creds_part#*:}

    # Host may have ":port"
    if [[ "$host_part" == *:* ]]; then
        DB_HOST=${host_part%%:*}
        DB_PORT=${host_part##*:}
    else
        # default
        DB_HOST=$host_part
        DB_PORT=5432        
    fi

    # Export so dropdb/createdb can read them
    export DB_NAME DB_USER DB_PASSWORD DB_HOST DB_PORT
}


# Read from .env file 
ENV_FILE=".env"

if [[ ! -f $ENV_FILE ]]; then
    echo "❌  $ENV_FILE not found; aborting." >&2
    exit 1
fi

# Grab the first non-comment, non-blank DATABASE_URL= line
# -m1: Max one matching line 
# -E: Use extended regex
DATABASE_URL=$(    
    # Get first matching line
    grep -m1 -E '^[[:space:]]*DATABASE_URL=' "$ENV_FILE" \
    # Strip away leading space and the prefix
    | sed -E 's/^[[:space:]]*DATABASE_URL=//' 
)
if [[ -z $DATABASE_URL ]]; then
    echo "❌  DATABASE_URL is missing in $ENV_FILE; aborting." >&2
    exit 1
fi


# NOTE: db name should be LOWERCASE
# Since PostgreSQL operations tend to assume lowercase anyways 
parse_pg_uri "$DATABASE_URL"

# Sanity check
echo "DB_NAME=$DB_NAME"
echo "DB_USER=$DB_USER"
echo "DB_PASSWORD=$DB_PASSWORD"
echo "DB_HOST=$DB_HOST"
echo "DB_PORT=$DB_PORT"


# For AWS Neon hosted DBs specifically
# Require SSL + Password
export PGSSLMODE=require          
export PGPASSWORD="$DB_PASSWORD"  

# Drop and Recreate DB (force)
echo "Dropping & creating PostgreSQL database $DB_NAME..."
dropdb --if-exists --force \
       --host="$DB_HOST" --port="$DB_PORT" --username="$DB_USER" "$DB_NAME"
createdb --host="$DB_HOST" --port="$DB_PORT" --username="$DB_USER" \
         --template=template0 --encoding=UTF8 "$DB_NAME"


# Remove migrations folder (for OUR apps only)
rm -rf applications/migrations
rm -rf availabilities/migrations  
rm -rf companies/migrations
rm -rf employer/migrations
rm -rf files/migrations
rm -rf groups/migrations
rm -rf jobs/migrations
rm -rf message/migrations
rm -rf reviews/migrations
rm -rf suggestions/migrations
rm -rf users/migrations


# Recreate migrations
# Absolute path to the Windows venv’s Python
PYWIN="/mnt/c/bihance/bihance-django/bihance/venv/Scripts/python.exe"

# Make migrations
"$PYWIN" manage.py makemigrations \
    applications availabilities companies employer files \
    groups jobs message reviews suggestions users

# Apply them
"$PYWIN" manage.py migrate


# # Load some initial data (using Django fixtures)
# # TODO in future
