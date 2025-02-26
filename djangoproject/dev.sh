#!/bin/bash

# Development script for managing the local environment

# Color definitions
GREEN='[0;32m'
BLUE='[0;34m'
YELLOW='[1;33m'
RED='[0;31m'
NC='[0m' # No Color

# Project name from config
PROJECT_NAME=$(grep PROJECT_NAME ./devtool.config | cut -d= -f2)

function show_help {
    echo -e "${BLUE}Development Environment Helper${NC}"
    echo ""
    echo "Usage:"
    echo "  ./dev.sh [command]"
    echo ""
    echo "Commands:"
    echo "  start       - Start all services (Django and NextJS)"
    echo "  stop        - Stop all running services"
    echo "  restart     - Restart all services"
    echo "  frontend    - Start only the NextJS frontend"
    echo "  backend     - Start only the Django backend"
    echo "  logs        - Show logs from all services"
    echo "  install     - Install dependencies for both frontend and backend"
    echo "  migrate     - Run Django migrations"
    echo "  shell       - Start Django shell"
    echo "  test        - Run tests for both frontend and backend"
    echo "  help        - Show this help message"
}

function start_services {
    echo -e "${GREEN}Starting development services...${NC}"
    docker-compose -f docker-compose.dev.yml up -d
    echo -e "${GREEN}Services started!${NC}"
    echo -e "Frontend: ${YELLOW}http://localhost:3000${NC}"
    echo -e "Backend API: ${YELLOW}http://localhost:8000/api${NC}"
    echo -e "Django Admin: ${YELLOW}http://localhost:8000/admin${NC}"
}

function stop_services {
    echo -e "${YELLOW}Stopping all services...${NC}"
    docker-compose -f docker-compose.dev.yml down
}

function start_frontend {
    echo -e "${GREEN}Starting NextJS frontend...${NC}"
    cd frontend && npm run dev
}

function start_backend {
    echo -e "${GREEN}Starting Django backend...${NC}"
    cd $PROJECT_NAME && python manage.py runserver 0.0.0.0:8000
}

function show_logs {
    echo -e "${BLUE}Showing logs... (Ctrl+C to exit)${NC}"
    docker-compose -f docker-compose.dev.yml logs -f
}

function install_deps {
    echo -e "${GREEN}Installing backend dependencies...${NC}"
    pip install -r $PROJECT_NAME/requirements.txt
    
    echo -e "${GREEN}Installing frontend dependencies...${NC}"
    cd frontend && npm install
    cd ..
}

function run_migrations {
    echo -e "${GREEN}Running Django migrations...${NC}"
    cd $PROJECT_NAME && python manage.py migrate
}

function django_shell {
    echo -e "${GREEN}Starting Django shell...${NC}"
    cd $PROJECT_NAME && python manage.py shell
}

function run_tests {
    echo -e "${GREEN}Running backend tests...${NC}"
    cd $PROJECT_NAME && python manage.py test
    
    echo -e "${GREEN}Running frontend tests...${NC}"
    cd frontend && npm test
}

# Main command router
case "$1" in
    start)
        start_services
        ;;
    stop)
        stop_services
        ;;
    restart)
        stop_services
        start_services
        ;;
    frontend)
        start_frontend
        ;;
    backend)
        start_backend
        ;;
    logs)
        show_logs
        ;;
    install)
        install_deps
        ;;
    migrate)
        run_migrations
        ;;
    shell)
        django_shell
        ;;
    test)
        run_tests
        ;;
    help|*)
        show_help
        ;;
esac
