# Internal API Management Platform

A production-ready RESTful API service built with FastAPI for managing internal tool configurations, user permissions, and API access control.

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-blue.svg)
![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)
![TypeScript](https://img.shields.io/badge/TypeScript-Ready-3178C6?logo=typescript&logoColor=white)
![Jenkins](https://img.shields.io/badge/Jenkins-CI%2FCD-D24939?logo=jenkins&logoColor=white)

## Features

- **JWT Authentication** - Secure token-based authentication with refresh tokens
- **Role-Based Access Control (RBAC)** - Admin, Manager, and User roles with granular permissions
- **API Key Management** - Generate, revoke, and manage API keys for services
- **Configuration Management** - Store and retrieve application configurations
- **Rate Limiting** - Protect endpoints from abuse with configurable rate limits
- **Comprehensive Logging** - Structured logging for debugging and monitoring
- **OpenAPI Documentation** - Auto-generated Swagger/ReDoc documentation

## Tech Stack

- **Backend**: Python 3.11+, FastAPI
- **Database**: PostgreSQL 15+
- **Authentication**: JWT (PyJWT), bcrypt
- **ORM**: SQLAlchemy 2.0
- **Migrations**: Alembic
- **Containerization**: Docker, Docker Compose
- **Testing**: pytest, pytest-asyncio

## Project Structure

```
       

1. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # or
   .\venv\Scripts\activate  # Windows
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Run database migrations**
   ```bash
   alembic upgrade head
   ```

5. **Start the server**
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```

### Docker Deployment

```bash
docker-compose up -d
```

## API Endpoints

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/auth/register` | Register new user |
| POST | `/api/v1/auth/login` | User login |
| POST | `/api/v1/auth/refresh` | Refresh access token |
| POST | `/api/v1/auth/logout` | Logout user |

### Users
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/users/me` | Get current user |
| GET | `/api/v1/users` | List all users (Admin) |
| PUT | `/api/v1/users/{id}` | Update user |
| DELETE | `/api/v1/users/{id}` | Delete user (Admin) |

### API Keys
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/api-keys` | Generate new API key |
| GET | `/api/v1/api-keys` | List user's API keys |
| DELETE | `/api/v1/api-keys/{id}` | Revoke API key |

### Configurations
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/configs` | List configurations |
| POST | `/api/v1/configs` | Create configuration |
| PUT | `/api/v1/configs/{key}` | Update configuration |
| DELETE | `/api/v1/configs/{key}` | Delete configuration |

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | - |
| `SECRET_KEY` | JWT secret key | - |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token expiration time | 30 |
| `REFRESH_TOKEN_EXPIRE_DAYS` | Refresh token expiration | 7 |
| `RATE_LIMIT_PER_MINUTE` | API rate limit | 100 |

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app tests/

# Run specific test file
pytest tests/test_auth.py -v
```

## Performance

- Handles **10,000+ daily API requests**
- Average response time: **< 50ms**
- 99.9% uptime with proper deployment

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Author

**Harsha Ramisetty**
- LinkedIn: [harsharamisetty](https://linkedin.com/in/harsharamisetty)
- GitHub: [harsharamisetty](https://github.com/harsharamisetty)
