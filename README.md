# Donut MCP Server

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Docker](https://img.shields.io/badge/docker-ready-blue.svg)](https://www.docker.com/)

Official Implementation of OCR-free Document Understanding Transformer (Donut) and Synthetic Document Generator (SynthDoG) with Model Context Protocol (MCP) Server support.

## 🚀 Features

- **FastAPI-based MCP Server**: Modern, high-performance API server for document processing
- **OCR-free Document Understanding**: Process documents without traditional OCR
- **Multiple Input Methods**: Support for file uploads, file paths, and batch processing
- **Docker Ready**: Complete containerization with Docker and Docker Compose
- **Production Ready**: Nginx reverse proxy, Redis caching, and SSL support
- **Health Monitoring**: Built-in health checks and monitoring endpoints
- **Rate Limiting**: API rate limiting and security features

## 📋 Prerequisites

- Python 3.9+
- Docker and Docker Compose
- CUDA-capable GPU (optional, for faster inference)

## 🛠️ Installation

### Option 1: Docker (Recommended)

1. **Clone the repository**
   ```bash
   git clone https://github.com/seongyeon1/donut.git
   cd donut
   ```

2. **Run with Docker Compose**
   ```bash
   # Development mode
   ./run-docker.sh --dev
   
   # Production mode (with nginx and redis)
   ./run-docker.sh --production
   ```

3. **Access the server**
   - Server: http://localhost:8000
   - API Docs: http://localhost:8000/docs
   - Health Check: http://localhost:8000/health

### Option 2: Local Development

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the server**
   ```bash
   python app.py
   ```

## 🐳 Docker Commands

```bash
# Build images
./run-docker.sh --build

# Start services
./run-docker.sh --dev

# Production mode
./run-docker.sh --production

# Stop services
./run-docker.sh --stop

# View logs
./run-docker.sh --logs

# Test API
./run-docker.sh --test
```

## 📚 API Endpoints

### Core Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Server information and available endpoints |
| `GET` | `/health` | Health check and system status |
| `POST` | `/process/file` | Process uploaded image file |
| `POST` | `/process/paths` | Process images from file paths |
| `POST` | `/process/batch` | Batch process multiple images |

### Request Examples

**Process uploaded file:**
```bash
curl -X POST "http://localhost:8000/process/file" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@example.jpg"
```

**Process by file path:**
```bash
curl -X POST "http://localhost:8000/process/paths" \
  -H "accept: application/json" \
  -H "Content-Type: application/json" \
  -d '{"image_paths": ["examples/example1.jpg"]}'
```

**Health check:**
```bash
curl "http://localhost:8000/health"
```

## ⚙️ Configuration

### Environment Variables

Create a `.env` file based on `.env.example`:

```bash
# Model Configuration
MODEL_NAME=naver-clova-ix/donut-base-finetuned-cord-v2
DEVICE=auto  # auto, cuda, cpu

# Server Configuration
HOST=0.0.0.0
PORT=8000
WORKERS=1

# API Configuration
RATE_LIMIT=100
UPLOAD_MAX_SIZE=50
```

### Configuration Files

- `config/server.yaml`: Server configuration
- `docker-compose.yml`: Docker services configuration
- `nginx.conf`: Nginx reverse proxy configuration

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Client App    │───▶│   Nginx Proxy    │───▶│  Donut MCP      │
│                 │    │   (Optional)     │    │   Server        │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │                        │
                                ▼                        ▼
                       ┌──────────────────┐    ┌─────────────────┐
                       │   Redis Cache    │    │   Donut Model   │
                       │   (Optional)     │    │                 │
                       └──────────────────┘    └─────────────────┘
```

## 🔧 Development

### Project Structure

```
donut/
├── app.py                 # Main FastAPI application
├── Dockerfile            # Docker image definition
├── docker-compose.yml    # Docker services configuration
├── requirements.txt      # Python dependencies
├── run-docker.sh        # Docker management script
├── nginx.conf           # Nginx configuration
├── config/              # Configuration files
│   └── server.yaml     # Server settings
├── examples/            # Example images
├── models/              # Custom model files
└── output/              # Processing results
```

### Adding New Features

1. **Update app.py**: Add new endpoints and logic
2. **Update requirements.txt**: Add new dependencies
3. **Update Dockerfile**: Modify container configuration if needed
4. **Test locally**: Run with `./run-docker.sh --test`
5. **Commit changes**: Follow Git workflow

## 🧪 Testing

### API Testing

```bash
# Test health endpoint
curl http://localhost:8000/health

# Test file processing
curl -X POST http://localhost:8000/process/file \
  -F "file=@examples/example1.jpg"

# Test batch processing
curl -X POST http://localhost:8000/process/paths \
  -H "Content-Type: application/json" \
  -d '{"image_paths": ["examples/example1.jpg", "examples/example2.jpg"]}'
```

### Load Testing

```bash
# Install Apache Bench
sudo apt-get install apache2-utils

# Test with 100 requests, 10 concurrent
ab -n 100 -c 10 http://localhost:8000/health
```

## 🚀 Production Deployment

### Production Mode

```bash
# Start with production profile
./run-docker.sh --production

# Or manually
docker-compose --profile production up -d
```

### SSL Configuration

1. **Generate SSL certificates**
   ```bash
   mkdir -p ssl
   openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
     -keyout ssl/key.pem -out ssl/cert.pem
   ```

2. **Enable SSL in nginx.conf**
   ```nginx
   listen 443 ssl http2;
   ssl_certificate /etc/nginx/ssl/cert.pem;
   ssl_certificate_key /etc/nginx/ssl/key.pem;
   ```

### Monitoring

- **Health checks**: `/health` endpoint
- **Logs**: `docker-compose logs -f`
- **Metrics**: Container resource usage
- **Uptime**: Docker health checks

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Clova AI](https://clova.ai/) for the original Donut implementation
- [FastAPI](https://fastapi.tiangolo.com/) for the web framework
- [Docker](https://www.docker.com/) for containerization

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/seongyeon1/donut/issues)
- **Discussions**: [GitHub Discussions](https://github.com/seongyeon1/donut/discussions)
- **Documentation**: [API Docs](http://localhost:8000/docs) (when server is running)

---

**Made with ❤️ for the AI community**
