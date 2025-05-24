# Contributing to Container Farm Control System

Thank you for your interest in contributing! This project serves diverse communities including educators, therapists, researchers, and commercial growers.

## Quick Start for Contributors

1. **Fork the repository** and clone your fork
2. **Read the documentation** in `docs/user_guides/`
3. **Set up your development environment** using `setup/setup.sh`
4. **Test your changes** on actual hardware when possible
5. **Submit a pull request** with clear documentation

## Types of Contributions

###  Bug Fixes
- Test the fix on actual hardware
- Include before/after photos if relevant
- Update documentation if the bug affected setup procedures

###  New Features
- Discuss major features in an issue first
- Ensure compatibility with educational and therapeutic use cases
- Provide complete documentation and examples

###  Hardware Compatibility
- Test new hardware for at least 24 hours
- Provide wiring diagrams and photos
- Include supplier information and pricing
- Update the hardware compatibility database

###  Documentation
- Ensure content is appropriate for all user types
- Include safety warnings where applicable
- Provide examples for different skill levels
- Consider accessibility in educational contexts

###  Educational Content
- Align with common educational standards
- Include age-appropriate safety considerations
- Provide assessment and evaluation tools
- Consider diverse learning needs

###  Therapeutic Applications
- Respect privacy and dignity requirements
- Include accessibility considerations
- Provide clear safety guidelines
- Consider motor skill and cognitive accommodations

## Development Setup

### Prerequisites
- Raspberry Pi 4B (recommended) or compatible device
- Basic electronics knowledge for hardware testing
- Familiarity with Python and web development

### Installation
```bash
git clone https://github.com/HydroFarmerJason/OpenSourceControlledEnvironments.git
cd OpenSourceControlledEnvironments
sudo ./setup/setup.sh
```

### Testing
```bash
# Run all tests
python -m pytest tests/

# Test specific hardware
python tests/hardware/test_sensors.py

# Run integration tests
python tests/integration/test_system_integration.py
```

## Code Standards

### Python Code
- Follow PEP 8 style guidelines
- Include type hints where possible
- Add docstrings for all functions and classes
- Include error handling and logging

### Hardware Code
- Always include safety checks
- Provide clear error messages
- Include timeout handling for sensor communication
- Document all GPIO pin assignments

### Documentation
- Use clear, accessible language
- Include practical examples
- Provide troubleshooting sections
- Consider non-native English speakers

## Safety Requirements

### Electrical Safety
- All high-voltage work must be clearly marked as requiring professional installation
- Include proper warnings about electrical hazards
- Verify all wiring diagrams before publishing
- Emphasize the importance of proper grounding

### Chemical Safety
- Document safe handling of pH solutions and nutrients
- Include material safety data sheet (MSDS) references
- Emphasize proper storage and disposal
- Include first aid information

### Educational Safety
- Consider age-appropriate safety measures
- Include supervision requirements
- Provide emergency procedures
- Consider liability and insurance implications

## Review Process

### Automated Checks
All contributions are automatically tested for:
- Code syntax and style
- Basic functionality tests
- Documentation formatting
- Security vulnerabilities

### Manual Review
Maintainers will review:
- Hardware safety considerations
- Educational appropriateness
- Therapeutic suitability
- Technical accuracy

### Hardware Testing
For hardware-related contributions:
- Provide photos of working setup
- Document testing duration and conditions
- Include any failure modes or limitations
- Test with multiple Pi models if possible

## Community Guidelines

### Communication
- Be respectful and constructive
- Help newcomers learn and contribute
- Share knowledge and experiences
- Acknowledge the work of others

### Collaboration
- Coordinate major changes through issues
- Respect different use cases and requirements
- Consider the global nature of the community
- Support educational and therapeutic missions

### Knowledge Sharing
- Document your successes and failures
- Share photos and videos of working systems
- Contribute to troubleshooting discussions
- Help maintain the hardware compatibility database

## Getting Help

### Technical Support
- Check existing issues and documentation first
- Provide detailed system information
- Include photos of hardware setup
- Be patient - this is a volunteer-driven project

### Community Support
- Join discussions in GitHub Discussions
- Participate in community showcase
- Share your builds and experiences
- Help others with their questions

## Recognition

Contributors are recognized through:
- Inclusion in CONTRIBUTORS.md
- GitHub contributor statistics
- Community showcase features
- Annual contributor recognition

## Legal Considerations

### Licensing
- All code contributions are under MIT License
- Documentation contributions are under CC BY-SA 4.0
- Hardware designs are under CERN-OHL-W v2
- By contributing, you agree to these licenses

### Patents
- Contributors must not knowingly include patented technology
- If uncertain about patent issues, discuss in an issue first
- Commercial contributors should verify patent freedom

### Educational/Therapeutic Use
- Consider privacy requirements for student/patient data
- Ensure contributions are appropriate for institutional use
- Include necessary safety disclaimers
- Respect regulatory requirements in different jurisdictions

## Thank You!

Your contributions help make growing food more accessible, educational, and therapeutic for communities worldwide. Every contribution, no matter how small, makes a difference in advancing food security, education, and healing through agriculture.
