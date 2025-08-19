# Key Components and Their Interactions

## 1. Core Intelligence Techniques

### Technique 1: Payload Optimization
**Component**: `PayloadOptimizer` class in `src/mcp/fastapi_app/main.py`
**Implementation Status**: ✅ Fully Implemented
**Interactions**:
- Receives input from API endpoints (`/optimize_payload`)
- Processes subreddit lists and keyword arrays
- Generates optimized JSON payloads for Apify Actors
- Saves results to `data/processed/payloads/`
- Feeds into data collection systems
- Integrated with Goose session templates for automated payload generation

**Dependencies**:
- FastAPI for API interface
- JSON serialization for payload storage
- File system for result persistence
- Pydantic models for request validation

**Enhanced Features**:
- Boolean clause compression to stay within URL length limits
- Redundancy elimination for search terms
- Coverage expansion for missing areas
- Per-subreddit start URL generation
- Optimization history tracking

### Technique 2: TF-IDF Phrase Mining
**Component**: `PhraseMiner` class in `src/mcp/fastapi_app/main.py`
**Implementation Status**: ✅ Fully Implemented
**Interactions**:
- Loads processed data from `data/processed/`
- Performs TF-IDF analysis on text corpora
- Classifies terms into domain categories
- Identifies emerging terms by comparing with previous lexicons
- Saves results to `data/lexicon/`
- Integrated with BMAD stories for structured phrase mining workflows

**Dependencies**:
- Scikit-learn for TF-IDF implementation
- Pandas for data processing
- File system for corpus loading and result storage
- JSON for lexicon persistence

**Enhanced Features**:
- Domain-specific classification (financial, legal, operational, market, development)
- N-gram range support (1-3 grams)
- Term importance scoring with category weighting
- Emerging term detection with temporal comparison
- Lexicon versioning with timestamped files

### Technique 3: Client-Side Filtering
**Component**: `ClientSideFilterEngine` class in `src/mcp/fastapi_app/main.py`
**Implementation Status**: ✅ Fully Implemented
**Interactions**:
- Loads raw data from `data/raw/`
- Applies 6-stage filtering pipeline
- Calculates relevance scores for posts
- Saves filtered results to `data/processed/`
- Provides top posts for immediate analysis
- Integrated with MCP Use automation for scheduled filtering

**Dependencies**:
- Pandas for data manipulation
- Scikit-learn for semantic similarity
- File system for data loading and storage
- Regular expressions for text processing
- Pydantic models for request validation

**Enhanced Features**:
- Temporal filtering with date range support
- Keyword inclusion/exclusion with boolean logic
- Quality filtering with configurable thresholds
- Semantic similarity filtering using TF-IDF vectors
- Geographic filtering with city/metro targeting
- Deduplication with multiple strategies (exact, fuzzy, content hash)
- Composite relevance scoring with weighted components

### Technique 4: Local-Sub Targeting
**Component**: `LocalSubTargeting` class in `src/mcp/fastapi_app/main.py`
**Implementation Status**: ✅ Fully Implemented
**Interactions**:
- Loads metro configurations from `config/cities.yml`
- Discovers related subreddits for metro areas
- Analyzes posting patterns for different regions
- Updates configuration files with new findings
- Provides targeted subreddit lists for data collection
- Integrated with Goose session templates for geographic expansion

**Dependencies**:
- YAML for configuration management
- Pandas for pattern analysis
- File system for configuration storage
- Pydantic models for request validation

**Enhanced Features**:
- Metro area configuration management
- Subreddit discovery with activity validation
- Regional keyword extraction and analysis
- Posting pattern analysis with temporal trends
- Metro-specific targeting strategies
- Estimated post volume calculation

### Technique 5: Vertical Specialization
**Component**: `VerticalSpecializer` class in `src/mcp/fastapi_app/main.py`
**Implementation Status**: ✅ Fully Implemented
**Interactions**:
- Maintains vertical-specific lexicons
- Analyzes posts for vertical relevance
- Generates vertical-specific search strategies
- Identifies market opportunities by vertical
- Saves configurations to `config/`
- Integrated with BMAD stories for structured vertical analysis

