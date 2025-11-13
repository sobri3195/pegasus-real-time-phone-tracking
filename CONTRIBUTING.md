# Contributing to Phone Tracking System

Thank you for your interest in contributing! Please read these guidelines before submitting contributions.

## ⚠️ Legal Requirements

Before contributing, you must understand and agree that:

1. This system is ONLY for authorized device tracking
2. Contributions must not facilitate illegal surveillance
3. All features must respect privacy and consent
4. You are responsible for ensuring your contributions comply with applicable laws

## Code of Conduct

### Our Standards

- **Ethical Use**: Only contribute features for legitimate tracking purposes
- **Privacy First**: Always prioritize user privacy and consent
- **Security Focused**: Security vulnerabilities must be reported privately
- **Respectful Communication**: Be professional and respectful in all interactions

## How to Contribute

### Reporting Bugs

**Security Vulnerabilities**: DO NOT open public issues. Email security@your-domain.com

**Regular Bugs**:
1. Check if the bug has already been reported
2. Use the bug report template
3. Include:
   - Description of the issue
   - Steps to reproduce
   - Expected vs actual behavior
   - System information (OS, Python version, etc.)
   - Relevant logs or error messages

### Suggesting Enhancements

1. Check existing feature requests
2. Open an issue with the enhancement template
3. Clearly describe:
   - The problem you're solving
   - Your proposed solution
   - Alternatives considered
   - Potential impact on privacy/security

### Pull Requests

#### Before You Start

1. **Fork** the repository
2. **Create a branch** from `main`:
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **Set up development environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

#### Development Guidelines

##### Code Style

**Python**:
- Follow PEP 8
- Use meaningful variable names
- Add docstrings to functions
- Keep functions focused and small
- Maximum line length: 100 characters

```python
def process_location(self, location_data: Dict) -> Dict:
    """
    Process location data from GPS or BTS sources.
    
    Args:
        location_data: Dictionary containing location information
    
    Returns:
        Processed location data with accuracy metrics
    
    Raises:
        ValueError: If required location data is missing
    """
    # Implementation
```

**Kotlin**:
- Follow Kotlin coding conventions
- Use descriptive function names
- Add KDoc comments for public APIs
- Prefer immutability where possible

##### Testing

**All contributions must include tests**:

```python
# tests/test_your_feature.py
import pytest
from your_module import YourClass

class TestYourFeature:
    def setup_method(self):
        self.instance = YourClass()
    
    def test_basic_functionality(self):
        result = self.instance.do_something()
        assert result is not None
```

Run tests before submitting:
```bash
pytest tests/ -v
```

##### Documentation

Update documentation for:
- New API endpoints → API_DOCUMENTATION.md
- New features → README.md and PROJECT_SUMMARY.md
- Security changes → SECURITY.md
- Deployment changes → DEPLOYMENT.md

#### Commit Guidelines

**Commit Message Format**:
```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types**:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Examples**:
```
feat(location): Add Wi-Fi positioning support

Implements Wi-Fi triangulation as fallback when GPS and BTS unavailable.
Uses WifiManager to collect nearby AP information.

Closes #123
```

```
fix(security): Prevent token reuse after revocation

Added token revocation check in authentication decorator.
Updated tests to verify revoked tokens are rejected.

Fixes #456
```

#### Submitting Pull Request

1. **Update your fork**:
   ```bash
   git fetch upstream
   git rebase upstream/main
   ```

2. **Run all checks**:
   ```bash
   # Run tests
   pytest tests/ -v
   
   # Check code style
   flake8 .
   
   # Verify all files compile
   python3 -m py_compile *.py
   ```

3. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

4. **Create Pull Request**:
   - Use the PR template
   - Link related issues
   - Describe changes clearly
   - Include screenshots for UI changes
   - List any breaking changes

5. **Code Review**:
   - Respond to feedback promptly
   - Make requested changes
   - Keep discussion focused and professional

## Development Setup

### Prerequisites

- Python 3.9+
- PostgreSQL (for production testing)
- Android Studio (for mobile development)
- Git

### Initial Setup

```bash
# Clone your fork
git clone https://github.com/your-username/phone-tracking-system.git
cd phone-tracking-system

