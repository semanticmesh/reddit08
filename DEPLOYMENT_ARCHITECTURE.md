# CRE Intelligence Platform Deployment Architecture

## Overview

This document provides visual diagrams illustrating the architecture of both Docker deployment and local development setup options for the CRE Intelligence Platform.

## Docker Deployment Architecture

```mermaid
graph TD
    A[Client/Browser] --> B[Nginx Reverse Proxy]
    B --> C[FastAPI Application]
    
    subgraph Docker Containers
        C --> D[(PostgreSQL Database)]
        C --> E[(Redis Cache)]
        C --> F[Celery Worker]
        C --> G[Celery Beat]
    end
    
    subgraph External Services
        H[OpenAI API]
        I[Reddit API]
        J[News API]
        K[Twitter API]
    end
    
    C --> H
    C --> I
    C --> J
    C --> K
    F --> D
    F --> E
    G --> E
    
    style A fill:#e1f5fe
    style B fill:#f3e5f5
    style C fill:#e8f5e8
    style D fill:#fff3e0
    style E fill:#fce4ec
    style F fill:#f1f8e9
    style G fill:#fff8e1
    style H fill:#e0f7fa
    style I fill:#e0f7fa
    style J fill:#e0f7fa
    style K fill:#e0f7fa
```

## Local Development Architecture

```mermaid
graph TD
    A[Developer] --> B[FastAPI Application]
    
    subgraph Local Services
        B --> C[(PostgreSQL Database)]
        B --> D[(Redis Cache)]
    end
    
    subgraph External Services
        E[OpenAI API]
        F[Reddit API]
        G[News API]
        H[Twitter API]
    end
    
    B --> E
    B --> F
    B --> G
    B --> H
    
    style A fill:#e1f5fe
    style B fill:#e8f5e8
    style C fill:#fff3e0
    style D fill:#fce4ec
    style E fill:#e0f7fa
    style F fill:#e0f7fa
    style G fill:#e0f7fa
    style H fill:#e0f7fa
```

## Service Dependencies

### Docker Deployment Dependencies

```mermaid
graph LR
    A[FastAPI App] --> B[PostgreSQL]
    A --> C[Redis]
    D[Celery Worker] --> B
    D --> C
    E[Celery Beat] --> C
    F[Nginx] --> A
    
    style A fill:#4CAF50,color:#fff
    style B fill:#FF9800,color:#fff
    style C fill:#F44336,color:#fff
    style D fill:#9C27B0,color:#fff
    style E fill:#673AB7,color:#fff
    style F fill:#2196F3,color:#fff
```

### Local Development Dependencies

```mermaid
graph LR
    A[FastAPI App] --> B[PostgreSQL]
    A --> C[Redis]
    
    style A fill:#4CAF50,color:#fff
    style B fill:#FF9800,color:#fff
    style C fill:#F44336,color:#fff
```

## Data Flow Diagram

### Docker Deployment Data Flow

```mermaid
flowchart LR
    A[Data Sources] --> B[FastAPI App]
    B --> C{Processing}
    C --> D[PostgreSQL]
    C --> E[Redis Cache]
    C --> F[Celery Tasks]
    F --> G[Background Processing]
    G --> D
    G --> H[External APIs]
    
    subgraph Platform Services
        B
        C
        D
        E
        F
        G
    end
    
    subgraph External
        A
        H
    end
    
    style A fill:#e0f7fa
    style B fill:#e8f5e8
    style C fill:#f1f8e9
    style D fill:#fff3e0
    style E fill:#fce4ec
    style F fill:#f3e5f5
    style G fill:#e1f5fe
    style H fill:#e0f7fa
```

## Container/Process Relationships

### Docker Container Relationships

```mermaid
graph TD
    A[reddit08-nginx] --> B[reddit08-cre-platform]
    B --> C[reddit08-postgres]
    B --> D[reddit08-redis]
    E[reddit08-celery] --> C
    E --> D
    F[reddit08-celery-beat] --> D
    
    style A fill:#2196F3,color:#fff
    style B fill:#4CAF50,color:#fff
    style C fill:#FF9800,color:#fff
    style D fill:#F44336,color:#fff
    style E fill:#9C27B0,color:#fff
    style F fill:#673AB7,color:#fff
```

## Network Architecture

### Docker Network Isolation

```mermaid
graph TD
    subgraph Host Network
        A[External Access]
    end
    
    subgraph reddit08-network
        B[reddit08-nginx]
        C[reddit08-cre-platform]
        D[reddit08-postgres]
        E[reddit08-redis]
        F[reddit08-celery]
        G[reddit08-celery-beat]
    end
    
    A --> B
    B --> C
    C --> D
    C --> E
    F --> D
    F --> E
    G --> E
    
    style A fill:#e1f5fe
    style B fill:#2196F3,color:#fff
    style C fill:#4CAF50,color:#fff
    style D fill:#FF9800,color:#fff
    style E fill:#F44336,color:#fff
    style F fill:#9C27B0,color:#fff
    style G fill:#673AB7,color:#fff
```

## Key Differences Summary

| Aspect | Docker Deployment | Local Development |
|--------|------------------|-------------------|
| **Isolation** | Full container isolation | Direct system access |
| **Dependencies** | All in containers | Requires local services |
| **Management** | Docker Compose commands | Manual service management |
| **Scalability** | Easy horizontal scaling | Limited scaling |
| **Consistency** | Guaranteed environment consistency | Depends on local setup |
| **Resource Usage** | Higher (container overhead) | Lower (direct access) |
| **Debugging** | Container-based debugging | Direct system debugging |

## Deployment Recommendations

### For Production Use
- ✅ Use Docker deployment
- ✅ Ensure proper resource allocation
- ✅ Configure monitoring and logging
- ✅ Set up backup procedures
- ✅ Implement security best practices

### For Development Use
- ✅ Use local development setup
- ✅ Enable debug mode
- ✅ Use development-focused configurations
- ✅ Set up hot-reloading
- ✅ Configure detailed logging

## Support Resources

- Full Documentation: [docs/README.md](./docs/README.md)
- Installation Guide: [INSTALLATION_GUIDE.md](./INSTALLATION_GUIDE.md)
- Deployment Summary: [DEPLOYMENT_SUMMARY.md](./DEPLOYMENT_SUMMARY.md)