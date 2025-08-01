# Quiz App

## Overview

This is a Flask-based educational quiz application that generates AI-powered multiple-choice questions using Google's Gemini API. Students can create personalized quizzes on any topic, take the quiz with an interactive interface, and review their performance with detailed analytics. The application tracks quiz history and provides comprehensive feedback to help students learn from their mistakes.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Backend Architecture
- **Framework**: Flask web framework with SQLAlchemy ORM for database operations
- **Database**: SQLite for development with PostgreSQL support via environment configuration
- **API Integration**: Google Gemini 2.5 Flash model for AI-powered question generation
- **Session Management**: Flask sessions for maintaining quiz state across requests

### Data Model Design
- **QuizSession**: Tracks individual quiz attempts with student info, topic, timing, and scoring
- **Question**: Stores generated questions with multiple-choice options, correct answers, and student responses
- **Relationship**: One-to-many between QuizSession and Questions with cascade deletion

### Frontend Architecture
- **Template Engine**: Jinja2 templating with Bootstrap 5 for responsive UI
- **Theme**: Replit dark theme integration for consistent styling
- **JavaScript**: Vanilla JS for form validation, topic suggestions, and interactive quiz features
- **Visualization**: Chart.js for performance analytics and score visualization

### Question Generation System
- **Pydantic Models**: Structured data validation for quiz questions and responses
- **JSON Schema**: Enforced response format from Gemini API for consistent question structure
- **Error Handling**: Robust error management for AI API failures and malformed responses

### Security and Configuration
- **Environment Variables**: Sensitive data like API keys and database URLs stored in environment
- **Proxy Middleware**: ProxyFix for proper handling of reverse proxy headers
- **Session Security**: Configurable session secrets with development defaults

## External Dependencies

### AI Services
- **Google Gemini API**: Primary service for generating educational quiz questions with structured JSON responses

### Frontend Libraries
- **Bootstrap 5**: UI framework with Replit dark theme customization
- **Chart.js**: Interactive charts for quiz performance visualization
- **Font Awesome**: Icon library for enhanced user interface elements

### Database
- **SQLite**: Default development database with automatic table creation
- **PostgreSQL**: Production database support via DATABASE_URL environment variable

### Python Packages
- **Flask**: Web framework with SQLAlchemy extension for database operations
- **Google GenAI**: Official Google Generative AI client library
- **Pydantic**: Data validation and serialization for API responses
- **Werkzeug**: WSGI utilities including ProxyFix middleware

### Development Tools
- **Logging**: Built-in Python logging for debugging and monitoring
- **Hot Reload**: Flask development server with debug mode enabled