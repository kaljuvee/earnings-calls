# Deployment Guide - Earnings Call Analyzer

This guide provides instructions for deploying the Earnings Call Analyzer application to various platforms.

---

## Table of Contents

1. [Local Deployment](#local-deployment)
2. [Streamlit Cloud Deployment](#streamlit-cloud-deployment)
3. [Docker Deployment](#docker-deployment)
4. [AWS Deployment](#aws-deployment)
5. [Environment Variables](#environment-variables)
6. [Production Considerations](#production-considerations)

---

## Local Deployment

### Prerequisites

- Python 3.11 or higher
- pip package manager
- Git

### Steps

1. **Clone the repository:**
```bash
git clone https://github.com/kaljuvee/earnings-calls.git
cd earnings-calls
```

2. **Create virtual environment (recommended):**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Configure environment variables:**
```bash
cp .env.sample .env
# Edit .env with your API keys
```

Required API keys:
- `XAI_API_KEY` - XAI API key
- `GOOGLE_API_KEY` - Google Gemini API key
- `API_NINJAS_KEY` - API Ninjas API key

5. **Run the application:**
```bash
streamlit run Home.py
```

6. **Access the application:**
Open your browser to `http://localhost:8501`

---

## Streamlit Cloud Deployment

Streamlit Cloud is the easiest way to deploy Streamlit applications.

### Prerequisites

- GitHub account
- Streamlit Cloud account (free at [share.streamlit.io](https://share.streamlit.io))

### Steps

1. **Push code to GitHub:**
```bash
git remote add origin https://github.com/YOUR_USERNAME/earnings-calls.git
git push -u origin main
```

2. **Deploy on Streamlit Cloud:**
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Click "New app"
   - Select your repository: `YOUR_USERNAME/earnings-calls`
   - Set main file path: `Home.py`
   - Click "Deploy"

3. **Configure Secrets:**
   - In Streamlit Cloud dashboard, go to app settings
   - Click "Secrets"
   - Add your environment variables in TOML format:

```toml
XAI_API_KEY = "your-xai-api-key"
GOOGLE_API_KEY = "your-google-api-key"
API_NINJAS_KEY = "your-fmp-api-key"
```

4. **Access your app:**
Your app will be available at: `https://YOUR_USERNAME-earnings-calls.streamlit.app`

### Advantages

- ✅ Free hosting for public repositories
- ✅ Automatic deployments on git push
- ✅ Built-in secrets management
- ✅ No server management required

### Limitations

- ⚠️ Limited resources (1 GB RAM, 1 CPU core)
- ⚠️ Apps sleep after inactivity
- ⚠️ Not suitable for high-traffic production use

---

## Docker Deployment

Deploy using Docker for consistent environments.

### Create Dockerfile

Create `Dockerfile` in the project root:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Create necessary directories
RUN mkdir -p transcripts test-results

# Expose Streamlit port
EXPOSE 8501

# Health check
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

# Run Streamlit
ENTRYPOINT ["streamlit", "run", "Home.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

### Create docker-compose.yml

```yaml
version: '3.8'

services:
  streamlit:
    build: .
    ports:
      - "8501:8501"
    environment:
      - XAI_API_KEY=${XAI_API_KEY}
      - GOOGLE_API_KEY=${GOOGLE_API_KEY}
      - API_NINJAS_KEY=${API_NINJAS_KEY}
    volumes:
      - ./transcripts:/app/transcripts
      - ./test-results:/app/test-results
    restart: unless-stopped
```

### Build and Run

```bash
# Build the image
docker build -t earnings-call-analyzer .

# Run with environment variables
docker run -p 8501:8501 \
  -e XAI_API_KEY="your-key" \
  -e GOOGLE_API_KEY="your-key" \
  -e API_NINJAS_KEY="your-key" \
  earnings-call-analyzer

# Or use docker-compose
docker-compose up -d
```

### Access

Open browser to `http://localhost:8501`

---

## AWS Deployment

Deploy to AWS using EC2 or ECS.

### Option 1: EC2 Deployment

1. **Launch EC2 Instance:**
   - Choose Ubuntu 22.04 LTS
   - Instance type: t3.medium or larger
   - Configure security group to allow port 8501

2. **Connect to instance:**
```bash
ssh -i your-key.pem ubuntu@your-ec2-ip
```

3. **Install dependencies:**
```bash
sudo apt update
sudo apt install -y python3.11 python3-pip git
```

4. **Clone and setup:**
```bash
git clone https://github.com/kaljuvee/earnings-calls.git
cd earnings-calls
pip install -r requirements.txt
```

5. **Configure environment:**
```bash
nano .env
# Add your API keys
```

6. **Run with systemd:**

Create `/etc/systemd/system/streamlit.service`:

```ini
[Unit]
Description=Streamlit Earnings Call Analyzer
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/earnings-calls
Environment="PATH=/home/ubuntu/.local/bin:/usr/bin"
ExecStart=/home/ubuntu/.local/bin/streamlit run Home.py --server.port=8501 --server.address=0.0.0.0
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable streamlit
sudo systemctl start streamlit
```

7. **Setup Nginx reverse proxy (optional):**

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Option 2: ECS Deployment

1. **Push Docker image to ECR:**
```bash
aws ecr create-repository --repository-name earnings-call-analyzer
docker tag earnings-call-analyzer:latest YOUR_ECR_URI:latest
docker push YOUR_ECR_URI:latest
```

2. **Create ECS Task Definition:**
```json
{
  "family": "earnings-call-analyzer",
  "containerDefinitions": [
    {
      "name": "streamlit",
      "image": "YOUR_ECR_URI:latest",
      "memory": 2048,
      "cpu": 1024,
      "essential": true,
      "portMappings": [
        {
          "containerPort": 8501,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {"name": "XAI_API_KEY", "value": "your-key"},
        {"name": "GOOGLE_API_KEY", "value": "your-key"},
        {"name": "API_NINJAS_KEY", "value": "your-key"}
      ]
    }
  ]
}
```

3. **Create ECS Service with ALB**

---

## Environment Variables

### Required Variables

| Variable | Description | Where to Get |
|----------|-------------|--------------|
| `XAI_API_KEY` | XAI API key for LLM access | [XAI Platform](https://x.ai) |
| `GOOGLE_API_KEY` | Google Gemini API key | [Google AI Studio](https://makersuite.google.com/app/apikey) |
| `API_NINJAS_KEY` | API Ninjas API key | [API Ninjas Dashboard](https://api-ninjas.com/register) |

### Optional Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `STREAMLIT_SERVER_PORT` | Port for Streamlit | 8501 |
| `STREAMLIT_SERVER_ADDRESS` | Server address | localhost |
| `STREAMLIT_THEME_BASE` | Theme (light/dark) | light |

### Setting Environment Variables

**Linux/Mac:**
```bash
export XAI_API_KEY="your-key"
export GOOGLE_API_KEY="your-key"
export API_NINJAS_KEY="your-key"
```

**Windows:**
```cmd
set XAI_API_KEY=your-key
set GOOGLE_API_KEY=your-key
set API_NINJAS_KEY=your-key
```

**Docker:**
```bash
docker run -e XAI_API_KEY="your-key" ...
```

**Streamlit Cloud:**
Use the Secrets management UI (TOML format)

---

## Production Considerations

### Security

1. **API Keys:**
   - Never commit API keys to git
   - Use environment variables or secrets management
   - Rotate keys regularly
   - Use different keys for dev/staging/prod

2. **HTTPS:**
   - Always use HTTPS in production
   - Use Let's Encrypt for free SSL certificates
   - Configure proper SSL/TLS settings

3. **Authentication:**
   - Consider adding user authentication
   - Use Streamlit's built-in authentication or OAuth
   - Implement rate limiting

4. **Network Security:**
   - Configure firewall rules
   - Use VPC for AWS deployments
   - Restrict access to necessary ports only

### Performance

1. **Caching:**
   - Use Streamlit's `@st.cache_data` and `@st.cache_resource`
   - Cache API responses
   - Implement Redis for distributed caching

2. **Resource Limits:**
   - Set appropriate memory limits
   - Monitor CPU usage
   - Implement request timeouts

3. **Scaling:**
   - Use load balancer for multiple instances
   - Consider serverless options (AWS Lambda + API Gateway)
   - Implement horizontal scaling

### Monitoring

1. **Application Monitoring:**
   - Use Streamlit's built-in metrics
   - Implement custom logging
   - Track API usage and costs

2. **Infrastructure Monitoring:**
   - AWS CloudWatch for AWS deployments
   - Datadog, New Relic, or similar tools
   - Set up alerts for errors and performance issues

3. **Error Tracking:**
   - Implement Sentry or similar error tracking
   - Log all API errors
   - Monitor rate limits

### Backup and Recovery

1. **Data Backup:**
   - Regularly backup transcripts and analysis results
   - Use S3 or similar object storage
   - Implement automated backup schedules

2. **Database Backup:**
   - If using a database, implement regular backups
   - Test restore procedures
   - Keep backups in multiple regions

3. **Disaster Recovery:**
   - Document recovery procedures
   - Test disaster recovery plan
   - Maintain infrastructure as code

### Cost Optimization

1. **API Costs:**
   - Monitor API usage
   - Implement caching to reduce calls
   - Use cheaper models when appropriate
   - Set budget alerts

2. **Infrastructure Costs:**
   - Use spot instances for non-critical workloads
   - Implement auto-scaling
   - Review and optimize resource allocation
   - Use reserved instances for predictable workloads

3. **Storage Costs:**
   - Implement lifecycle policies
   - Archive old results
   - Compress large files
   - Use appropriate storage tiers

### Compliance

1. **Data Privacy:**
   - Comply with GDPR, CCPA if applicable
   - Implement data retention policies
   - Document data handling procedures

2. **Financial Regulations:**
   - Add appropriate disclaimers
   - Comply with financial advisory regulations
   - Document that this is for educational purposes

3. **Terms of Service:**
   - Review API provider terms of service
   - Ensure compliance with data usage policies
   - Implement rate limiting as required

---

## Troubleshooting Deployment

### Common Issues

**Issue: Port already in use**
```bash
# Find process using port 8501
lsof -i :8501
# Kill the process
kill -9 PID
```

**Issue: Module not found**
```bash
# Reinstall dependencies
pip install --force-reinstall -r requirements.txt
```

**Issue: Permission denied**
```bash
# Fix permissions
chmod +x Home.py
chown -R ubuntu:ubuntu /home/ubuntu/earnings-calls
```

**Issue: Out of memory**
- Increase instance size
- Optimize caching
- Reduce concurrent requests

**Issue: API rate limits**
- Implement exponential backoff
- Add request queuing
- Cache responses

---

## Maintenance

### Regular Tasks

1. **Weekly:**
   - Review error logs
   - Check API usage and costs
   - Monitor performance metrics

2. **Monthly:**
   - Update dependencies
   - Review security patches
   - Backup data
   - Review and optimize costs

3. **Quarterly:**
   - Security audit
   - Performance review
   - Update documentation
   - Review disaster recovery plan

### Updates

```bash
# Pull latest changes
git pull origin main

# Update dependencies
pip install --upgrade -r requirements.txt

# Restart application
sudo systemctl restart streamlit  # For systemd
docker-compose restart  # For Docker
```

---

## Support

For deployment issues:
- Check GitHub Issues: [https://github.com/kaljuvee/earnings-calls/issues](https://github.com/kaljuvee/earnings-calls/issues)
- Review Streamlit documentation: [https://docs.streamlit.io](https://docs.streamlit.io)
- Contact: dev@lohusalu.com

---

*Lohusalu Capital Management*