# Add upstream remote
git remote add upstream https://github.com/original/phone-tracking-system.git

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install development dependencies
pip install pytest flake8 black

# Generate keys
python scripts/generate_keys.py

# Copy and configure environment
cp .env.example .env
# Edit .env with your settings

# Initialize database
python init_db.py

# Run tests
pytest tests/
```

### Running the Development Server

```bash
# Activate virtual environment
source venv/bin/activate

# Run server with debug mode
export FLASK_DEBUG=True
python app.py
```

## Project Structure

```
├── app.py                 # Main Flask application
├── config.py              # Configuration
├── models.py              # Database models
├── security.py            # Authentication & encryption
├── location_engine.py     # Location processing
├── tests/                 # Unit tests
├── scripts/               # Helper scripts
├── mobile_agent/          # Android app
└── docs/                  # Documentation
```

## Testing Guidelines

### Unit Tests

Test individual components in isolation:

```python
def test_token_generation(self):
    token = security_manager.generate_token("device_123")
    assert token is not None
    assert isinstance(token, str)
```

### Integration Tests

Test API endpoints end-to-end:

```python
def test_location_update_flow(client):
    # Register device
    response = client.post('/api/devices/register', json={
        'owner_name': 'Test User',
        'consent_verified': True
    })
    device_id = response.json['device']['device_id']
    
    # Update location
    response = client.post('/api/location/update', json={
        'device_id': device_id,
        'latitude': 37.7749,
        'longitude': -122.4194,
        'source': 'GPS'
    })
    assert response.status_code == 201
```

### Test Coverage

Maintain >80% test coverage:

```bash
pytest --cov=. --cov-report=html tests/
```

## Security Considerations

### Before Submitting Security-Related Changes

1. Review SECURITY.md thoroughly
2. Consider all threat vectors
3. Add appropriate tests
4. Document security implications
5. Never commit secrets or keys

### Security Checklist

- [ ] Input validation added
- [ ] SQL injection prevented
- [ ] XSS protection in place
- [ ] Authentication required for sensitive endpoints
- [ ] Rate limiting considered
- [ ] Audit logging included
- [ ] Encryption used for sensitive data
- [ ] No hardcoded secrets

## Documentation Standards

### Code Comments

```python
# Good: Explains WHY
# Use trilateration when 3+ towers available for better accuracy
result = self._trilateration(cell_towers)

# Bad: Explains WHAT (code already shows this)
# Call trilateration function
result = self._trilateration(cell_towers)
```

### API Documentation

For new endpoints, add to API_DOCUMENTATION.md:

```markdown
### New Endpoint
Brief description of what it does.

**Endpoint:** `POST /api/new/endpoint`

**Authentication:** Required

**Request Body:**
\`\`\`json
{
  "param": "value"
}
\`\`\`

**Response:** `200 OK`
\`\`\`json
{
  "result": "success"
}
\`\`\`
```

## Mobile Development

### Android Contributions

1. Follow Android development best practices
2. Test on multiple Android versions (API 24+)
3. Handle permissions properly
4. Respect battery optimization
5. Implement proper error handling

### Building Android App

```bash
cd mobile_agent
./gradlew assembleDebug
./gradlew test
```

## Release Process

### Version Numbering

Follow Semantic Versioning (MAJOR.MINOR.PATCH):

- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes

### Creating a Release

1. Update version numbers
2. Update CHANGELOG.md
3. Run all tests
4. Create release branch
5. Tag the release
6. Update documentation

## Getting Help

- **Questions**: Open a discussion
- **Bugs**: Open an issue
- **Security**: Email security@your-domain.com
- **Chat**: Join our community (if available)

## Recognition

Contributors will be:
- Listed in CONTRIBUTORS.md
- Credited in release notes
- Recognized in the README

## License

By contributing, you agree that your contributions will be licensed under the MIT License with the legal disclaimers included in this project.

---

Thank you for helping make authorized device tracking more secure and reliable!
