# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 2.x.x   | :white_check_mark: |
| 1.x.x   | :x:                |

## Reporting a Vulnerability

### Security Contact
Report security vulnerabilities to: [security@opensourcefarm.org]

**Please do not report security vulnerabilities through public GitHub issues.**

### What to Include
- Description of the vulnerability
- Steps to reproduce the issue
- Potential impact assessment
- Suggested fix (if you have one)

### Response Timeline
- **24 hours**: Initial response acknowledging receipt
- **72 hours**: Preliminary assessment of severity
- **1 week**: Detailed response with timeline for fix
- **30 days**: Target resolution for high-severity issues

## Security Considerations

### Hardware Security
- Physical access to Raspberry Pi provides root access
- Secure physical installation in educational/therapeutic environments
- Consider lockable enclosures for public installations
- Disable unnecessary services and ports

### Network Security
- Change default passwords immediately after installation
- Use strong passwords for all accounts
- Enable SSH key authentication
- Consider VPN for remote access
- Regularly update all software components

### Data Privacy
- Student/patient data requires special protection
- Implement appropriate access controls
- Consider data retention policies
- Ensure compliance with local privacy regulations (FERPA, HIPAA, GDPR)

### Educational Environment Security
- Restrict student access to system administration
- Monitor for inappropriate use
- Implement appropriate content filtering
- Ensure age-appropriate security measures

### Therapeutic Environment Security
- Protect patient privacy and dignity
- Secure therapy session data
- Implement appropriate access controls for therapeutic staff
- Consider HIPAA compliance requirements

## Best Practices

### Installation Security
- Use official Raspberry Pi OS images
- Verify checksums of downloaded files
- Keep all software updated
- Use reputable suppliers for hardware

### Operational Security
- Regular security updates
- Monitor system logs
- Backup important data
- Test recovery procedures

### Development Security
- Code review for security issues
- Dependency vulnerability scanning
- Secure coding practices
- Regular security audits

## Vulnerability Disclosure

We follow responsible disclosure practices:

1. **Private disclosure** to maintainers first
2. **Coordinated timeline** for public disclosure
3. **User notification** through security advisories
4. **Credit acknowledgment** for reporters (unless anonymity requested)

## Security Updates

Security updates are released as:
- **Patches** for supported versions
- **Security advisories** on GitHub
- **Documentation updates** with mitigation strategies
- **Community notifications** through appropriate channels

Thank you for helping keep Container Farm Control System secure for educational and therapeutic communities worldwide.