**Dependencies**:
- Regular expressions for text matching
- Pandas for data analysis
- File system for configuration storage
- Pydantic models for request validation
- Enum for vertical categories

**Enhanced Features**:
- Vertical-specific lexicon management (office, retail, industrial, multifamily, hospitality, mixed-use)
- Lexicon conflict resolution with context disambiguation
- Vertical opportunity identification with scoring
- Specialized analysis frameworks per vertical
- Cross-vertical correlation analysis

### Technique 6: Dual-Sort Strategy
**Component**: `DualSortStrategy` class in `src/mcp/fastapi_app/main.py`
**Implementation Status**: ✅ Fully Implemented
**Interactions**:
- Collects posts using different sort strategies
- Performs deduplication across collections
- Analyzes temporal coverage gaps
- Executes backfill for historical data
- Saves comprehensive results to `data/processed/`
- Integrated with MCP Use automation for scheduled backfill

**Dependencies**:
- Pandas for data manipulation
- File system for data storage
- Date/time libraries for temporal analysis
- Pydantic models for request validation
- Enum for sort strategies

**Enhanced Features**:
- Multi-sort strategy support (new, relevance, top, hot)
- Cross-sort deduplication with multiple strategies
- Coverage gap analysis with temporal visualization
- Historical backfill with chunked processing
- Coverage score calculation and reporting

## 2. API Layer Components

### FastAPI Server
**Component**: `app` instance in `src/mcp/fastapi_app/main.py`
**Implementation Status**: ✅ Fully Implemented
**Interactions**:
- Exposes REST endpoints for all six techniques
- Handles request validation through Pydantic models
- Routes requests to appropriate technique implementations
- Provides interactive documentation via Swagger UI
- Returns JSON responses with results and metadata
- Supports full pipeline execution via `/execute_full_pipeline`

**Dependencies**:
- FastAPI framework
- Pydantic for data validation
- Uvicorn for ASGI server
- Technique implementation classes
- JSON for response serialization

**Enhanced Features**:
- Comprehensive API documentation with examples
- Background task support for long-running operations
- Request/response logging for monitoring
- Error handling with detailed error messages
- API versioning support

### Native MCP Server
**Component**: `CREIntelligenceMCPServer` class in `src/mcp/native_server/server.py`
**Implementation Status**: ✅ Fully Implemented
**Interactions**:
- Provides WebSocket interface for MCP protocol
- Registers all technique implementations as MCP tools
- Handles tool listing and execution requests
- Converts between MCP protocol and internal APIs
- Supports both tool listing and tool calling
- Integrated with Goose for interactive workflows

**Dependencies**:
- WebSockets library
- JSON for message serialization
- Technique implementation classes
- MCP protocol specifications
- AsyncIO for concurrent operations

**Enhanced Features**:
- Full MCP protocol compliance
- Tool parameter validation with schema definitions
- Error handling with MCP-compliant error responses
- Connection management with graceful shutdown
- Performance monitoring and logging

## 3. Data Management Components

### Data Manager
**Component**: `DataManager` class in `src/scripts/utility_scripts.py`
**Implementation Status**: ✅ Fully Implemented
**Interactions**:
- Manages data lifecycle across directories
- Archives old processed data
- Cleans cache files
- Merges filtered data files
- Exports data for external analysis
- Accessible via CLI commands (`cre-data`)

**Dependencies**:
- File system operations
- Pandas for data merging
- Pathlib for path operations
- Click for CLI interface
- JSON for metadata storage

**Enhanced Features**:
- Storage statistics reporting
- Configurable archive policies
- Cache cleanup with age-based retention
- Data export in multiple formats (Parquet, CSV, Excel)
- Duplicate removal with ID-based deduplication

### Backup Manager
**Component**: `BackupManager` class in `src/scripts/utility_scripts.py`
**Implementation Status**: ✅ Fully Implemented
**Interactions**:
- Creates backups of data and configurations
- Backs up PostgreSQL database
- Restores data from backups
- Manages backup retention
- Lists available backups
- Accessible via CLI commands (`cre-backup`)

**Dependencies**:
- Tarfile for archive creation
- Subprocess for database tools
- File system operations
- Click for CLI interface
- Regular expressions for connection string parsing

