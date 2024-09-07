#!/bin/bash

# Function to generate a new Alembic revision
generate_revision() {
    echo "Generating new Alembic revision..."
    alembic revision --autogenerate -m "$1"
    if [ $? -eq 0 ]; then
        echo "Revision generated successfully."
    else
        echo "Failed to generate revision."
        exit 1
    fi
}

# Function to apply Alembic migrations
apply_migrations() {
    echo "Applying Alembic migrations..."
    alembic upgrade head
    if [ $? -eq 0 ]; then
        echo "Migrations applied successfully."
    else
        echo "Failed to apply migrations."
        exit 1
    fi
}

# Function to downgrade Alembic migrations by revision ID
downgrade_migration() {
    echo "Downgrading Alembic migration to $1..."
    alembic downgrade "$1"
    if [ $? -eq 0 ]; then
        echo "Migration downgraded successfully."
    else
        echo "Failed to downgrade migration."
        exit 1
    fi
}

# Function to downgrade the last Alembic migration
downgrade_last_migration() {
    echo "Downgrading the last Alembic migration..."
    alembic downgrade -1
    if [ $? -eq 0 ]; then
        echo "Last migration downgraded successfully."
    else
        echo "Failed to downgrade the last migration."
        exit 1
    fi
}

# Function to repopulate the database from migration history
repopulate_database() {
    echo "Dropping alembic version table (if it exists)..."
    alembic downgrade base  # Downgrade to base to potentially drop alembic_version

    echo "Repopulating database from migration history..."
    alembic upgrade head
    if [ $? -eq 0 ]; then
        echo "Database repopulated successfully."
    else
        echo "Failed to repopulate database."
        exit 1
    fi
}

# Function to show all Alembic migrations
show_migrations() {
    echo "Listing all Alembic migrations..."
    alembic history
    if [ $? -eq 0 ]; then
        echo "Migrations listed successfully."
    else
        echo "Failed to list migrations."
        exit 1
    fi
}

# Print usage instructions
usage() {
    echo "Usage: $0 [option] \"<revision message>\""
    echo "Options:"
    echo "  -r, --revision    Generate a new Alembic revision"
    echo "                    Requires a revision message."
    echo "                    Example: $0 -r \"Added new column to users table\""
    echo "  -a, --apply       Apply Alembic migrations"
    echo "                    Applies all pending migrations."
    echo "  -d, --downgrade   Downgrade Alembic migration by revision ID"
    echo "                    Example: $0 -d <revision_id>"
    echo "  -l, --last        Downgrade the last Alembic migration"
    echo "                    Example: $0 -l"
    echo "  -s, --show        Show all Alembic migrations"
    echo "                    Example: $0 -s"
    echo "  -p, --populate    Repopulate the database from migration history"
    echo "                    (After dropping tables)"
    echo "  -b, --both        Generate a new revision and apply migrations"
    echo "                    Requires a revision message."
    echo "                    Example: $0 -b \"Added new column to users table\""
    echo "  -h, --help        Show this help message and exit"
    exit 1
}

# Check if at least one argument is provided
if [ $# -lt 1 ]; then
    usage
fi

# Parse command-line options
case "$1" in
    -r|--revision)
        if [ -z "$2" ]; then
            echo "Please provide a revision message."
            echo "Usage: $0 -r \"<revision message>\""
            exit 1
        fi
        generate_revision "$2"
        ;;
    -a|--apply)
        apply_migrations
        ;;
    -d|--downgrade)
        if [ -z "$2" ]; then
            echo "Please provide a revision ID."
            echo "Usage: $0 -d <revision_id>"
            exit 1
        fi
        downgrade_migration "$2"
        ;;
    -l|--last)
        downgrade_last_migration
        ;;
    -s|--show)
        show_migrations
        ;;
    -b|--both)
        if [ -z "$2" ]; then
            echo "Please provide a revision message."
            echo "Usage: $0 -b \"<revision message>\""
            exit 1
        fi
        generate_revision "$2"
        apply_migrations
        ;;
    -h|--help)
        usage
        ;;
    *)
        usage
        ;;
esac
