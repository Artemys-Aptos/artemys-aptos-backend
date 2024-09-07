#!/bin/bash

# Function to pull the latest changes for the current branch
pull_changes() {
    echo "Pulling latest changes for the current branch..."
    git pull
    if [ $? -eq 0 ]; then
        echo "Changes pulled successfully."
    else
        echo "Failed to pull changes."
        exit 1
    fi
}

# Function to push changes for the current branch
push_changes() {
    echo "Pushing changes for the current branch..."
    git push
    if [ $? -eq 0 ]; then
        echo "Changes pushed successfully."
    else
        echo "Failed to push changes."
        exit 1
    fi
}

# Function to merge a branch into the current branch
merge_branch() {
    echo "Merging branch $1 into the current branch..."
    git merge "$1"
    if [ $? -eq 0 ]; then
        echo "Branch $1 merged successfully."
    else
        echo "Failed to merge branch $1."
        exit 1
    fi
}

# Function to switch to a branch
switch_branch() {
    echo "Switching to branch $1..."
    git checkout "$1"
    if [ $? -eq 0 ]; then
        echo "Switched to branch $1 successfully."
    else
        echo "Failed to switch to branch $1."
        exit 1
    fi
}

# Function to create a new branch and switch to it
create_branch() {
    echo "Creating and switching to new branch $1..."
    git checkout -b "$1"
    if [ $? -eq 0 ]; then
        echo "New branch $1 created and switched to successfully."
    else
        echo "Failed to create and switch to branch $1."
        exit 1
    fi
}

# Function to show the current branch
show_current_branch() {
    echo "Current branch is: $(git branch --show-current)"
}

# Function to list all branches
list_branches() {
    echo "Listing all branches..."
    git branch -a
    if [ $? -eq 0 ]; then
        echo "Branches listed successfully."
    else
        echo "Failed to list branches."
        exit 1
    fi
}

# Print usage instructions
usage() {
    echo "Usage: $0 [option] <branch_name>"
    echo "Options:"
    echo "  -p, --pull        Pull the latest changes for the current branch"
    echo "                    Example: $0 -p"
    echo "  -u, --push        Push changes for the current branch"
    echo "                    Example: $0 -u"
    echo "  -m, --merge       Merge a specified branch into the current branch"
    echo "                    Example: $0 -m <branch_name>"
    echo "  -c, --checkout    Switch to a specified branch"
    echo "                    Example: $0 -c <branch_name>"
    echo "  -n, --new-branch  Create and switch to a new branch"
    echo "                    Example: $0 -n <branch_name>"
    echo "  -s, --show        Show the current branch"
    echo "                    Example: $0 -s"
    echo "  -l, --list        List all branches"
    echo "                    Example: $0 -l"
    echo "  -h, --help        Show this help message and exit"
    exit 1
}

# Check if at least one argument is provided
if [ $# -lt 1 ]; then
    usage
fi

# Parse command-line options
case "$1" in
    -p|--pull)
        pull_changes
        ;;
    -u|--push)
        push_changes
        ;;
    -m|--merge)
        if [ -z "$2" ]; then
            echo "Please provide a branch name to merge."
            echo "Usage: $0 -m <branch_name>"
            exit 1
        fi
        merge_branch "$2"
        ;;
    -c|--checkout)
        if [ -z "$2" ]; then
            echo "Please provide a branch name to switch to."
            echo "Usage: $0 -c <branch_name>"
            exit 1
        fi
        switch_branch "$2"
        ;;
    -n|--new-branch)
        if [ -z "$2" ]; then
            echo "Please provide a name for the new branch."
            echo "Usage: $0 -n <branch_name>"
            exit 1
        fi
        create_branch "$2"
        ;;
    -s|--show)
        show_current_branch
        ;;
    -l|--list)
        list_branches
        ;;
    -h|--help)
        usage
        ;;
    *)
        usage
        ;;
esac