**Enhanced Features**:
- Incremental and full backup support
- Database backup with pg_dump integration
- Backup restoration with psql integration
- Backup listing with size information
- Automatic cleanup of old backups

### Performance Monitor
**Component**: `PerformanceMonitor` class in `src/scripts/utility_scripts.py`
**Implementation Status**: ✅ Fully Implemented
**Interactions**:
- Monitors system performance metrics
- Tracks process resource usage
- Tests API endpoint performance
- Generates performance reports
- Provides continuous monitoring
- Accessible via CLI commands (`cre-monitor`)

**Dependencies**:
- Psutil for system metrics
- HTTPX for API testing
- JSON for metrics storage
- AsyncIO for concurrent operations
- Pathlib for file operations

**Enhanced Features**:
- Real-time system monitoring (CPU, memory, disk, network)
- Process-specific monitoring with filtering
- API endpoint performance testing
- Continuous monitoring with configurable duration
- Performance summary generation with statistics

## 4. Development Infrastructure Components

### Testing Framework
**Component**: Pytest-based tests in `src/tests/`
**Implementation Status**: ✅ Fully Implemented
**Interactions**:
- Tests individual technique implementations
- Validates API endpoints
- Tests MCP server functionality
- Runs integration tests
- Provides code coverage metrics

**Dependencies**:
- Pytest for test framework
- FastAPI TestClient for API testing
- WebSockets for MCP testing
- Mock for dependency isolation
- Pytest-asyncio for async testing

**Enhanced Features**:
- Unit tests for each technique implementation
- Integration tests for API endpoints
- End-to-end tests for MCP server
- Code coverage reporting with pytest-cov
- Test fixtures for data setup and teardown

### CI/CD Pipeline
**Component**: GitHub Actions workflow in `.github/workflows/ci.yml`
**Implementation Status**: ✅ Fully Implemented
**Interactions**:
- Runs code quality checks on push/pull request
- Executes test suite across Python versions
- Performs security scanning
- Builds and pushes Docker images
- Deploys to staging and production

**Dependencies**:
- GitHub Actions runners
- Docker for container building
- Security scanning tools (Trivy, Bandit)
- Testing frameworks
- Code quality tools (Black, Flake8, MyPy)

**Enhanced Features**:
- Multi-Python version testing (3.9, 3.10, 3.11)
- Code quality enforcement with pre-commit hooks
- Security scanning with multiple tools
- Docker image building and publishing
- Automated deployment to staging environment

### Development Tools
**Component**: Makefile and utility scripts
**Implementation Status**: ✅ Fully Implemented
**Interactions**:
- Provides common development tasks
- Manages dependencies and installations
- Runs tests and quality checks
- Formats code
- Manages data and database operations

**Dependencies**:
- Make for task automation
- Python tools (pip, black, isort, etc.)
- Docker for containerization
- Database tools (alembic, pg_dump)
- CLI tools for system operations

**Enhanced Features**:
- One-command setup with `make install`
- Code formatting with `make format`
- Quality checks with `make lint`
- Testing with `make test` and `make test-cov`
- Database operations with `make db-*` commands

## 5. Orchestration Components

### Goose AI Integration
**Component**: Session templates and MCP extensions in `src/goose_config_templates.txt`
**Implementation Status**: ✅ Fully Implemented
**Interactions**:
- Provides interactive workflow orchestration
- Manages session context and state
- Coordinates tool execution across MCP servers
- Integrates with BMAD stories for structured workflows
- Supports automated scheduling with MCP Use

**Dependencies**:
- Goose AI framework
- MCP protocol for tool communication
- YAML for session template definition
- Git MCP for knowledge management

**Enhanced Features**:
- Pre-configured session templates for common workflows
- Multi-MCP server coordination
- Context preservation across sessions
- Interactive decision points in workflows
- Automated session execution with scheduling

### BMAD Stories
**Component**: YAML story definitions in `src/scripts/bmad_stories.txt`
**Implementation Status**: ✅ Fully Implemented
**Interactions**:
- Provides structured task execution patterns
- Defines acceptance criteria for workflows
- Integrates with MCP tools for execution
- Supports role-based task assignment
- Enables automated testing and validation

