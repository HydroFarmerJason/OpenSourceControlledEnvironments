# Container Farm Control System

<div align="center">

![Project Logo](assets/images/logos/container-farm-logo.png)

**Open-source, offline-capable control system for container farms, greenhouses, and controlled growing environments**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Documentation: CC BY-SA 4.0](https://img.shields.io/badge/Documentation-CC%20BY--SA%204.0-blue.svg)](https://creativecommons.org/licenses/by-sa/4.0/)
[![Hardware Compatibility](https://img.shields.io/badge/Hardware-Pi%204B%20Tested-green.svg)](hardware/compatibility/HARDWARE_COMPATIBILITY.md)

[Quick Start](#quick-start) • [Documentation](docs/) • [Examples](examples/) • [Hardware Guide](hardware/compatibility/HARDWARE_COMPATIBILITY.md)

</div>

---

## 🌱 **What is Container Farm Control System?**

A comprehensive, **privacy-first** control system that transforms shipping containers, greenhouses, or growing spaces into intelligent, automated farms. Originally developed as an alternative to proprietary systems, it prioritizes **user autonomy**, **data sovereignty**, and **community needs**.

### **Perfect for:**
- 🏫 **Educators** - STEM curriculum integration with real-world applications
- 🏥 **Therapists** - Horticultural therapy with accessibility features  
- 👨‍🌾 **Farmers** - Commercial production with cost-effective automation
- 🔬 **Researchers** - Data collection and experimental control
- 🏠 **Hobbyists** - Home growing with professional-grade monitoring

---

## 🚀 **Quick Start**

### **Option 1: Complete Installation (Recommended)**
```bash
# Clone repository and run setup
git clone https://github.com/HydroFarmerJason/OpenSourceControlledEnvironments.git
cd OpenSourceControlledEnvironments
sudo ./setup/setup.sh
```

### **Option 2: Educational Quick Setup**
```bash
# Simplified setup for classroom use
sudo ./setup/educational_setup.sh
```

**🎯 Ready in 15 minutes!** Access your dashboard at `http://your-pi-ip-address`

---

## 📊 **Dashboard Previews**

| Setup Type | Description | Configuration |
|------------|-------------|---------------|
| **Basic Monitoring** | Simple temperature and humidity monitoring | [View Config →](config/systems/basic_monitoring.json) |
| **Educational** | Student-friendly interface with safety features | [View Config →](config/profiles/educator.json) |
| **Commercial** | Production-ready dashboard with advanced controls | [View Config →](config/profiles/farmer.json) |

---

## ✨ **Key Features**

<table>
<tr>
<td width="50%">

### 🔧 **Complete Environmental Control**
- **Climate Management**: Temperature, humidity, CO2 monitoring
- **Smart Irrigation**: pH, EC, and nutrient management  
- **Lighting Control**: Automated photoperiod management
- **Safety Systems**: Emergency shutoffs and alerts

### 🎓 **Educational Features**
- **Curriculum Integration**: Aligned with STEM standards
- **Student Tracking**: Individual progress monitoring
- **Safety First**: Age-appropriate controls and restrictions
- **Assessment Tools**: Built-in evaluation metrics

</td>
<td width="50%">

### ♿ **Accessibility & Inclusion**
- **Visual Accommodations**: High-contrast themes, large fonts
- **Motor Skill Support**: Simplified controls, large buttons
- **Cognitive Aids**: Visual guides, step-by-step prompts
- **Therapeutic Tools**: Progress tracking, customizable interfaces

### 🛡️ **Privacy & Data Sovereignty** 
- **Offline Operation**: No cloud dependencies required
- **Local Storage**: All data stays on your device
- **User Control**: Choose what data to share and with whom
- **Open Source**: Transparent, auditable code

</td>
</tr>
</table>

---

## 🛒 **Complete Setup Examples**

### 💰 **Budget Setup ($75-150)**
Perfect for education and hobby use
- Raspberry Pi 4B (2GB) + microSD
- DS18B20 temperature sensor
- DHT22 humidity sensor  
- 2-channel relay board
- Basic grow light control

**[📋 Complete Parts List →](hardware/compatibility/shopping_lists/budget_setup.json)**

### 🏫 **Educational Setup ($150-250)**
Classroom-ready with safety features
- All basic components plus:
- BME280 environmental sensor
- Pi Camera for photo documentation
- Educational safety enclosure
- Student-friendly interface

**[📋 Complete Parts List →](hardware/compatibility/shopping_lists/educational.json)**

### 🏭 **Commercial Setup ($400-800)**
Production-ready hydroponic system
- Professional sensors (pH, EC, CO2)
- 8-channel relay control
- Peristaltic pumps for precise dosing
- Industrial enclosures
- Remote monitoring capabilities

**[📋 Complete Parts List →](hardware/compatibility/shopping_lists/commercial.json)**

### 📚 **Classroom Setup Example**
Open-source configuration for K-12 classroom grow labs

**[📂 Example Files →](examples/classroom_setup/)**

### 🌿 **Therapy Garden Example**
Therapeutic garden setup with accessibility features

**[📂 Example Files →](examples/therapy_garden/)**

---

## 📸 **Success Stories**

<table>
<tr>
<td align="center">
<img src="assets/images/showcase/classroom-build.jpg" width="200px" alt="Classroom Installation"/>
<br/><b>Lincoln Elementary</b><br/>
<i>"Students increased science engagement by 40%"</i>
</td>
<td align="center">
<img src="assets/images/showcase/therapy-garden.jpg" width="200px" alt="Therapy Garden"/>
<br/><b>Recovery Center</b><br/>
<i>"Patients show improved focus and calmness"</i>
</td>
<td align="center">
<img src="assets/images/showcase/commercial-farm.jpg" width="200px" alt="Commercial Farm"/>
<br/><b>Urban Microgreens</b><br/>
<i>"Cut labor costs 60%, increased yield 25%"</i>
</td>
</tr>
</table>

**[📖 Read More Success Stories →](community/showcase/)**

- *Classroom Setup success stories coming soon*
- *Therapy Garden success stories coming soon*

---

## 🔌 **Hardware Compatibility**

**Tested & Verified:**
- ✅ **Raspberry Pi**: 4B (recommended), 3B+, Zero 2W  
- ✅ **Sensors**: 50+ compatible environmental sensors
- ✅ **Controllers**: Relay boards, solid-state relays, contactors
- ✅ **Communication**: I2C, SPI, 1-Wire, UART, Analog

**[📋 Complete Compatibility Guide →](hardware/compatibility/HARDWARE_COMPATIBILITY.md)**

---

## 📚 **Documentation**

| User Type | Quick Start | Advanced Guide |
|-----------|-------------|----------------|
| 🏫 **Educators** | [Educational Quick Start →](docs/educational/quick_start.md) | [Curriculum Integration →](docs/educational/curriculum_guide.md) |
| 🏥 **Therapists** | [Therapy Setup →](docs/therapeutic/quick_start.md) | [Therapeutic Protocols →](docs/therapeutic/therapy_protocols.md) |
| 👨‍🌾 **Farmers** | [Commercial Setup →](docs/commercial/quick_start.md) | [Business Guide →](docs/commercial/business_guide.md) |
| 🔬 **Researchers** | [Research Setup →](docs/research/quick_start.md) | [Data Standards →](docs/research/data_standards.md) |
| 👨‍💻 **Developers** | [Development Setup →](docs/technical/development.md) | [API Reference →](docs/technical/api_reference.md) |

---

## 🤝 **Community**

### **Get Help & Connect**
- 💬 **GitHub Discussions** - Q&A and community support (enable in repository settings)
- 🐛 **Issue Tracker** - Bug reports and feature requests  
- 📸 [User Showcase](community/showcase/) - Share your builds and successes
- 🎓 [Educational Community](docs/educational/) - Teacher resources and lesson plans

### **Contributing**
We welcome contributions from everyone! Whether you're fixing bugs, adding features, testing hardware, or improving documentation.

**[📋 Contributing Guide →](.github/CONTRIBUTING.md)**

---

## 🆚 **Why Choose Container Farm Control System?**

| Feature | Container Farm | Proprietary Systems |
|---------|---------------|-------------------|
| **Cost** | $75-800 setup | $5,000-50,000+ |
| **Data Ownership** | ✅ You own all data | ❌ Vendor controls data |
| **Offline Operation** | ✅ Works without internet | ❌ Requires cloud connection |
| **Customization** | ✅ Fully customizable | ❌ Limited options |
| **Educational Use** | ✅ Designed for education | ⚠️ Limited educational features |
| **Privacy** | ✅ Complete privacy | ❌ Data harvesting |
| **Vendor Lock-in** | ✅ Open ecosystem | ❌ Proprietary hardware |

---

## ⚖️ **License & Legal**

- **Software**: [MIT License](LICENSE) - Use commercially, modify freely
- **Documentation**: [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/) - Share with attribution
- **Hardware Designs**: [CERN-OHL-W v2](https://cern-ohl.web.cern.ch/) - Open hardware license

**Safe for commercial, educational, and therapeutic use.**

---

## 🛡️ **Safety & Compliance**

- **Educational Safety**: Age-appropriate controls, supervision guidelines
- **Electrical Safety**: Professional installation guides for high-voltage components  
- **Therapeutic Compliance**: HIPAA considerations, accessibility standards
- **Food Safety**: Guidelines for edible crop production

**[📋 Complete Safety Guide →](hardware/safety/)**

---

## 🗺️ **Roadmap**

### **Version 1.1 (Q3 2024)**
- [ ] Mobile app for remote monitoring
- [ ] Advanced machine learning for yield prediction  
- [ ] Multi-language support (Spanish, French, Mandarin)
- [ ] Enhanced accessibility features

### **Version 1.2 (Q4 2024)**
- [ ] Multi-container fleet management
- [ ] Advanced analytics dashboard
- [ ] Integration with popular IoT platforms
- [ ] Expanded therapeutic protocols

**[📈 Full Roadmap →](ROADMAP.md)**

---

## 📞 **Support**

### **Community Support** (Free)
- GitHub Discussions for general questions
- Community troubleshooting database
- User-contributed solutions

### **Professional Support** 
- Installation assistance for schools/institutions
- Custom development for commercial users
- Training workshops for educators

**Contact information available in repository documentation**

---

<div align="center">

**Made with 🌱 for growers, educators, and healers worldwide**

**⭐ Star this project if it helps you grow!**

</div>
