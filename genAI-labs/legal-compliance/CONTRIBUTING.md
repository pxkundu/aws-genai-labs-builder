# Contributing to Legal Compliance AI Platform

Thank you for your interest in contributing to the Legal Compliance AI Platform! This document provides guidelines and information for contributors.

## 🚀 Getting Started

### Prerequisites
- Python 3.9+
- Node.js 18+
- Docker and Docker Compose
- Git

### Development Setup
1. Fork the repository
2. Clone your fork: `git clone https://github.com/your-username/legal-compliance-ai.git`
3. Run the setup script: `./scripts/setup.sh`
4. Add your API keys to `.env`
5. Start development: `./scripts/dev-start.sh`

## 📋 Development Workflow

### Branch Naming
- `feature/description` - New features
- `bugfix/description` - Bug fixes
- `docs/description` - Documentation updates
- `refactor/description` - Code refactoring
- `test/description` - Test improvements

### Commit Messages
Follow the conventional commits format:
```
type(scope): description

[optional body]

[optional footer]
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Test additions/changes
- `chore`: Maintenance tasks

### Pull Request Process
1. Create a feature branch from `main`
2. Make your changes
3. Add tests for new functionality
4. Ensure all tests pass
5. Update documentation if needed
6. Submit a pull request

## 🧪 Testing

### Backend Tests
```bash
cd backend
python -m pytest tests/ -v
```

### Frontend Tests
```bash
cd frontend
npm test
```

### Integration Tests
```bash
npm run test:e2e
```

### Test Coverage
- Aim for 90%+ coverage on critical components
- Write tests for new features
- Update tests when fixing bugs

## 📝 Code Style

### Python (Backend)
- Follow PEP 8
- Use Black for formatting: `black backend/`
- Use isort for imports: `isort backend/`
- Use flake8 for linting: `flake8 backend/`

### TypeScript/JavaScript (Frontend)
- Follow ESLint configuration
- Use Prettier for formatting: `npm run format`
- Use TypeScript for type safety

### General Guidelines
- Write clear, self-documenting code
- Add comments for complex logic
- Use meaningful variable and function names
- Keep functions small and focused

## 🔧 Adding New Features

### Backend API Endpoints
1. Add route in `backend/api/routes/`
2. Add service logic in `backend/services/`
3. Add data models in `backend/models/`
4. Add tests in `backend/tests/`
5. Update API documentation

### Frontend Components
1. Create component in `frontend/src/components/`
2. Add TypeScript types in `frontend/src/types/`
3. Add tests in `frontend/src/components/__tests__/`
4. Update storybook stories if applicable

### New LLM Integration
1. Add client configuration in `backend/services/llm_service.py`
2. Implement response parsing
3. Add error handling
4. Add tests
5. Update documentation

## 🐛 Reporting Bugs

### Bug Report Template
```markdown
**Describe the bug**
A clear description of what the bug is.

**To Reproduce**
Steps to reproduce the behavior:
1. Go to '...'
2. Click on '....'
3. Scroll down to '....'
4. See error

**Expected behavior**
What you expected to happen.

**Screenshots**
If applicable, add screenshots.

**Environment:**
- OS: [e.g. macOS, Linux]
- Browser: [e.g. Chrome, Firefox]
- Version: [e.g. 1.0.0]

**Additional context**
Any other context about the problem.
```

## 💡 Feature Requests

### Feature Request Template
```markdown
**Is your feature request related to a problem?**
A clear description of what the problem is.

**Describe the solution you'd like**
A clear description of what you want to happen.

**Describe alternatives you've considered**
Alternative solutions or features you've considered.

**Additional context**
Any other context or screenshots about the feature request.
```

## 📚 Documentation

### Code Documentation
- Add docstrings to Python functions and classes
- Add JSDoc comments to TypeScript functions
- Update README files when adding new features
- Keep API documentation up to date

### User Documentation
- Update user guides for new features
- Add screenshots for UI changes
- Keep deployment guides current

## 🔒 Security

### Security Considerations
- Never commit API keys or secrets
- Use environment variables for configuration
- Validate all user inputs
- Follow security best practices
- Report security issues privately

### Reporting Security Issues
Email security issues to: security@legalcomplianceai.com

## 🌍 Internationalization

### Adding New Jurisdictions
1. Add jurisdiction to `Jurisdiction` enum
2. Update legal context in `LLMService`
3. Add jurisdiction description
4. Update frontend jurisdiction list
5. Add tests

### Adding New Practice Areas
1. Add practice area to `PracticeArea` enum
2. Update follow-up question templates
3. Add practice area description
4. Update frontend practice area list
5. Add tests

## 📊 Performance

### Performance Guidelines
- Optimize database queries
- Use caching appropriately
- Minimize API calls to LLMs
- Implement proper error handling
- Monitor resource usage

### Performance Testing
- Add load tests for high-traffic endpoints
- Monitor response times
- Test with various question complexities
- Validate caching behavior

## 🚀 Deployment

### Pre-deployment Checklist
- [ ] All tests pass
- [ ] Code review completed
- [ ] Documentation updated
- [ ] Security review completed
- [ ] Performance testing done
- [ ] Environment variables configured

### Deployment Process
1. Create release branch
2. Update version numbers
3. Run full test suite
4. Deploy to staging
5. Run integration tests
6. Deploy to production
7. Monitor deployment

## 🤝 Community Guidelines

### Code of Conduct
- Be respectful and inclusive
- Provide constructive feedback
- Help others learn and grow
- Follow the golden rule

### Communication
- Use GitHub discussions for questions
- Be clear and concise
- Provide context for issues
- Respond to feedback promptly

## 📞 Getting Help

### Resources
- GitHub Discussions for questions
- Documentation in `/docs`
- Issue tracker for bugs
- Pull requests for contributions

### Contact
- Maintainers: @legal-compliance-ai/maintainers
- Discord: [Join our community](https://discord.gg/legal-compliance-ai)
- Email: contributors@legalcomplianceai.com

## 🎉 Recognition

### Contributors
We recognize all contributors in our README and release notes.

### Types of Contributions
- Code contributions
- Documentation improvements
- Bug reports and fixes
- Feature suggestions
- Testing and quality assurance
- Community support

Thank you for contributing to the Legal Compliance AI Platform! 🚀