**Dependencies**:
- YAML for story definition
- MCP protocol for tool execution
- Git for version control
- Pydantic for validation

**Enhanced Features**:
- Six technique-specific stories with detailed workflows
- Acceptance criteria with measurable outcomes
- Integration with Goose session templates
- Automated execution with MCP Use
- Sprint planning and progress tracking

### MCP Use Automation
**Component**: Automation scripts in `src/scripts/mcp_use_automation.py`
**Implementation Status**: ✅ Fully Implemented
**Interactions**:
- Enables headless execution of MCP tools
- Provides scheduling capabilities for automated workflows
- Integrates with CLI tools for system operations
- Supports batch processing of multiple operations
- Generates execution reports and metrics

**Dependencies**:
- MCP protocol for tool communication
- Schedule library for job scheduling
- AsyncIO for concurrent operations
- JSON for configuration and reporting

**Enhanced Features**:
- Daily, weekly, and monthly job scheduling
- Automated pipeline execution with `run_full_pipeline`
- Progress tracking and error handling
- Report generation with execution metrics
- Integration with system logging

## 6. Data Flow Interactions

### Data Collection Flow
```
External Sources → Apify Actors → Raw Data Storage → Filtering → Processed Data
                                      ↓
                                Phrase Mining → Lexicon Updates
                                      ↓
                            Payload Optimization → Improved Collection
```

### Analysis Pipeline Flow
```
Processed Data → Local-Sub Targeting → Metro-Specific Analysis
      ↓
Vertical Specialization → Domain-Specific Insights
      ↓
Dual-Sort Strategy → Comprehensive Coverage Analysis
```

### Output Generation Flow
```
Analysis Results → API Endpoints → Client Applications
       ↓
MCP Server → AI Agents and Tools
       ↓
CLI Tools → Automation Scripts
       ↓
Export Functions → External Systems
       ↓
Goose Sessions → Interactive Workflows
       ↓
BMAD Stories → Structured Analysis
```

## 7. Cross-Component Dependencies

### Shared Libraries
- **Pandas**: Used across all technique implementations for data processing
- **Scikit-learn**: Used for TF-IDF, semantic similarity, and potential ML features
- **FastAPI**: Core framework for REST API
- **WebSockets**: Core library for MCP server
- **Pydantic**: Data validation for both API and MCP interfaces
- **AsyncIO**: Asynchronous operations throughout the platform
- **Pathlib**: Standardized path handling across components

### Shared Data Structures
- **File System Layout**: All components use consistent directory structure
- **JSON/JSONL Formats**: Standard data exchange format
- **Configuration Files**: Shared YAML configuration approach
- **Database Schema**: Common database structure for persistence
- **API Models**: Shared Pydantic models for request/response validation

### Shared Utilities
- **Logging**: Consistent logging approach across all components
- **Path Management**: Standardized path handling with pathlib
- **Error Handling**: Common exception patterns
- **Async Operations**: Consistent async/await patterns
- **Configuration Management**: Environment variable and file-based configuration

## 8. Interface Contracts

### API Contracts
- **Request/Response Models**: Pydantic models define data contracts
- **Endpoint URLs**: Standardized REST endpoints
- **HTTP Status Codes**: Consistent error handling
- **JSON Schema**: Predictable response structures
- **API Versioning**: Semantic versioning for API evolution

### MCP Contracts
- **Tool Definitions**: Standardized tool parameter definitions
- **Message Format**: JSON-RPC 2.0 compliant messaging
- **Error Handling**: Consistent error response format
- **Capability Exchange**: Standardized tool listing
- **Session Management**: Context preservation across tool calls

### Data Contracts
- **File Formats**: JSON/JSONL for structured data
- **Directory Structure**: Consistent data organization
- **Naming Conventions**: Standardized file naming
- **Metadata**: Consistent metadata inclusion
- **Versioning**: Timestamp-based versioning for data files

This comprehensive component interaction map shows how the CRE Intelligence Platform is structured as a cohesive system where each component plays a specific role while maintaining loose coupling through well-defined interfaces. The platform leverages modern technologies and follows best practices for scalability, maintainability, and extensibility.