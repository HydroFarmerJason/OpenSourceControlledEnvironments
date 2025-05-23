@dataclass
class TownService:
    """Service available in town intranet."""
    service_id: str
    name: str
    description: str
    service_type: str  # "communication", "data_storage", "security", etc.
    endpoint_url: str
    requires_authentication: bool = True
    access_level: str = "all"  # "all", "admin", "contributor", etc.
    status: str = "active"  # "active", "maintenance", "deprecated"
    dependencies: List[str] = field(default_factory=list)
    admin_contact: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CommunityIntranet:
    """Community intranet system."""
    intranet_id: str
    community_id: str
    name: str
    description: str
    domain: Optional[str] = None
    network_type: str = "mesh"  # "mesh", "client-server", "hybrid"
    installation_date: float = field(default_factory=time.time)
    services: List[str] = field(default_factory=list)
    administrators: List[str] = field(default_factory=list)
    backup_schedule: str = "daily"
    offline_functionality: bool = True
    server_hardware: Dict[str, Any] = field(default_factory=dict)
    network_topology: Dict[str, Any] = field(default_factory=dict)
    security_measures: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class LocalLLMModel:
    """Local LLM model for community use."""
    model_id: str
    name: str
    description: str
    model_size: str  # "small", "medium", "large"
    parameter_count: int
    requires_gpu: bool
    disk_size_mb: int
    ram_required_mb: int
    supported_languages: List[str]
    specialized_for: List[str] = field(default_factory=list)  # Areas of specialization
    fine_tunable: bool = True
    source_url: Optional[str] = None
    license: str = "open"
    version: str = "1.0"
    metadata: Dict[str, Any] = field(default_factory=dict)


class TownIntranetBuilder:
    """
    Builder for town intranets with offline knowledge bases and local LLMs.
    """
    
    def __init__(self, data_path: str = "intranet_data"):
        """
        Initialize town intranet builder.
        
        Args:
            data_path: Path for storing intranet data
        """
        self.data_path = data_path
        
        # Ensure paths exist
        os.makedirs(data_path, exist_ok=True)
        os.makedirs(os.path.join(data_path, "resources"), exist_ok=True)
        os.makedirs(os.path.join(data_path, "services"), exist_ok=True)
        os.makedirs(os.path.join(data_path, "intranets"), exist_ok=True)
        os.makedirs(os.path.join(data_path, "llm_models"), exist_ok=True)
        
        # Load data
        self.resources: Dict[str, KnowledgeResource] = {}
        self.services: Dict[str, TownService] = {}
        self.intranets: Dict[str, CommunityIntranet] = {}
        self.llm_models: Dict[str, LocalLLMModel] = {}
        
        self._load_data()
        
        # Initialize default resources and services if none exist
        if not self.services:
            self._initialize_default_services()
        if not self.llm_models:
            self._initialize_default_llm_models()
    
    def _load_data(self) -> None:
        """Load intranet data from disk."""
        try:
            # Load resources
            resources_dir = os.path.join(self.data_path, "resources")
            for filename in os.listdir(resources_dir):
                if filename.endswith(".json"):
                    file_path = os.path.join(resources_dir, filename)
                    try:
                        with open(file_path, "r") as f:
                            data = json.load(f)
                            resource = KnowledgeResource(
                                resource_id=data.get("resource_id", filename.replace(".json", "")),
                                title=data.get("title", "Unknown Resource"),
                                description=data.get("description", ""),
                                category=KnowledgeCategory[data.get("category", "TECHNICAL")],
                                resource_type=ResourceType[data.get("resource_type", "DOCUMENT")],
                                file_path=data.get("file_path", ""),
                                creator_id=data.get("creator_id"),
                                created_date=data.get("created_date", time.time()),
                                last_updated_date=data.get("last_updated_date", time.time()),
                                tags=data.get("tags", []),
                                related_resources=data.get("related_resources", []),
                                permissions=data.get("permissions", {}),
                                version=data.get("version", "1.0"),
                                size_bytes=data.get("size_bytes"),
                                metadata=data.get("metadata", {})
                            )
                            self.resources[resource.resource_id] = resource
                    except Exception as e:
                        logger.error(f"Error loading resource from {file_path}: {e}")
                        
            # Load services
            services_dir = os.path.join(self.data_path, "services")
            for filename in os.listdir(services_dir):
                if filename.endswith(".json"):
                    file_path = os.path.join(services_dir, filename)
                    try:
                        with open(file_path, "r") as f:
                            data = json.load(f)
                            service = TownService(
                                service_id=data.get("service_id", filename.replace(".json", "")),
                                name=data.get("name", "Unknown Service"),
                                description=data.get("description", ""),
                                service_type=data.get("service_type", ""),
                                endpoint_url=data.get("endpoint_url", ""),
                                requires_authentication=data.get("requires_authentication", True),
                                access_level=data.get("access_level", "all"),
                                status=data.get("status", "active"),
                                dependencies=data.get("dependencies", []),
                                admin_contact=data.get("admin_contact"),
                                metadata=data.get("metadata", {})
                            )
                            self.services[service.service_id] = service
                    except Exception as e:
                        logger.error(f"Error loading service from {file_path}: {e}")
                        
            # Load intranets
            intranets_dir = os.path.join(self.data_path, "intranets")
            for filename in os.listdir(intranets_dir):
                if filename.endswith(".json"):
                    file_path = os.path.join(intranets_dir, filename)
                    try:
                        with open(file_path, "r") as f:
                            data = json.load(f)
                            intranet = CommunityIntranet(
                                intranet_id=data.get("intranet_id", filename.replace(".json", "")),
                                community_id=data.get("community_id", ""),
                                name=data.get("name", "Unknown Intranet"),
                                description=data.get("description", ""),
                                domain=data.get("domain"),
                                network_type=data.get("network_type", "mesh"),
                                installation_date=data.get("installation_date", time.time()),
                                services=data.get("services", []),
                                administrators=data.get("administrators", []),
                                backup_schedule=data.get("backup_schedule", "daily"),
                                offline_functionality=data.get("offline_functionality", True),
                                server_hardware=data.get("server_hardware", {}),
                                network_topology=data.get("network_topology", {}),
                                security_measures=data.get("security_measures", []),
                                metadata=data.get("metadata", {})
                            )
                            self.intranets[intranet.intranet_id] = intranet
                    except Exception as e:
                        logger.error(f"Error loading intranet from {file_path}: {e}")
                        
            # Load LLM models
            llm_models_dir = os.path.join(self.data_path, "llm_models")
            for filename in os.listdir(llm_models_dir):
                if filename.endswith(".json"):
                    file_path = os.path.join(llm_models_dir, filename)
                    try:
                        with open(file_path, "r") as f:
                            data = json.load(f)
                            llm_model = LocalLLMModel(
                                model_id=data.get("model_id", filename.replace(".json", "")),
                                name=data.get("name", "Unknown Model"),
                                description=data.get("description", ""),
                                model_size=data.get("model_size", "medium"),
                                parameter_count=data.get("parameter_count", 0),
                                requires_gpu=data.get("requires_gpu", True),
                                disk_size_mb=data.get("disk_size_mb", 0),
                                ram_required_mb=data.get("ram_required_mb", 0),
                                supported_languages=data.get("supported_languages", ["English"]),
                                specialized_for=data.get("specialized_for", []),
                                fine_tunable=data.get("fine_tunable", True),
                                source_url=data.get("source_url"),
                                license=data.get("license", "open"),
                                version=data.get("version", "1.0"),
                                metadata=data.get("metadata", {})
                            )
                            self.llm_models[llm_model.model_id] = llm_model
                    except Exception as e:
                        logger.error(f"Error loading LLM model from {file_path}: {e}")
                        
            logger.info(f"Loaded {len(self.resources)} resources, {len(self.services)} services, {len(self.intranets)} intranets, and {len(self.llm_models)} LLM models")
            
        except Exception as e:
            logger.error(f"Error loading intranet data: {e}")
    
    def _save_resource(self, resource: KnowledgeResource) -> None:
        """Save resource to disk."""
        try:
            file_path = os.path.join(self.data_path, "resources", f"{resource.resource_id}.json")
            
            # Prepare resource data
            resource_data = {
                "resource_id": resource.resource_id,
                "title": resource.title,
                "description": resource.description,
                "category": resource.category.name,
                "resource_type": resource.resource_type.name,
                "file_path": resource.file_path,
                "creator_id": resource.creator_id,
                "created_date": resource.created_date,
                "last_updated_date": resource.last_updated_date,
                "tags": resource.tags,
                "related_resources": resource.related_resources,
                "permissions": resource.permissions,
                "version": resource.version,
                "size_bytes": resource.size_bytes,
                "metadata": resource.metadata
            }
            
            with open(file_path, "w") as f:
                json.dump(resource_data, f, indent=2)
                
        except Exception as e:
            logger.error(f"Error saving resource: {e}")
    
    def _save_service(self, service: TownService) -> None:
        """Save service to disk."""
        try:
            file_path = os.path.join(self.data_path, "services", f"{service.service_id}.json")
            
            # Prepare service data
            service_data = {
                "service_id": service.service_id,
                "name": service.name,
                "description": service.description,
                "service_type": service.service_type,
                "endpoint_url": service.endpoint_url,
                "requires_authentication": service.requires_authentication,
                "access_level": service.access_level,
                "status": service.status,
                "dependencies": service.dependencies,
                "admin_contact": service.admin_contact,
                "metadata": service.metadata
            }
            
            with open(file_path, "w") as f:
                json.dump(service_data, f, indent=2)
                
        except Exception as e:
            logger.error(f"Error saving service: {e}")
    
    def _save_intranet(self, intranet: CommunityIntranet) -> None:
        """Save intranet to disk."""
        try:
            file_path = os.path.join(self.data_path, "intranets", f"{intranet.intranet_id}.json")
            
            # Prepare intranet data
            intranet_data = {
                "intranet_id": intranet.intranet_id,
                "community_id": intranet.community_id,
                "name": intranet.name,
                "description": intranet.description,
                "domain": intranet.domain,
                "network_type": intranet.network_type,
                "installation_date": intranet.installation_date,
                "services": intranet.services,
                "administrators": intranet.administrators,
                "backup_schedule": intranet.backup_schedule,
                "offline_functionality": intranet.offline_functionality,
                "server_hardware": intranet.server_hardware,
                "network_topology": intranet.network_topology,
                "security_measures": intranet.security_measures,
                "metadata": intranet.metadata
            }
            
            with open(file_path, "w") as f:
                json.dump(intranet_data, f, indent=2)
                
        except Exception as e:
            logger.error(f"Error saving intranet: {e}")
    
    def _save_llm_model(self, llm_model: LocalLLMModel) -> None:
        """Save LLM model to disk."""
        try:
            file_path = os.path.join(self.data_path, "llm_models", f"{llm_model.model_id}.json")
            
            # Prepare LLM model data
            llm_model_data = {
                "model_id": llm_model.model_id,
                "name": llm_model.name,
                "description": llm_model.description,
                "model_size": llm_model.model_size,
                "parameter_count": llm_model.parameter_count,
                "requires_gpu": llm_model.requires_gpu,
                "disk_size_mb": llm_model.disk_size_mb,
                "ram_required_mb": llm_model.ram_required_mb,
                "supported_languages": llm_model.supported_languages,
                "specialized_for": llm_model.specialized_for,
                "fine_tunable": llm_model.fine_tunable,
                "source_url": llm_model.source_url,
                "license": llm_model.license,
                "version": llm_model.version,
                "metadata": llm_model.metadata
            }
            
            with open(file_path, "w") as f:
                json.dump(llm_model_data, f, indent=2)
                
        except Exception as e:
            logger.error(f"Error saving LLM model: {e}")
    
    def _initialize_default_services(self) -> None:
        """Initialize default town intranet services."""
        default_services = [
            # Secure Mesh Communication
            TownService(
                service_id="mesh_communication",
                name="Secure Mesh Communication",
                description="Decentralized communication service using mesh networking for resilient, secure messaging and data sharing.",
                service_type="communication",
                endpoint_url="http://localhost:7000/api/mesh",
                requires_authentication=True,
                access_level="all",
                status="active",
                dependencies=["local_identity"],
                metadata={
                    "protocols": ["matrix", "scuttlebutt"],
                    "encryption": "end-to-end",
                    "offline_capable": True,
                    "data_persistence": "local_first",
                    "synchronization": "eventual_consistency"
                }
            ),
            
            # Local Identity Service
            TownService(
                service_id="local_identity",
                name="Local Identity Service",
                description="Self-sovereign identity management for community members with cryptographic verification and privacy controls.",
                service_type="identity",
                endpoint_url="http://localhost:7001/api/identity",
                requires_authentication=True,
                access_level="all",
                status="active",
                dependencies=[],
                metadata={
                    "id_format": "did",
                    "key_management": "local",
                    "verification_method": "challenge-response",
                    "private_key_storage": "secure_enclave",
                    "supports_attestations": True
                }
            ),
            
            # Knowledge Repository
            TownService(
                service_id="knowledge_repo",
                name="Community Knowledge Repository",
                description="Searchable database of community knowledge, documentation, and learning resources with offline access.",
                service_type="data_storage",
                endpoint_url="http://localhost:7002/api/knowledge",
                requires_authentication=True,
                access_level="all",
                status="active",
                dependencies=["local_identity"],
                metadata={
                    "storage_format": "git-lfs",
                    "search_engine": "tantivy",
                    "categorization": "folksonomy",
                    "versioning": True,
                    "full_text_search": True,
                    "supports_rich_media": True,
                    "offline_sync": True
                }
            ),
            
            # Local LLM Service
            TownService(
                service_id="local_llm",
                name="Local Language Model Service",
                description="Locally hosted language models for AI assistance without external dependencies or data leakage.",
                service_type="ai",
                endpoint_url="http://localhost:7003/api/llm",
                requires_authentication=True,
                access_level="all",
                status="active",
                dependencies=["local_identity", "knowledge_repo"],
                metadata={
                    "inference_engine": "llama.cpp",
                    "privacy_preserving": True,
                    "context_window": 8192,
                    "supports_fine_tuning": True,
                    "hardware_acceleration": "optional",
                    "quantization": "4-bit",
                    "model_switching": True
                }
            ),
            
            # Community Calendar
            TownService(
                service_id="community_calendar",
                name="Community Calendar and Coordination",
                description="Shared calendar for community events, work coordination, and resource scheduling.",
                service_type="coordination",
                endpoint_url="http://localhost:7004/api/calendar",
                requires_authentication=True,
                access_level="all",
                status="active",
                dependencies=["local_identity", "mesh_communication"],
                metadata={
                    "supports_recurrence": True,
                    "resource_booking": True,
                    "skill_matching": True,
                    "notifications": True,
                    "export_formats": ["ical", "csv"],
                    "consensus_features": True
                }
            ),
            
            # Resource Inventory
            TownService(
                service_id="resource_inventory",
                name="Community Resource Inventory",
                description="Tracking and management system for community resources, tools, materials, and skills.",
                service_type="inventory",
                endpoint_url="http://localhost:7005/api/inventory",
                requires_authentication=True,
                access_level="all",
                status="active",
                dependencies=["local_identity", "community_calendar"],
                metadata={
                    "tracking_methods": ["qr-code", "manual"],
                    "sharing_economy": True,
                    "maintenance_tracking": True,
                    "resource_matching": True,
                    "visualizations": True,
                    "supports_geolocation": True
                }
            ),
            
            # Decision Support
            TownService(
                service_id="decision_support",
                name="Consensus Decision Support",
                description="Tools for facilitating community decision-making using various governance models.",
                service_type="governance",
                endpoint_url="http://localhost:7006/api/governance",
                requires_authentication=True,
                access_level="all",
                status="active",
                dependencies=["local_identity", "mesh_communication"],
                metadata={
                    "decision_methods": ["consensus", "sociocracy", "voting"],
                    "proposal_tracking": True,
                    "discussion_threading": True,
                    "anonymized_feedback": True,
                    "outcome_documentation": True,
                    "conflict_resolution_tools": True
                }
            ),
            
            # Local Maps
            TownService(
                service_id="local_maps",
                name="Community Mapping Service",
                description="Detailed local maps with infrastructure, resources, hazards, and ecological features.",
                service_type="spatial",
                endpoint_url="http://localhost:7007/api/maps",
                requires_authentication=True,
                access_level="all",
                status="active",
                dependencies=["local_identity"],
                metadata={
                    "map_formats": ["vector", "raster"],
                    "offline_maps": True,
                    "collaborative_editing": True,
                    "layers": ["infrastructure", "ecology", "resources", "hazards"],
                    "3d_visualization": True,
                    "temporal_data": True
                }
            )
        ]
        
        # Add services
        for service in default_services:
            self.services[service.service_id] = service
            self._save_service(service)
            
        logger.info(f"Initialized {len(default_services)} default intranet services")
    
    def _initialize_default_llm_models(self) -> None:
        """Initialize default local LLM models."""
        default_models = [
            # Lightweight Assistant
            LocalLLMModel(
                model_id="lightweight_assistant",
                name="Community Assistant (Lightweight)",
                description="Efficient general-purpose assistant optimized for low-resource hardware.",
                model_size="small",
                parameter_count=1100000000,  # 1.1B
                requires_gpu=False,
                disk_size_mb=600,
                ram_required_mb=2048,
                supported_languages=["English"],
                specialized_for=["general_assistance", "text_completion", "summarization"],
                fine_tunable=True,
                source_url="https://example.org/models/lightweight",
                license="Apache-2.0",
                version="1.0",
                metadata={
                    "architecture": "transformer",
                    "quantization": "4-bit",
                    "prompt_format": "standard",
                    "min_hardware": "Raspberry Pi 4 (4GB)",
                    "context_window": 2048,
                    "training_domains": ["general_knowledge", "basic_coding", "simple_reasoning"]
                }
            ),
            
            # Technical Knowledge LLM
            LocalLLMModel(
                model_id="technical_specialist",
                name="Technical Knowledge Specialist",
                description="Specialized model focused on practical technical knowledge for resilient systems.",
                model_size="medium",
                parameter_count=7000000000,  # 7B
                requires_gpu=True,
                disk_size_mb=3500,
                ram_required_mb=8192,
                supported_languages=["English"],
                specialized_for=["technical_documentation", "system_design", "troubleshooting", "agriculture", "energy_systems", "water_systems"],
                fine_tunable=True,
                source_url="https://example.org/models/technical_specialist",
                license="MIT",
                version="1.0",
                metadata={
                    "architecture": "transformer",
                    "quantization": "4-bit",
                    "prompt_format": "standard",
                    "min_hardware": "NVIDIA Jetson Nano or equivalent",
                    "context_window": 8192,
                    "training_domains": ["technical_manuals", "scientific_literature", "engineering", "permaculture", "appropriate_technology"]
                }
            ),
            
            # Ecological Knowledge LLM
            LocalLLMModel(
                model_id="ecological_knowledge",
                name="Bioregional Ecological Assistant",
                description="Specialized model for ecological knowledge, biodiversity, and ecosystem management.",
                model_size="medium",
                parameter_count=7000000000,  # 7B
                requires_gpu=True,
                disk_size_mb=3500,
                ram_required_mb=8192,
                supported_languages=["English"],
                specialized_for=["ecology", "biodiversity", "conservation", "climate_adaptation", "forest_management", "watershed_management"],
                fine_tunable=True,
                source_url="https://example.org/models/ecological",
                license="CC-BY-NC-4.0",
                version="1.0",
                metadata={
                    "architecture": "transformer",
                    "quantization": "4-bit",
                    "prompt_format": "standard",
                    "min_hardware": "NVIDIA Jetson Nano or equivalent",
                    "context_window": 6144,
                    "training_domains": ["ecology_textbooks", "scientific_papers", "field_guides", "indigenous_knowledge", "conservation_literature"]
                }
            ),
            
            # Governance Assistant
            LocalLLMModel(
                model_id="governance_assistant",
                name="Community Governance Assistant",
                description="Specialized model for facilitation, governance processes, and conflict resolution.",
                model_size="medium",
                parameter_count=7000000000,  # 7B
                requires_gpu=True,
                disk_size_mb=3500,
                ram_required_mb=8192,
                supported_languages=["English"],
                specialized_for=["facilitation", "conflict_resolution", "governance", "consensus", "sociocracy", "group_process", "decision_making"],
                fine_tunable=True,
                source_url="https://example.org/models/governance",
                license="CC-BY-NC-4.0",
                version="1.0",
                metadata={
                    "architecture": "transformer",
                    "quantization": "4-bit",
                    "prompt_format": "standard",
                    "min_hardware": "NVIDIA Jetson Nano or equivalent",
                    "context_window": 8192,
                    "training_domains": ["governance_literature", "facilitation_guides", "case_studies", "conflict_resolution", "group_dynamics"]
                }
            ),
            
            # Multi-domain Reference LLM
            LocalLLMModel(
                model_id="comprehensive_reference",
                name="Comprehensive Reference Model",
                description="Larger, more comprehensive model with extensive knowledge across multiple domains.",
                model_size="large",
                parameter_count=30000000000,  # 30B
                requires_gpu=True,
                disk_size_mb=16000,
                ram_required_mb=24576,
                supported_languages=["English", "Spanish", "French", "German"],
                specialized_for=["general_knowledge", "academic_research", "creative_writing", "reasoning", "education"],
                fine_tunable=False,  # Too large for fine-tuning on typical community hardware
                source_url="https://example.org/models/comprehensive",
                license="CC-BY-NC-4.0",
                version="1.0",
                metadata={
                    "architecture": "transformer",
                    "quantization": "4-bit",
                    "prompt_format": "standard",
                    "min_hardware": "NVIDIA RTX 3080 or equivalent",
                    "context_window": 16384,
                    "training_domains": ["general_knowledge", "academic_literature", "technical_documentation", "creative_works", "mathematics", "science"]
                }
            )
        ]
        
        # Add models
        for model in default_models:
            self.llm_models[model.model_id] = model
            self._save_llm_model(model)
            
        logger.info(f"Initialized {len(default_models)} default LLM models")
    
    def add_resource(self, resource: Dict[str, Any]) -> Dict[str, Any]:
        """
        Add a knowledge resource.
        
        Args:
            resource: Resource information
            
        Returns:
            Addition result
        """
        try:
            # Validate required fields
            required_fields = ["title", "description", "category", "resource_type", "file_path"]
            for field in required_fields:
                if field not in resource:
                    return {
                        "success": False,
                        "error": f"Missing required field: {field}"
                    }
                    
            # Generate ID if not provided
            resource_id = resource.get("resource_id")
            if not resource_id:
                resource_id = f"resource_{hashlib.md5(f'{resource['title']}_{time.time()}'.encode()).hexdigest()[:8]}"
                
            # Parse category
            try:
                category = KnowledgeCategory[resource["category"]]
            except KeyError:
                return {
                    "success": False,
                    "error": f"Invalid knowledge category: {resource['category']}"
                }
                
            # Parse resource type
            try:
                resource_type = ResourceType[resource["resource_type"]]
            except KeyError:
                return {
                    "success": False,
                    "error": f"Invalid resource type: {resource['resource_type']}"
                }
                
            # Create resource
            new_resource = KnowledgeResource(
                resource_id=resource_id,
                title=resource["title"],
                description=resource["description"],
                category=category,
                resource_type=resource_type,
                file_path=resource["file_path"],
                creator_id=resource.get("creator_id"),
                created_date=resource.get("created_date", time.time()),
                last_updated_date=resource.get("last_updated_date", time.time()),
                tags=resource.get("tags", []),
                related_resources=resource.get("related_resources", []),
                permissions=resource.get("permissions", {}),
                version=resource.get("version", "1.0"),
                size_bytes=resource.get("size_bytes"),
                metadata=resource.get("metadata", {})
            )
            
            # Add resource
            self.resources[resource_id] = new_resource
            
            # Save to disk
            self._save_resource(new_resource)
            
            return {
                "success": True,
                "resource_id": resource_id,
                "message": f"Added resource: {new_resource.title}"
            }
            
        except Exception as e:
            logger.error(f"Error adding resource: {e}")
            return {
                "success": False,
                "error": f"Resource addition error: {str(e)}"
            }
    
    def create_intranet(self, intranet: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a community intranet.
        
        Args:
            intranet: Intranet information
            
        Returns:
            Creation result
        """
        try:
            # Validate required fields
            required_fields = ["community_id", "name", "description"]
            for field in required_fields:
                if field not in intranet:
                    return {
                        "success": False,
                        "error": f"Missing required field: {field}"
                    }
                    
            # Generate ID if not provided
            intranet_id = intranet.get("intranet_id")
            if not intranet_id:
                intranet_id = f"intranet_{hashlib.md5(f'{intranet['name']}_{time.time()}'.encode()).hexdigest()[:8]}"
                
            # Create default services list if not provided
            services = intranet.get("services")
            if not services:
                services = [service_id for service_id in self.services.keys()]
                
            # Create intranet
            new_intranet = CommunityIntranet(
                intranet_id=intranet_id,
                community_id=intranet["community_id"],
                name=intranet["name"],
                description=intranet["description"],
                domain=intranet.get("domain"),
                network_type=intranet.get("network_type", "mesh"),
                installation_date=intranet.get("installation_date", time.time()),
                services=services,
                administrators=intranet.get("administrators", []),
                backup_schedule=intranet.get("backup_schedule", "daily"),
                offline_functionality=intranet.get("offline_functionality", True),
                server_hardware=intranet.get("server_hardware", self._get_default_server_hardware()),
                network_topology=intranet.get("network_topology", self._get_default_network_topology()),
                security_measures=intranet.get("security_measures", self._get_default_security_measures()),
                metadata=intranet.get("metadata", {})
            )
            
            # Add intranet
            self.intranets[intranet_id] = new_intranet
            
            # Save to disk
            self._save_intranet(new_intranet)
            
            return {
                "success": True,
                "intranet_id": intranet_id,
                "message": f"Created intranet: {new_intranet.name}",
                "services_configured": len(services)
            }
            
        except Exception as e:
            logger.error(f"Error creating intranet: {e}")
            return {
                "success": False,
                "error": f"Intranet creation error: {str(e)}"
            }
    
    def _get_default_server_hardware(self) -> Dict[str, Any]:
        """Get default server hardware configuration."""
        return {
            "primary_server": {
                "type": "raspberry_pi",
                "model": "Raspberry Pi 4 Model B",
                "ram_gb": 8,
                "storage_gb": 128,
                "processor": "Quad-core Cortex-A72",
                "power_consumption_watts": 5
            },
            "backup_server": {
                "type": "raspberry_pi",
                "model": "Raspberry Pi 4 Model B",
                "ram_gb": 4,
                "storage_gb": 64,
                "processor": "Quad-core Cortex-A72",
                "power_consumption_watts": 5
            },
            "gpu_accelerator": {
                "type": "nvidia_jetson",
                "model": "Jetson Nano",
                "ram_gb": 4,
                "cuda_cores": 128,
                "power_consumption_watts": 10
            },
            "storage_array": {
                "type": "external_raid",
                "capacity_tb": 4,
                "raid_level": "RAID-1",
                "drive_count": 2,
                "connection": "USB 3.0",
                "power_consumption_watts": 8
            },
            "power_system": {
                "type": "solar_battery",
                "solar_watts": 200,
                "battery_capacity_wh": 1500,
                "backup_runtime_hours": 48
            },
            "networking": {
                "primary_router": "Mesh-capable WiFi 6 router",
                "mesh_nodes": 5,
                "radio_backup": "LoRa module"
            }
        }
    
    def _get_default_network_topology(self) -> Dict[str, Any]:
        """Get default network topology configuration."""
        return {
            "type": "hybrid_mesh",
            "components": [
                {
                    "name": "core_mesh",
                    "nodes": [
                        {"id": "central", "type": "server", "connections": ["n1", "n2", "n3", "n4"]},
                        {"id": "n1", "type": "mesh", "connections": ["central", "n2", "n5"]},
                        {"id": "n2", "type": "mesh", "connections": ["central", "n1", "n3", "n6"]},
                        {"id": "n3", "type": "mesh", "connections": ["central", "n2", "n4", "n7"]},
                        {"id": "n4", "type": "mesh", "connections": ["central", "n3", "n8"]}
                    ]
                },
                {
                    "name": "extended_mesh",
                    "nodes": [
                        {"id": "n5", "type": "relay", "connections": ["n1", "n9", "n10"]},
                        {"id": "n6", "type": "relay", "connections": ["n2", "n11", "n12"]},
                        {"id": "n7", "type": "relay", "connections": ["n3", "n13", "n14"]},
                        {"id": "n8", "type": "relay", "connections": ["n4", "n15", "n16"]}
                    ]
                },
                {
                    "name": "client_nodes",
                    "nodes": [
                        {"id": "n9", "type": "client", "connections": ["n5"]},
                        {"id": "n10", "type": "client", "connections": ["n5"]},
                        {"id": "n11", "type": "client", "connections": ["n6"]},
                        {"id": "n12", "type": "client", "connections": ["n6"]},
                        {"id": "n13", "type": "client", "connections": ["n7"]},
                        {"id": "n14", "type": "client", "connections": ["n7"]},
                        {"id": "n15", "type": "client", "connections": ["n8"]},
                        {"id": "n16", "type": "client", "connections": ["n8"]}
                    ]
                }
            ],
            "redundancy_paths": [
                ["central", "n1", "n5", "n10"],
                ["central", "n2", "n6", "n11"],
                ["central", "n3", "n7", "n13"],
                ["central", "n4", "n8", "n15"]
            ],
            "fallback_modes": [
                {
                    "name": "isolated_operation",
                    "trigger": "network_partition",
                    "behavior": "continue_local_operations"
                },
                {
                    "name": "low_power_mode",
                    "trigger": "power_shortage",
                    "behavior": "essential_services_only"
                },
                {
                    "name": "emergency_broadcast",
                    "trigger": "disaster_alert",
                    "behavior": "maximize_reach_minimize_bandwidth"
                }
            ]
        }
    
    def _get_default_security_measures(self) -> List[str]:
        """Get default security measures."""
        return [
            "End-to-end encryption for all communications",
            "Physical server access controls",
            "Offline cryptographic key storage",
            "Multi-factor authentication for administrative access",
            "Regular encrypted backups",
            "Network traffic anomaly detection",
            "Regular security audits",
            "Automated security updates",
            "Resource access permission system",
            "Network isolation capabilities",
            "Data provenance tracking"
        ]
    
    def generate_intranet_deployment_guide(self, intranet_id: str) -> Dict[str, Any]:
        """
        Generate a deployment guide for an intranet.
        
        Args:
            intranet_id: Intranet identifier
            
        Returns:
            Deployment guide
        """
        # Check intranet exists
        if intranet_id not in self.intranets:
            return {
                "success": False,
                "error": "Intranet not found"
            }
            
        try:
            intranet = self.intranets[intranet_id]
            
            # Generate hardware requirements
            hardware_requirements = []
            
            if "primary_server" in intranet.server_hardware:
                server = intranet.server_hardware["primary_server"]
                hardware_requirements.append({
                    "component": "Primary Server",
                    "specifications": f"{server.get('model', 'Server')} with {server.get('ram_gb', 4)}GB RAM, {server.get('storage_gb', 64)}GB storage",
                    "quantity": 1,
                    "estimated_cost": "$150-350",
                    "alternatives": "Any small form-factor computer with similar specifications"
                })
                
            if "backup_server" in intranet.server_hardware:
                server = intranet.server_hardware["backup_server"]
                hardware_requirements.append({
                    "component": "Backup Server",
                    "specifications": f"{server.get('model', 'Server')} with {server.get('ram_gb', 4)}GB RAM, {server.get('storage_gb', 64)}GB storage",
                    "quantity": 1,
                    "estimated_cost": "$150-250",
                    "alternatives": "Can be lower specification than primary server"
                })
                
            if "gpu_accelerator" in intranet.server_hardware:
                gpu = intranet.server_hardware["gpu_accelerator"]
                hardware_requirements.append({
                    "component": "GPU Accelerator",
                    "specifications": f"{gpu.get('model', 'GPU')} with {gpu.get('ram_gb', 4)}GB RAM",
                    "quantity": 1,
                    "estimated_cost": "$150-500",
                    "alternatives": "Optional for basic setups; required for running larger LLMs"
                })
                
            if "storage_array" in intranet.server_hardware:
                storage = intranet.server_hardware["storage_array"]
                hardware_requirements.append({
                    "component": "Storage Array",
                    "specifications": f"{storage.get('capacity_tb', 4)}TB {storage.get('raid_level', 'RAID-1')} array",
                    "quantity": 1,
                    "estimated_cost": "$200-400",
                    "alternatives": "External hard drives with regular backup routine"
                })
                
            if "networking" in intranet.server_hardware:
                networking = intranet.server_hardware["networking"]
                hardware_requirements.append({
                    "component": "Mesh Networking Equipment",
                    "specifications": f"{networking.get('primary_router', 'WiFi router')} with {networking.get('mesh_nodes', 5)} mesh nodes",
                    "quantity": 1,
                    "estimated_cost": "$300-600",
                    "alternatives": "Any mesh-capable WiFi system"
                })
                
            if "power_system" in intranet.server_hardware:
                power = intranet.server_hardware["power_system"]
                hardware_requirements.append({
                    "component": "Power System",
                    "specifications": f"{power.get('solar_watts', 200)}W solar with {power.get('battery_capacity_wh', 1500)}Wh battery storage",
                    "quantity": 1,
                    "estimated_cost": "$500-1000",
                    "alternatives": "Any reliable power source with battery backup"
                })
                
            # Generate software requirements
            software_requirements = []
            
            # Add base system
            software_requirements.append({
                "component": "Base Operating System",
                "specifications": "Debian or Ubuntu Linux LTS",
                "source": "https://ubuntu.com/download/server",
                "notes": "Server version recommended for minimal resource usage"
            })
            
            # Add required services
            for service_id in intranet.services:
                if service_id in self.services:
                    service = self.services[service_id]
                    software_requirements.append({
                        "component": service.name,
                        "specifications": service.description,
                        "source": "Local deployment package",
                        "notes": f"Service type: {service.service_type}"
                    })
                    
            # Add recommended LLMs
            llm_recommendations = []
            
            for model_id, model in self.llm_models.items():
                # Filter for models that can run on the specified hardware
                if not model.requires_gpu or "gpu_accelerator" in intranet.server_hardware:
                    llm_recommendations.append({
                        "model": model.name,
                        "description": model.description,
                        "size": f"{model.disk_size_mb} MB",
                        "requirements": f"RAM: {model.ram_required_mb} MB, {'GPU required' if model.requires_gpu else 'CPU only'}",
                        "use_cases": model.specialized_for
                    })
            
            # Generate deployment phases
            deployment_phases = [
                {
                    "phase": "Preparation",
                    "steps": [
                        "Acquire and prepare hardware components",
                        "Prepare secure, climate-controlled space for server equipment",
                        "Download required software and installation packages",
                        "Document network layout and access information",
                        "Prepare backup power and cooling systems"
                    ],
                    "estimated_time": "1-2 weeks",
                    "prerequisites": "Hardware acquisition, basic technical knowledge"
                },
                {
                    "phase": "Core Infrastructure Setup",
                    "steps": [
                        "Install base operating system",
                        "Configure networking and security settings",
                        "Set up storage systems and backup routines",
                        "Deploy container management system",
                        "Configure power management and monitoring"
                    ],
                    "estimated_time": "2-3 days",
                    "prerequisites": "Completed preparation phase"
                },
                {
                    "phase": "Service Deployment",
                    "steps": [
                        "Deploy identity and authentication service",
                        "Deploy mesh communication service",
                        "Deploy knowledge repository",
                        "Deploy LLM service and download models",
                        "Deploy community coordination services",
                        "Configure service integration and dependencies"
                    ],
                    "estimated_time": "3-5 days",
                    "prerequisites": "Completed core infrastructure setup"
                },
                {
                    "phase": "Testing and Validation",
                    "steps": [
                        "Test all individual services",
                        "Validate service integration",
                        "Perform security assessment",
                        "Test failure scenarios and recovery",
                        "Optimize performance and resource usage"
                    ],
                    "estimated_time": "2-3 days",
                    "prerequisites": "Completed service deployment"
                },
                {
                    "phase": "Community Onboarding",
                    "steps": [
                        "Create initial administrator accounts",
                        "Document user onboarding process",
                        "Prepare training materials for community members",
                        "Conduct initial training sessions",
                        "Establish support and maintenance procedures"
                    ],
                    "estimated_time": "1 week",
                    "prerequisites": "Completed testing and validation"
                },
                {
                    "phase": "Knowledge Population",
                    "steps": [
                        "Import initial knowledge repository content",
                        "Configure LLMs with community-specific knowledge",
                        "Document local resources and skills",
                        "Create initial community calendar and events",
                        "Establish knowledge curation processes"
                    ],
                    "estimated_time": "1-2 weeks (ongoing)",
                    "prerequisites": "Completed community onboarding"
                }
            ]
            
            # Generate maintenance guidelines
            maintenance_guidelines = [
                {
                    "category": "Regular Backups",
                    "frequency": "Daily automated, weekly verified",
                    "procedures": [
                        "Automated daily backup to local storage",
                        "Weekly backup verification check",
                        "Monthly backup to offline storage",
                        "Quarterly full system backup"
                    ],
                    "responsibility": "System administrators"
                },
                {
                    "category": "Security Updates",
                    "frequency": "Weekly",
                    "procedures": [
                        "Review available security updates",
                        "Test updates on backup system",
                        "Apply updates during low-usage window",
                        "Verify system functionality post-update"
                    ],
                    "responsibility": "System administrators"
                },
                {
                    "category": "Hardware Maintenance",
                    "frequency": "Monthly",
                    "procedures": [
                        "Check for hardware errors in logs",
                        "Inspect physical hardware condition",
                        "Clean cooling systems and dust filters",
                        "Test backup power systems"
                    ],
                    "responsibility": "Hardware team"
                },
                {
                    "category": "Network Monitoring",
                    "frequency": "Continuous, weekly review",
                    "procedures": [
                        "Automated monitoring of network performance",
                        "Weekly review of connection quality",
                        "Monthly testing of fallback communication modes",
                        "Quarterly review of network topology"
                    ],
                    "responsibility": "Network team"
                },
                {
                    "category": "Knowledge Management",
                    "frequency": "Ongoing, monthly review",
                    "procedures": [
                        "Community contribution monitoring",
                        "Content quality review",
                        "Content organization and tagging",
                        "Identification of knowledge gaps"
                    ],
                    "responsibility": "Knowledge stewards"
                },
                {
                    "category": "User Support",
                    "frequency": "Daily",
                    "procedures": [
                        "Monitor user support requests",
                        "Address access issues promptly",
                        "Document common issues and solutions",
                        "Identify training needs"
                    ],
                    "responsibility": "Support team"
                }
            ]
            
            # Return complete deployment guide
            return {
                "success": True,
                "intranet_id": intranet_id,
                "intranet_name": intranet.name,
                "community_id": intranet.community_id,
                "hardware_requirements": hardware_requirements,
                "software_requirements": software_requirements,
                "llm_recommendations": llm_recommendations,
                "deployment_phases": deployment_phases,
                "maintenance_guidelines": maintenance_guidelines,
                "total_estimated_cost": f"${sum(int(req['estimated_cost'].split('-')[0].replace('"""
GaiaBioregionalHarmony: Ecological Balance and Community Restoration Module
Version: 0.1 Alpha
Description: A Gaia-level implementation for the PulseHuman framework enabling
             bioregional rebalancing, collaborative relocation, and the creation
             of decentralized, ecologically harmonious communities connected
             through mutual aid networks.
"""

import os
import time
import logging
import asyncio
import json
import hashlib
import sqlite3
import math
import random
from typing import Dict, List, Tuple, Optional, Any, Union, Set, Callable
from dataclasses import dataclass, field
from enum import Enum, auto
from pathlib import Path

# Import from PulseHuman
from PulseHuman import (
    DevelopmentalStage, HumanDevelopmentalMode, DevelopmentalActivity,
    HumanDevelopmentalProgress, PulseHumanEngine, PulseHumanActivities
)

# Import from PulseEcoRecovery
from PulseEcoRecovery import (
    KnowledgeRepository, ResilienceBridgeCoordinator,
    ResilienceEducationModule, SystemsArchitectModule
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("gaia_bioregional")


# ====================================================================
# 1. BIOREGION MAPPING AND ANALYSIS
# ====================================================================

class ClimateZone(Enum):
    """Climate zones for bioregional mapping."""
    RAINFOREST = auto()      # Hot, wet year-round
    MONSOON = auto()         # Seasonal heavy rainfall
    SAVANNA = auto()         # Tropical wet and dry
    DESERT_HOT = auto()      # Hot, arid
    DESERT_COLD = auto()     # Cold, arid
    STEPPE_HOT = auto()      # Hot, semi-arid
    STEPPE_COLD = auto()     # Cold, semi-arid
    MEDITERRANEAN = auto()   # Hot dry summers, mild wet winters
    HUMID_SUBTROPICAL = auto() # Hot humid summers, mild winters
    OCEANIC = auto()         # Warm to cool, year-round precipitation
    CONTINENTAL_HOT = auto() # Hot summers, cold winters
    CONTINENTAL_WARM = auto() # Warm summers, cold winters
    CONTINENTAL_COOL = auto() # Cool summers, cold winters
    SUBARCTIC = auto()       # Short cool summers, very cold winters
    TUNDRA = auto()          # Very short cool summers, very cold winters
    POLAR_ICE = auto()       # Perpetual ice and snow
    MOUNTAIN = auto()        # Variable by elevation


class EcosystemType(Enum):
    """Major ecosystem types."""
    FOREST_TEMPERATE = auto()  # Temperate forest
    FOREST_TROPICAL = auto()   # Tropical forest
    FOREST_BOREAL = auto()     # Boreal/Taiga forest
    GRASSLAND = auto()         # Grasslands/Prairie/Savanna
    DESERT = auto()            # Desert ecosystems
    SHRUBLAND = auto()         # Chaparral/Shrubland
    TUNDRA = auto()            # Arctic/alpine tundra
    WETLAND = auto()           # Wetlands/Marshes/Swamps
    FRESHWATER = auto()        # Lakes/Rivers/Streams
    COASTAL = auto()           # Coastal ecosystems
    MARINE = auto()            # Marine ecosystems
    ALPINE = auto()            # Mountain ecosystems
    URBAN = auto()             # Urban ecosystems
    AGRICULTURAL = auto()      # Agricultural ecosystems


class WaterAvailability(Enum):
    """Water availability classification."""
    ABUNDANT = auto()        # Plentiful year-round surface and groundwater
    SUFFICIENT = auto()      # Adequate with proper management
    SEASONAL = auto()        # Abundant seasonally, limited other times
    STRESSED = auto()        # Currently adequate but facing stress
    SCARCE = auto()          # Limited availability, careful management required
    CRITICAL = auto()        # Severe shortage, urgent conservation needed


class SoilQuality(Enum):
    """Soil quality classification."""
    EXCELLENT = auto()       # Deep, fertile, well-structured
    GOOD = auto()            # Fertile with some limitations
    MODERATE = auto()        # Workable but needs amendments
    POOR = auto()            # Significant limitations
    DEGRADED = auto()        # Damaged by erosion/contamination


class InfrastructureStatus(Enum):
    """Infrastructure status classification."""
    MODERN = auto()          # Up-to-date, well-maintained
    ADEQUATE = auto()        # Functional but aging
    DEGRADED = auto()        # Partially functional, needs significant repair
    MINIMAL = auto()         # Basic infrastructure only
    ABSENT = auto()          # Little to no existing infrastructure


class PopulationDensity(Enum):
    """Population density classification."""
    URBAN_DENSE = auto()     # Dense city centers
    URBAN_MODERATE = auto()  # Urban but not dense
    SUBURBAN = auto()        # Suburban areas
    RURAL_DEVELOPED = auto() # Developed rural
    RURAL_SPARSE = auto()    # Sparsely populated
    WILDERNESS = auto()      # Virtually uninhabited


@dataclass
class BioregionMetrics:
    """Metrics for bioregional analysis."""
    climate_zone: ClimateZone
    ecosystem_types: List[EcosystemType]
    water_availability: WaterAvailability
    soil_quality: SoilQuality
    infrastructure_status: InfrastructureStatus
    population_density: PopulationDensity
    land_availability_acres: float
    climate_resilience_score: float  # 0-10 scale
    current_population: int
    optimal_population: int
    agricultural_capacity_people: int
    renewable_energy_potential: Dict[str, float]  # kWh/year by type
    ecological_health_score: float  # 0-10 scale
    natural_disaster_risk: Dict[str, float]  # Risk scores by disaster type


@dataclass
class USRegion:
    """US region for bioregional analysis."""
    region_id: str
    name: str
    states: List[str]
    major_cities: List[str]
    center_lat: float
    center_long: float
    area_sq_miles: float
    metrics: BioregionMetrics
    watersheds: List[str]
    key_resources: List[str]
    special_considerations: List[str]
    proposed_communities: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class HumanSkillProfile:
    """Profile of skills for bioregional matching."""
    skill_categories: Dict[str, float]  # Category -> proficiency level (0-1)
    career_experience: List[str]
    physical_capabilities: Dict[str, float]  # Capability -> level (0-1)
    climate_preferences: List[ClimateZone]
    community_role_preferences: List[str]
    relocation_readiness: float  # 0-1 scale
    requires_specialized_healthcare: bool
    dependent_family_members: int
    special_considerations: List[str]
    interests: List[str]


@dataclass
class RelocationMatch:
    """Match between human and bioregion for relocation."""
    human_id: str
    region_id: str
    community_id: Optional[str]
    compatibility_score: float  # 0-1 scale
    skill_match_score: float  # 0-1 scale
    climate_match_score: float  # 0-1 scale
    needs_match_score: float  # 0-1 scale
    role_recommendations: List[str]
    rationale: str
    suggested_preparation: List[str]


class BioregionalMapper:
    """
    Analyzes and maps bioregions for sustainable community development.
    """
    
    def __init__(self, data_path: str = "bioregional_data"):
        """
        Initialize bioregional mapper.
        
        Args:
            data_path: Path for storing bioregional data
        """
        self.data_path = data_path
        
        # Ensure paths exist
        os.makedirs(data_path, exist_ok=True)
        os.makedirs(os.path.join(data_path, "regions"), exist_ok=True)
        os.makedirs(os.path.join(data_path, "communities"), exist_ok=True)
        
        # Load US regions
        self.us_regions: Dict[str, USRegion] = {}
        self._load_us_regions()
        
        # Initialize with default regions if none exist
        if not self.us_regions:
            self._initialize_default_regions()
    
    def _load_us_regions(self) -> None:
        """Load US regions from disk."""
        try:
            # Load regions
            regions_dir = os.path.join(self.data_path, "regions")
            for filename in os.listdir(regions_dir):
                if filename.endswith(".json"):
                    file_path = os.path.join(regions_dir, filename)
                    try:
                        with open(file_path, "r") as f:
                            data = json.load(f)
                            
                            # Parse metrics
                            metrics_data = data.get("metrics", {})
                            metrics = BioregionMetrics(
                                climate_zone=ClimateZone[metrics_data.get("climate_zone", "CONTINENTAL_WARM")],
                                ecosystem_types=[EcosystemType[et] for et in metrics_data.get("ecosystem_types", ["FOREST_TEMPERATE"])],
                                water_availability=WaterAvailability[metrics_data.get("water_availability", "SUFFICIENT")],
                                soil_quality=SoilQuality[metrics_data.get("soil_quality", "MODERATE")],
                                infrastructure_status=InfrastructureStatus[metrics_data.get("infrastructure_status", "ADEQUATE")],
                                population_density=PopulationDensity[metrics_data.get("population_density", "RURAL_DEVELOPED")],
                                land_availability_acres=metrics_data.get("land_availability_acres", 0.0),
                                climate_resilience_score=metrics_data.get("climate_resilience_score", 5.0),
                                current_population=metrics_data.get("current_population", 0),
                                optimal_population=metrics_data.get("optimal_population", 0),
                                agricultural_capacity_people=metrics_data.get("agricultural_capacity_people", 0),
                                renewable_energy_potential=metrics_data.get("renewable_energy_potential", {}),
                                ecological_health_score=metrics_data.get("ecological_health_score", 5.0),
                                natural_disaster_risk=metrics_data.get("natural_disaster_risk", {})
                            )
                            
                            # Create region
                            region = USRegion(
                                region_id=data.get("region_id", filename.replace(".json", "")),
                                name=data.get("name", "Unknown Region"),
                                states=data.get("states", []),
                                major_cities=data.get("major_cities", []),
                                center_lat=data.get("center_lat", 0.0),
                                center_long=data.get("center_long", 0.0),
                                area_sq_miles=data.get("area_sq_miles", 0.0),
                                metrics=metrics,
                                watersheds=data.get("watersheds", []),
                                key_resources=data.get("key_resources", []),
                                special_considerations=data.get("special_considerations", []),
                                proposed_communities=data.get("proposed_communities", []),
                                metadata=data.get("metadata", {})
                            )
                            
                            self.us_regions[region.region_id] = region
                    except Exception as e:
                        logger.error(f"Error loading region from {file_path}: {e}")
                        
            logger.info(f"Loaded {len(self.us_regions)} US regions")
            
        except Exception as e:
            logger.error(f"Error loading US regions: {e}")
    
    def _save_region(self, region: USRegion) -> None:
        """Save region to disk."""
        try:
            file_path = os.path.join(self.data_path, "regions", f"{region.region_id}.json")
            
            # Convert metrics for JSON serialization
            metrics_data = {
                "climate_zone": region.metrics.climate_zone.name,
                "ecosystem_types": [et.name for et in region.metrics.ecosystem_types],
                "water_availability": region.metrics.water_availability.name,
                "soil_quality": region.metrics.soil_quality.name,
                "infrastructure_status": region.metrics.infrastructure_status.name,
                "population_density": region.metrics.population_density.name,
                "land_availability_acres": region.metrics.land_availability_acres,
                "climate_resilience_score": region.metrics.climate_resilience_score,
                "current_population": region.metrics.current_population,
                "optimal_population": region.metrics.optimal_population,
                "agricultural_capacity_people": region.metrics.agricultural_capacity_people,
                "renewable_energy_potential": region.metrics.renewable_energy_potential,
                "ecological_health_score": region.metrics.ecological_health_score,
                "natural_disaster_risk": region.metrics.natural_disaster_risk
            }
            
            # Prepare region data
            region_data = {
                "region_id": region.region_id,
                "name": region.name,
                "states": region.states,
                "major_cities": region.major_cities,
                "center_lat": region.center_lat,
                "center_long": region.center_long,
                "area_sq_miles": region.area_sq_miles,
                "metrics": metrics_data,
                "watersheds": region.watersheds,
                "key_resources": region.key_resources,
                "special_considerations": region.special_considerations,
                "proposed_communities": region.proposed_communities,
                "metadata": region.metadata
            }
            
            with open(file_path, "w") as f:
                json.dump(region_data, f, indent=2)
                
        except Exception as e:
            logger.error(f"Error saving region: {e}")
    
    def _initialize_default_regions(self) -> None:
        """Initialize default US bioregions."""
        default_regions = [
            # Pacific Northwest
            USRegion(
                region_id="pacific_northwest",
                name="Pacific Northwest",
                states=["Washington", "Oregon", "Idaho (western)"],
                major_cities=["Seattle", "Portland", "Spokane", "Eugene", "Olympia"],
                center_lat=47.7511,
                center_long=-120.7401,
                area_sq_miles=163000,
                metrics=BioregionMetrics(
                    climate_zone=ClimateZone.OCEANIC,
                    ecosystem_types=[EcosystemType.FOREST_TEMPERATE, EcosystemType.COASTAL, EcosystemType.ALPINE],
                    water_availability=WaterAvailability.ABUNDANT,
                    soil_quality=SoilQuality.GOOD,
                    infrastructure_status=InfrastructureStatus.MODERN,
                    population_density=PopulationDensity.RURAL_DEVELOPED,
                    land_availability_acres=15000000,
                    climate_resilience_score=7.5,
                    current_population=12000000,
                    optimal_population=15000000,
                    agricultural_capacity_people=20000000,
                    renewable_energy_potential={
                        "hydro": 72000000000,
                        "wind": 45000000000,
                        "solar": 18000000000,
                        "geothermal": 5000000000
                    },
                    ecological_health_score=8.0,
                    natural_disaster_risk={
                        "wildfire": 0.7,
                        "earthquake": 0.6,
                        "flooding": 0.5,
                        "volcanic": 0.3,
                        "drought": 0.3
                    }
                ),
                watersheds=["Columbia River Basin", "Puget Sound"],
                key_resources=["Timber", "Hydropower", "Fisheries", "Fertile valleys"],
                special_considerations=[
                    "Cascadia subduction zone earthquake risk",
                    "Increasing wildfire risk with climate change",
                    "Water abundance but seasonal drought in some areas"
                ]
            ),
            
            # Great Lakes
            USRegion(
                region_id="great_lakes",
                name="Great Lakes Bioregion",
                states=["Michigan", "Wisconsin", "Minnesota", "Illinois (northern)", "Indiana (northern)", "Ohio (northern)"],
                major_cities=["Chicago", "Detroit", "Milwaukee", "Cleveland", "Minneapolis"],
                center_lat=44.1347,
                center_long=-84.6035,
                area_sq_miles=176000,
                metrics=BioregionMetrics(
                    climate_zone=ClimateZone.CONTINENTAL_WARM,
                    ecosystem_types=[EcosystemType.FOREST_TEMPERATE, EcosystemType.FRESHWATER, EcosystemType.GRASSLAND],
                    water_availability=WaterAvailability.ABUNDANT,
                    soil_quality=SoilQuality.GOOD,
                    infrastructure_status=InfrastructureStatus.ADEQUATE,
                    population_density=PopulationDensity.SUBURBAN,
                    land_availability_acres=12000000,
                    climate_resilience_score=7.0,
                    current_population=40000000,
                    optimal_population=30000000,
                    agricultural_capacity_people=60000000,
                    renewable_energy_potential={
                        "wind": 85000000000,
                        "solar": 25000000000,
                        "hydro": 8000000000
                    },
                    ecological_health_score=6.0,
                    natural_disaster_risk={
                        "flooding": 0.5,
                        "blizzard": 0.7,
                        "tornado": 0.4,
                        "drought": 0.3
                    }
                ),
                watersheds=["Great Lakes Basin", "Mississippi River (Upper)"],
                key_resources=["Freshwater", "Fertile farmland", "Forests", "Minerals"],
                special_considerations=[
                    "20% of world's fresh surface water",
                    "Legacy industrial contamination in some areas",
                    "Climate change bringing increased precipitation",
                    "Invasive species challenges"
                ]
            ),
            
            # New England
            USRegion(
                region_id="new_england",
                name="New England",
                states=["Maine", "New Hampshire", "Vermont", "Massachusetts", "Connecticut", "Rhode Island"],
                major_cities=["Boston", "Providence", "Portland", "Burlington"],
                center_lat=43.6615,
                center_long=-70.9989,
                area_sq_miles=72000,
                metrics=BioregionMetrics(
                    climate_zone=ClimateZone.CONTINENTAL_COOL,
                    ecosystem_types=[EcosystemType.FOREST_TEMPERATE, EcosystemType.COASTAL, EcosystemType.FRESHWATER],
                    water_availability=WaterAvailability.SUFFICIENT,
                    soil_quality=SoilQuality.MODERATE,
                    infrastructure_status=InfrastructureStatus.ADEQUATE,
                    population_density=PopulationDensity.SUBURBAN,
                    land_availability_acres=8000000,
                    climate_resilience_score=6.5,
                    current_population=14700000,
                    optimal_population=12000000,
                    agricultural_capacity_people=5000000,
                    renewable_energy_potential={
                        "wind": 42000000000,
                        "solar": 18000000000,
                        "hydro": 6000000000,
                        "tidal": 3000000000
                    },
                    ecological_health_score=7.0,
                    natural_disaster_risk={
                        "blizzard": 0.8,
                        "hurricane": 0.5,
                        "flooding": 0.5,
                        "sea_level_rise": 0.6
                    }
                ),
                watersheds=["Connecticut River", "Merrimack River", "Penobscot River"],
                key_resources=["Forests", "Coastal fisheries", "Hydropower potential", "Cultural heritage"],
                special_considerations=[
                    "Aging infrastructure",
                    "Coastal vulnerability to sea level rise",
                    "Reforestation success story",
                    "Strong local governance traditions"
                ]
            ),
            
            # Ozarks
            USRegion(
                region_id="ozarks",
                name="Ozarks and Upper South",
                states=["Missouri", "Arkansas", "Kentucky", "Tennessee", "Oklahoma (eastern)"],
                major_cities=["Nashville", "Louisville", "Memphis", "Little Rock", "Springfield"],
                center_lat=36.7336,
                center_long=-91.1591,
                area_sq_miles=180000,
                metrics=BioregionMetrics(
                    climate_zone=ClimateZone.HUMID_SUBTROPICAL,
                    ecosystem_types=[EcosystemType.FOREST_TEMPERATE, EcosystemType.FRESHWATER, EcosystemType.GRASSLAND],
                    water_availability=WaterAvailability.SUFFICIENT,
                    soil_quality=SoilQuality.MODERATE,
                    infrastructure_status=InfrastructureStatus.ADEQUATE,
                    population_density=PopulationDensity.RURAL_DEVELOPED,
                    land_availability_acres=25000000,
                    climate_resilience_score=6.0,
                    current_population=18000000,
                    optimal_population=16000000,
                    agricultural_capacity_people=30000000,
                    renewable_energy_potential={
                        "solar": 40000000000,
                        "hydro": 15000000000,
                        "wind": 10000000000
                    },
                    ecological_health_score=6.5,
                    natural_disaster_risk={
                        "tornado": 0.7,
                        "flooding": 0.6,
                        "ice_storm": 0.5,
                        "drought": 0.4
                    }
                ),
                watersheds=["Mississippi River", "Ohio River", "White River", "Arkansas River"],
                key_resources=["Freshwater springs", "Hardwood forests", "Agricultural land", "Caves and karst systems"],
                special_considerations=[
                    "Rich cultural heritage",
                    "Karst topography with sensitive groundwater",
                    "Biodiversity hotspot",
                    "Climate warming may enhance growing season"
                ]
            ),
            
            # Southwest
            USRegion(
                region_id="southwest",
                name="Southwest Desert",
                states=["Arizona", "New Mexico", "Nevada", "Utah (southern)"],
                major_cities=["Phoenix", "Tucson", "Albuquerque", "Las Vegas"],
                center_lat=33.7712,
                center_long=-111.3877,
                area_sq_miles=250000,
                metrics=BioregionMetrics(
                    climate_zone=ClimateZone.DESERT_HOT,
                    ecosystem_types=[EcosystemType.DESERT, EcosystemType.SHRUBLAND, EcosystemType.ALPINE],
                    water_availability=WaterAvailability.CRITICAL,
                    soil_quality=SoilQuality.POOR,
                    infrastructure_status=InfrastructureStatus.ADEQUATE,
                    population_density=PopulationDensity.RURAL_SPARSE,
                    land_availability_acres=75000000,
                    climate_resilience_score=3.5,
                    current_population=18000000,
                    optimal_population=5000000,
                    agricultural_capacity_people=2000000,
                    renewable_energy_potential={
                        "solar": 175000000000,
                        "wind": 30000000000,
                        "geothermal": 10000000000
                    },
                    ecological_health_score=4.5,
                    natural_disaster_risk={
                        "drought": 0.9,
                        "heat": 0.9,
                        "wildfire": 0.7,
                        "flash_flood": 0.6
                    }
                ),
                watersheds=["Colorado River", "Rio Grande", "Gila River"],
                key_resources=["Solar potential", "Minerals", "Indigenous cultural sites", "Desert biodiversity"],
                special_considerations=[
                    "Extreme water scarcity worsening with climate change",
                    "Current population exceeds ecological carrying capacity",
                    "Exceptional solar energy potential",
                    "Fragile desert ecosystems"
                ]
            ),
            
            # Northern Plains
            USRegion(
                region_id="northern_plains",
                name="Northern Plains",
                states=["North Dakota", "South Dakota", "Nebraska", "Montana (eastern)", "Wyoming (eastern)"],
                major_cities=["Omaha", "Lincoln", "Sioux Falls", "Fargo", "Billings"],
                center_lat=44.7237,
                center_long=-100.5547,
                area_sq_miles=355000,
                metrics=BioregionMetrics(
                    climate_zone=ClimateZone.CONTINENTAL_COOL,
                    ecosystem_types=[EcosystemType.GRASSLAND, EcosystemType.FRESHWATER, EcosystemType.AGRICULTURAL],
                    water_availability=WaterAvailability.STRESSED,
                    soil_quality=SoilQuality.EXCELLENT,
                    infrastructure_status=InfrastructureStatus.ADEQUATE,
                    population_density=PopulationDensity.RURAL_SPARSE,
                    land_availability_acres=150000000,
                    climate_resilience_score=5.0,
                    current_population=5000000,
                    optimal_population=9000000,
                    agricultural_capacity_people=80000000,
                    renewable_energy_potential={
                        "wind": 200000000000,
                        "solar": 40000000000,
                        "hydro": 5000000000
                    },
                    ecological_health_score=5.0,
                    natural_disaster_risk={
                        "drought": 0.6,
                        "blizzard": 0.8,
                        "tornado": 0.6,
                        "flooding": 0.5
                    }
                ),
                watersheds=["Missouri River", "Platte River", "Yellowstone River"],
                key_resources=["Fertile farmland", "Grasslands", "Wind potential", "Fossil fuels"],
                special_considerations=[
                    "Depopulating rural areas",
                    "World-class soil for agriculture",
                    "Exceptional wind energy potential",
                    "Climate change bringing more extreme precipitation patterns"
                ]
            )
        ]
        
        # Add regions
        for region in default_regions:
            self.us_regions[region.region_id] = region
            self._save_region(region)
            
        logger.info(f"Initialized {len(default_regions)} default US bioregions")
    
    def get_region(self, region_id: str) -> Optional[USRegion]:
        """
        Get a US bioregion by ID.
        
        Args:
            region_id: Region identifier
            
        Returns:
            Region if found, None otherwise
        """
        return self.us_regions.get(region_id)
    
    def get_all_regions(self) -> List[USRegion]:
        """
        Get all US bioregions.
        
        Returns:
            List of regions
        """
        return list(self.us_regions.values())
    
    def add_region(self, region: USRegion) -> bool:
        """
        Add a new US bioregion.
        
        Args:
            region: Region to add
            
        Returns:
            Success status
        """
        # Check if already exists
        if region.region_id in self.us_regions:
            return False
            
        # Add region
        self.us_regions[region.region_id] = region
        
        # Save to disk
        self._save_region(region)
        
        return True
    
    def update_region(self, region: USRegion) -> bool:
        """
        Update an existing US bioregion.
        
        Args:
            region: Region to update
            
        Returns:
            Success status
        """
        # Check if exists
        if region.region_id not in self.us_regions:
            return False
            
        # Update region
        self.us_regions[region.region_id] = region
        
        # Save to disk
        self._save_region(region)
        
        return True
    
    def find_regions_by_criteria(self, 
                              water_min: WaterAvailability = None,
                              climate_zones: List[ClimateZone] = None,
                              soil_min: SoilQuality = None,
                              population_density: List[PopulationDensity] = None,
                              climate_resilience_min: float = None) -> List[USRegion]:
        """
        Find regions matching specified criteria.
        
        Args:
            water_min: Minimum water availability
            climate_zones: Acceptable climate zones
            soil_min: Minimum soil quality
            population_density: Acceptable population densities
            climate_resilience_min: Minimum climate resilience score
            
        Returns:
            List of matching regions
        """
        matching_regions = []
        
        for region in self.us_regions.values():
            # Check water availability
            if water_min and region.metrics.water_availability.value < water_min.value:
                continue
                
            # Check climate zones
            if climate_zones and region.metrics.climate_zone not in climate_zones:
                continue
                
            # Check soil quality
            if soil_min and region.metrics.soil_quality.value < soil_min.value:
                continue
                
            # Check population density
            if population_density and region.metrics.population_density not in population_density:
                continue
                
            # Check climate resilience
            if climate_resilience_min and region.metrics.climate_resilience_score < climate_resilience_min:
                continue
                
            # All criteria matched
            matching_regions.append(region)
            
        return matching_regions
    
    def calculate_optimal_distribution(self) -> Dict[str, Any]:
        """
        Calculate optimal population distribution across bioregions.
        
        Returns:
            Optimal distribution information
        """
        # Get total current population and capacity
        total_current = sum(region.metrics.current_population for region in self.us_regions.values())
        total_optimal = sum(region.metrics.optimal_population for region in self.us_regions.values())
        total_agricultural_capacity = sum(region.metrics.agricultural_capacity_people for region in self.us_regions.values())
        
        # Calculate distribution
        distribution = {}
        surpluses = []
        deficits = []
        
        for region in self.us_regions.values():
            current = region.metrics.current_population
            optimal = region.metrics.optimal_population
            difference = optimal - current
            
            # Record distribution
            distribution[region.region_id] = {
                "name": region.name,
                "current_population": current,
                "optimal_population": optimal,
                "difference": difference,
                "agricultural_capacity": region.metrics.agricultural_capacity_people,
                "water_availability": region.metrics.water_availability.name,
                "climate_resilience": region.metrics.climate_resilience_score
            }
            
            # Track surpluses and deficits
            if difference > 0:
                deficits.append((region.region_id, difference))
            elif difference < 0:
                surpluses.append((region.region_id, -difference))
        
        # Sort surpluses and deficits by magnitude
        surpluses.sort(key=lambda x: x[1], reverse=True)
        deficits.sort(key=lambda x: x[1], reverse=True)
        
        return {
            "total_current_population": total_current,
            "total_optimal_population": total_optimal,
            "total_agricultural_capacity": total_agricultural_capacity,
            "distribution_by_region": distribution,
            "surplus_regions": surpluses,
            "deficit_regions": deficits
        }
    
    def get_region_compatibility_score(self, human_profile: HumanSkillProfile, region_id: str) -> Dict[str, Any]:
        """
        Calculate compatibility score between a human profile and a bioregion.
        
        Args:
            human_profile: Human skill profile
            region_id: Region identifier
            
        Returns:
            Compatibility assessment
        """
        # Get region
        region = self.us_regions.get(region_id)
        if not region:
            return {
                "success": False,
                "error": f"Region not found: {region_id}"
            }
            
        # Calculate climate match
        climate_match = 0.0
        if region.metrics.climate_zone in human_profile.climate_preferences:
            climate_match = 1.0
        else:
            # Partial matching based on similar climate groups
            for preferred in human_profile.climate_preferences:
                if self._are_climates_similar(preferred, region.metrics.climate_zone):
                    climate_match = 0.5
                    break
        
        # Calculate skill match
        skill_match = 0.0
        needed_skills = self._get_region_needed_skills(region)
        
        for category, importance in needed_skills.items():
            if category in human_profile.skill_categories:
                skill_match += importance * human_profile.skill_categories[category]
                
        # Normalize skill match
        if needed_skills:
            skill_match /= sum(needed_skills.values())
        
        # Calculate needs match (healthcare, family needs, etc.)
        needs_match = 1.0
        
        # Adjust for specialized healthcare
        if human_profile.requires_specialized_healthcare and region.metrics.infrastructure_status.value < InfrastructureStatus.ADEQUATE.value:
            needs_match *= 0.5
            
        # Adjust for family members
        if human_profile.dependent_family_members > 0:
            # Check for educational infrastructure, family services, etc.
            if region.metrics.infrastructure_status.value < InfrastructureStatus.ADEQUATE.value:
                needs_match *= 0.7
        
        # Calculate overall compatibility
        compatibility = (climate_match * 0.3) + (skill_match * 0.4) + (needs_match * 0.3)
        
        # Generate role recommendations
        role_recommendations = self._generate_role_recommendations(human_profile, region)
        
        # Generate rationale
        rationale = self._generate_compatibility_rationale(
            human_profile, region, climate_match, skill_match, needs_match
        )
        
        # Generate suggested preparation
        suggested_preparation = self._generate_preparation_suggestions(human_profile, region)
        
        return {
            "success": True,
            "region_id": region_id,
            "region_name": region.name,
            "compatibility_score": compatibility,
            "climate_match_score": climate_match,
            "skill_match_score": skill_match,
            "needs_match_score": needs_match,
            "role_recommendations": role_recommendations,
            "rationale": rationale,
            "suggested_preparation": suggested_preparation
        }
    
    def _are_climates_similar(self, climate1: ClimateZone, climate2: ClimateZone) -> bool:
        """
        Check if two climate zones are similar.
        
        Args:
            climate1: First climate zone
            climate2: Second climate zone
            
        Returns:
            Whether climates are similar
        """
        # Define climate zone groups
        continental_group = {
            ClimateZone.CONTINENTAL_HOT,
            ClimateZone.CONTINENTAL_WARM,
            ClimateZone.CONTINENTAL_COOL
        }
        
        desert_group = {
            ClimateZone.DESERT_HOT,
            ClimateZone.DESERT_COLD,
            ClimateZone.STEPPE_HOT,
            ClimateZone.STEPPE_COLD
        }
        
        tropical_group = {
            ClimateZone.RAINFOREST,
            ClimateZone.MONSOON,
            ClimateZone.SAVANNA
        }
        
        temperate_group = {
            ClimateZone.MEDITERRANEAN,
            ClimateZone.HUMID_SUBTROPICAL,
            ClimateZone.OCEANIC
        }
        
        cold_group = {
            ClimateZone.SUBARCTIC,
            ClimateZone.TUNDRA,
            ClimateZone.POLAR_ICE
        }
        
        # Check if climates are in the same group
        for group in [continental_group, desert_group, tropical_group, temperate_group, cold_group]:
            if climate1 in group and climate2 in group:
                return True
                
        return False
    
    def _get_region_needed_skills(self, region: USRegion) -> Dict[str, float]:
        """
        Determine skills needed in a region.
        
        Args:
            region: Region to analyze
            
        Returns:
            Dictionary of skill categories and their importance (0-1)
        """
        needed_skills = {}
        
        # Agricultural skills
        if region.metrics.agricultural_capacity_people > 0:
            importance = min(1.0, region.metrics.agricultural_capacity_people / (region.metrics.optimal_population * 0.5))
            needed_skills["agriculture"] = importance
        
        # Water management skills
        if region.metrics.water_availability.value <= WaterAvailability.SUFFICIENT.value:
            water_importance = 1.0 - (region.metrics.water_availability.value / WaterAvailability.ABUNDANT.value)
            needed_skills["water_management"] = water_importance
        
        # Infrastructure skills
        if region.metrics.infrastructure_status.value < InfrastructureStatus.MODERN.value:
            infra_importance = 1.0 - (region.metrics.infrastructure_status.value / InfrastructureStatus.MODERN.value)
            needed_skills["infrastructure"] = infra_importance
            
        # Renewable energy skills
        if sum(region.metrics.renewable_energy_potential.values()) > 0:
            energy_importance = min(1.0, sum(region.metrics.renewable_energy_potential.values()) / (10000000000 * len(region.metrics.renewable_energy_potential)))
            needed_skills["renewable_energy"] = energy_importance
            
        # Conservation/restoration skills
        if region.metrics.ecological_health_score < 7.0:
            eco_importance = 1.0 - (region.metrics.ecological_health_score / 10.0)
            needed_skills["conservation"] = eco_importance
            
        # Healthcare skills
        healthcare_importance = 0.8  # Always needed
        needed_skills["healthcare"] = healthcare_importance
        
        # Education skills
        education_importance = 0.8  # Always needed
        needed_skills["education"] = education_importance
        
        # Disaster preparedness skills
        if any(risk > 0.5 for risk in region.metrics.natural_disaster_risk.values()):
            disaster_importance = max(region.metrics.natural_disaster_risk.values())
            needed_skills["disaster_preparedness"] = disaster_importance
            
        return needed_skills
    
    def _generate_role_recommendations(self, profile: HumanSkillProfile, region: USRegion) -> List[str]:
        """
        Generate role recommendations based on profile and region.
        
        Args:
            profile: Human skill profile
            region: Region for potential relocation
            
        Returns:
            List of recommended roles
        """
        recommendations = []
        
        # Match career experience to regional needs
        region_needs = self._get_region_needed_skills(region)
        
        # Agriculture roles
        if "agriculture" in region_needs and any(ag_term in job.lower() for job in profile.career_experience for ag_term in ["farm", "garden", "crop", "agriculture", "food", "harvest"]):
            recommendations.append("Sustainable Agriculture Specialist")
            
        # Water management roles
        if "water_management" in region_needs and any(water_term in job.lower() for job in profile.career_experience for water_term in ["water", "hydrology", "irrigation", "plumbing"]):
            recommendations.append("Water Systems Coordinator")
            
        # Infrastructure roles
        if "infrastructure" in region_needs and any(infra_term in job.lower() for job in profile.career_experience for infra_term in ["construction", "builder", "engineer", "architect", "electrician", "carpenter"]):
            recommendations.append("Sustainable Infrastructure Developer")
            
        # Energy roles
        if "renewable_energy" in region_needs and any(energy_term in job.lower() for job in profile.career_experience for energy_term in ["energy", "solar", "wind", "electric", "power"]):
            recommendations.append("Renewable Energy Specialist")
            
        # Conservation roles
        if "conservation" in region_needs and any(eco_term in job.lower() for job in profile.career_experience for eco_term in ["ecology", "conservation", "environment", "biology", "forest"]):
            recommendations.append("Ecological Restoration Coordinator")
            
        # Healthcare roles
        if "healthcare" in region_needs and any(health_term in job.lower() for job in profile.career_experience for health_term in ["health", "medical", "doctor", "nurse", "therapist", "care"]):
            recommendations.append("Community Health Practitioner")
            
        # Education roles
        if "education" in region_needs and any(edu_term in job.lower() for job in profile.career_experience for edu_term in ["teach", "education", "school", "instructor", "professor", "training"]):
            recommendations.append("Educational Program Developer")
            
        # Disaster preparedness roles
        if "disaster_preparedness" in region_needs and any(disaster_term in job.lower() for job in profile.career_experience for disaster_term in ["emergency", "disaster", "safety", "rescue", "response"]):
            recommendations.append("Disaster Preparedness Coordinator")
            
        # Community roles
        if any(community_term in profile.interests for community_term in ["community", "governance", "organizing", "social", "leadership"]):
            recommendations.append("Community Integration Facilitator")
            
        # Add preferred roles based on profile
        for role in profile.community_role_preferences:
            if role not in recommendations:
                recommendations.append(role)
                
        return recommendations[:3]  # Limit to top 3 recommendations
    
    def _generate_compatibility_rationale(self, 
                                       profile: HumanSkillProfile, 
                                       region: USRegion,
                                       climate_match: float,
                                       skill_match: float,
                                       needs_match: float) -> str:
        """
        Generate a rationale for the compatibility assessment.
        
        Args:
            profile: Human skill profile
            region: Region being assessed
            climate_match: Climate match score
            skill_match: Skill match score
            needs_match: Needs match score
            
        Returns:
            Compatibility rationale
        """
        rationale_parts = []
        
        # Climate rationale
        if climate_match > 0.8:
            rationale_parts.append(f"The {region.metrics.climate_zone.name.replace('_', ' ').lower()} climate of {region.name} aligns well with your preferences.")
        elif climate_match > 0.4:
            rationale_parts.append(f"The {region.metrics.climate_zone.name.replace('_', ' ').lower()} climate of {region.name} is somewhat similar to your preferred climates.")
        else:
            rationale_parts.append(f"The climate of {region.name} differs from your stated preferences, which may require adjustment.")
            
        # Skills rationale
        if skill_match > 0.7:
            rationale_parts.append(f"Your skills in {', '.join(list(profile.skill_categories.keys())[:2])} are highly valuable in this region.")
        elif skill_match > 0.4:
            rationale_parts.append(f"Some of your skills would be useful in this region, though additional training might be beneficial.")
        else:
            rationale_parts.append("Your current skill set may need significant expansion to meet the region's needs.")
            
        # Needs rationale
        if needs_match > 0.8:
            rationale_parts.append("The region can likely meet your personal and family needs effectively.")
        elif needs_match > 0.4:
            rationale_parts.append("The region may meet most of your needs, with some limitations.")
        else:
            rationale_parts.append("The region has significant limitations in meeting your specific needs.")
            
        # Add regional highlights
        if region.metrics.water_availability.value >= WaterAvailability.SUFFICIENT.value:
            rationale_parts.append(f"Water availability is {region.metrics.water_availability.name.lower()}, which is a critical resource advantage.")
            
        if region.metrics.climate_resilience_score > 6.0:
            rationale_parts.append(f"This region has above-average climate resilience ({region.metrics.climate_resilience_score}/10).")
            
        if region.metrics.agricultural_capacity_people > region.metrics.optimal_population:
            rationale_parts.append("The region has excellent agricultural potential, capable of producing surplus food.")
            
        return " ".join(rationale_parts)
    
    def _generate_preparation_suggestions(self, profile: HumanSkillProfile, region: USRegion) -> List[str]:
        """
        Generate suggestions for preparation before relocation.
        
        Args:
            profile: Human skill profile
            region: Region for potential relocation
            
        Returns:
            List of preparation suggestions
        """
        suggestions = []
        
        # Skill development suggestions
        region_needs = self._get_region_needed_skills(region)
        missing_skills = [skill for skill, importance in region_needs.items() 
                        if importance > 0.5 and (skill not in profile.skill_categories or profile.skill_categories.get(skill, 0) < 0.5)]
        
        if missing_skills:
            skill_suggestion = f"Develop skills in {', '.join(missing_skills[:2])}"
            if len(missing_skills) > 2:
                skill_suggestion += f", and {missing_skills[2]}"
            suggestions.append(skill_suggestion)
            
        # Climate adaptation suggestions
        if region.metrics.climate_zone not in profile.climate_preferences:
            suggestions.append(f"Research and prepare for adapting to {region.metrics.climate_zone.name.replace('_', ' ').lower()} climate conditions")
            
        # Healthcare suggestions
        if profile.requires_specialized_healthcare and region.metrics.infrastructure_status.value < InfrastructureStatus.MODERN.value:
            suggestions.append("Research healthcare options and establish connections with medical providers before relocating")
            
        # Disaster preparedness
        high_risks = [disaster for disaster, risk in region.metrics.natural_disaster_risk.items() if risk > 0.6]
        if high_risks:
            suggestions.append(f"Develop preparedness plans for {', '.join(high_risks)} risks in this region")
            
        # Water management
        if region.metrics.water_availability.value <= WaterAvailability.STRESSED.value:
            suggestions.append("Learn water conservation techniques and rainwater harvesting appropriate for this region")
            
        # Energy systems
        top_energy = max(region.metrics.renewable_energy_potential.items(), key=lambda x: x[1], default=(None, 0))
        if top_energy[0]:
            suggestions.append(f"Familiarize yourself with {top_energy[0]} energy systems, which have significant potential in this region")
            
        # Community integration
        if "community" in region.name.lower() or region.metrics.population_density.value <= PopulationDensity.RURAL_DEVELOPED.value:
            suggestions.append("Connect with existing communities in the region to understand local customs and practices")
            
        return suggestions
    
    def recommend_relocation_matches(self, 
                                  human_profile: HumanSkillProfile,
                                  match_count: int = 3) -> List[Dict[str, Any]]:
        """
        Recommend bioregions for relocation based on human profile.
        
        Args:
            human_profile: Human skill profile
            match_count: Number of matches to return
            
        Returns:
            List of recommended matches
        """
        matches = []
        
        # Score all regions
        for region in self.us_regions.values():
            compatibility = self.get_region_compatibility_score(human_profile, region.region_id)
            
            if compatibility["success"]:
                matches.append(compatibility)
                
        # Sort by compatibility score
        matches.sort(key=lambda x: x["compatibility_score"], reverse=True)
        
        # Return top matches
        return matches[:match_count]


# ====================================================================
# 2. SUSTAINABLE COMMUNITY DESIGN
# ====================================================================

class CommunityScale(Enum):
    """Scale of sustainable community."""
    NEIGHBORHOOD = auto()   # 50-150 people
    VILLAGE = auto()        # 150-500 people
    TOWN = auto()           # 500-2000 people
    SMALL_CITY = auto()     # 2000-10000 people
    REGIONAL_HUB = auto()   # 10000+ people


class CommunityFocus(Enum):
    """Primary focus of community."""
    AGRICULTURAL = auto()   # Farming/food production
    ECOLOGICAL = auto()     # Ecosystem restoration/preservation
    EDUCATIONAL = auto()    # Knowledge/learning center
    MANUFACTURING = auto()  # Local production/maker
    MIXED_USE = auto()      # Balanced approach
    ENERGY = auto()         # Renewable energy production
    CULTURAL = auto()       # Arts and culture center
    TECHNOLOGICAL = auto()  # Tech development/innovation


class GovernanceModel(Enum):
    """Governance models for communities."""
    CONSENSUS = auto()      # Consensus-based decision making
    SOCIOCRACY = auto()     # Sociocratic circles
    REPRESENTATIVE = auto() # Elected representatives
    DIRECT_DEMOCRACY = auto() # Direct voting
    COUNCIL = auto()        # Council of stakeholders
    STEWARDSHIP = auto()    # Stewardship-based governance


@dataclass
class BuildingSystem:
    """Sustainable building system."""
    system_id: str
    name: str
    description: str
    primary_materials: List[str]
    skill_level_required: int  # 1-10 scale
    durability_years: int
    insulation_value: float  # R-value
    embodied_carbon: float  # kg CO2e/m²
    cost_per_sqm: float
    region_suitability: List[str]  # Region IDs
    climate_suitability: List[ClimateZone]
    advantages: List[str]
    disadvantages: List[str]
    construction_guide_url: Optional[str] = None
    images_urls: List[str] = field(default_factory=list)


@dataclass
class EnergySystem:
    """Sustainable energy system."""
    system_id: str
    name: str
    description: str
    energy_type: str  # solar, wind, hydro, biomass, geothermal
    capacity_range_kw: Tuple[float, float]
    storage_included: bool
    storage_capacity_kwh: float
    typical_output_kwh_per_year: float
    lifespan_years: int
    maintenance_level: int  # 1-10 scale
    upfront_cost_per_kw: float
    region_suitability: List[str]  # Region IDs
    climate_suitability: List[ClimateZone]
    advantages: List[str]
    disadvantages: List[str]
    installation_guide_url: Optional[str] = None
    images_urls: List[str] = field(default_factory=list)


@dataclass
class WaterSystem:
    """Sustainable water system."""
    system_id: str
    name: str
    description: str
    water_source: str  # rain, ground, surface, municipal
    collection_capacity_liters: float
    treatment_method: str
    treatment_capacity_liters_per_day: float
    energy_required_kwh_per_day: float
    lifespan_years: int
    maintenance_level: int  # 1-10 scale
    upfront_cost: float
    region_suitability: List[str]  # Region IDs
    climate_suitability: List[ClimateZone]
    advantages: List[str]
    disadvantages: List[str]
    installation_guide_url: Optional[str] = None
    images_urls: List[str] = field(default_factory=list)


@dataclass
class FoodSystem:
    """Sustainable food production system."""
    system_id: str
    name: str
    description: str
    production_type: str  # garden, farm, aquaponics, etc.
    area_required_sqm: float
    water_required_liters_per_day: float
    typical_yield_calories_per_sqm: float
    typical_yield_kg_per_sqm: float
    personnel_required_per_hectare: float
    energy_required_kwh_per_day: float
    setup_time_months: int
    region_suitability: List[str]  # Region IDs
    climate_suitability: List[ClimateZone]
    advantages: List[str]
    disadvantages: List[str]
    implementation_guide_url: Optional[str] = None
    images_urls: List[str] = field(default_factory=list)


@dataclass
class Community:
    """Sustainable community design."""
    community_id: str
    name: str
    region_id: str
    scale: CommunityScale
    focus: CommunityFocus
    governance: GovernanceModel
    description: str
    target_population: int
    land_area_acres: float
    bioregion_features: List[str]
    building_systems: List[str]  # Building system IDs
    energy_systems: List[str]  # Energy system IDs
    water_systems: List[str]  # Water system IDs
    food_systems: List[str]  # Food system IDs
    skill_requirements: Dict[str, int]  # Skill category -> count needed
    development_phases: List[Dict[str, Any]]
    special_features: List[str]
    estimated_implementation_cost: float
    estimated_annual_operating_cost: float
    mutual_aid_connections: List[str]  # Other community IDs
    metadata: Dict[str, Any] = field(default_factory=dict)


class SustainableCommunityDesigner:
    """
    Designs sustainable communities based on bioregion characteristics.
    """
    
    def __init__(self, 
                bioregional_mapper: BioregionalMapper,
                data_path: str = "community_data"):
        """
        Initialize sustainable community designer.
        
        Args:
            bioregional_mapper: Bioregional mapper
            data_path: Path for storing community data
        """
        self.mapper = bioregional_mapper
        self.data_path = data_path
        
        # Ensure paths exist
        os.makedirs(data_path, exist_ok=True)
        os.makedirs(os.path.join(data_path, "communities"), exist_ok=True)
        os.makedirs(os.path.join(data_path, "building_systems"), exist_ok=True)
        os.makedirs(os.path.join(data_path, "energy_systems"), exist_ok=True)
        os.makedirs(os.path.join(data_path, "water_systems"), exist_ok=True)
        os.makedirs(os.path.join(data_path, "food_systems"), exist_ok=True)
        
        # Load systems and communities
        self.building_systems: Dict[str, BuildingSystem] = {}
        self.energy_systems: Dict[str, EnergySystem] = {}
        self.water_systems: Dict[str, WaterSystem] = {}
        self.food_systems: Dict[str, FoodSystem] = {}
        self.communities: Dict[str, Community] = {}
        
        self._load_systems()
        self._load_communities()
        
        # Initialize with default systems if none exist
        if not self.building_systems:
            self._initialize_default_building_systems()
        if not self.energy_systems:
            self._initialize_default_energy_systems()
        if not self.water_systems:
            self._initialize_default_water_systems()
        if not self.food_systems:
            self._initialize_default_food_systems()
            
        # Initialize default community templates
        if not self.communities:
            self._initialize_default_communities()
    
    def _load_systems(self) -> None:
        """Load sustainable systems from disk."""
        try:
            # Load building systems
            building_dir = os.path.join(self.data_path, "building_systems")
            for filename in os.listdir(building_dir):
                if filename.endswith(".json"):
                    file_path = os.path.join(building_dir, filename)
                    try:
                        with open(file_path, "r") as f:
                            data = json.load(f)
                            system = BuildingSystem(
                                system_id=data.get("system_id", filename.replace(".json", "")),
                                name=data.get("name", "Unknown Building System"),
                                description=data.get("description", ""),
                                primary_materials=data.get("primary_materials", []),
                                skill_level_required=data.get("skill_level_required", 5),
                                durability_years=data.get("durability_years", 50),
                                insulation_value=data.get("insulation_value", 0.0),
                                embodied_carbon=data.get("embodied_carbon", 0.0),
                                cost_per_sqm=data.get("cost_per_sqm", 0.0),
                                region_suitability=data.get("region_suitability", []),
                                climate_suitability=[ClimateZone[c] for c in data.get("climate_suitability", [])],
                                advantages=data.get("advantages", []),
                                disadvantages=data.get("disadvantages", []),
                                construction_guide_url=data.get("construction_guide_url"),
                                images_urls=data.get("images_urls", [])
                            )
                            self.building_systems[system.system_id] = system
                    except Exception as e:
                        logger.error(f"Error loading building system from {file_path}: {e}")
                        
            # Load energy systems
            energy_dir = os.path.join(self.data_path, "energy_systems")
            for filename in os.listdir(energy_dir):
                if filename.endswith(".json"):
                    file_path = os.path.join(energy_dir, filename)
                    try:
                        with open(file_path, "r") as f:
                            data = json.load(f)
                            system = EnergySystem(
                                system_id=data.get("system_id", filename.replace(".json", "")),
                                name=data.get("name", "Unknown Energy System"),
                                description=data.get("description", ""),
                                energy_type=data.get("energy_type", ""),
                                capacity_range_kw=tuple(data.get("capacity_range_kw", [0, 0])),
                                storage_included=data.get("storage_included", False),
                                storage_capacity_kwh=data.get("storage_capacity_kwh", 0.0),
                                typical_output_kwh_per_year=data.get("typical_output_kwh_per_year", 0.0),
                                lifespan_years=data.get("lifespan_years", 20),
                                maintenance_level=data.get("maintenance_level", 5),
                                upfront_cost_per_kw=data.get("upfront_cost_per_kw", 0.0),
                                region_suitability=data.get("region_suitability", []),
                                climate_suitability=[ClimateZone[c] for c in data.get("climate_suitability", [])],
                                advantages=data.get("advantages", []),
                                disadvantages=data.get("disadvantages", []),
                                installation_guide_url=data.get("installation_guide_url"),
                                images_urls=data.get("images_urls", [])
                            )
                            self.energy_systems[system.system_id] = system
                    except Exception as e:
                        logger.error(f"Error loading energy system from {file_path}: {e}")
                        
            # Load water systems
            water_dir = os.path.join(self.data_path, "water_systems")
            for filename in os.listdir(water_dir):
                if filename.endswith(".json"):
                    file_path = os.path.join(water_dir, filename)
                    try:
                        with open(file_path, "r") as f:
                            data = json.load(f)
                            system = WaterSystem(
                                system_id=data.get("system_id", filename.replace(".json", "")),
                                name=data.get("name", "Unknown Water System"),
                                description=data.get("description", ""),
                                water_source=data.get("water_source", ""),
                                collection_capacity_liters=data.get("collection_capacity_liters", 0.0),
                                treatment_method=data.get("treatment_method", ""),
                                treatment_capacity_liters_per_day=data.get("treatment_capacity_liters_per_day", 0.0),
                                energy_required_kwh_per_day=data.get("energy_required_kwh_per_day", 0.0),
                                lifespan_years=data.get("lifespan_years", 20),
                                maintenance_level=data.get("maintenance_level", 5),
                                upfront_cost=data.get("upfront_cost", 0.0),
                                region_suitability=data.get("region_suitability", []),
                                climate_suitability=[ClimateZone[c] for c in data.get("climate_suitability", [])],
                                advantages=data.get("advantages", []),
                                disadvantages=data.get("disadvantages", []),
                                installation_guide_url=data.get("installation_guide_url"),
                                images_urls=data.get("images_urls", [])
                            )
                            self.water_systems[system.system_id] = system
                    except Exception as e:
                        logger.error(f"Error loading water system from {file_path}: {e}")
                        
            # Load food systems
            food_dir = os.path.join(self.data_path, "food_systems")
            for filename in os.listdir(food_dir):
                if filename.endswith(".json"):
                    file_path = os.path.join(food_dir, filename)
                    try:
                        with open(file_path, "r") as f:
                            data = json.load(f)
                            system = FoodSystem(
                                system_id=data.get("system_id", filename.replace(".json", "")),
                                name=data.get("name", "Unknown Food System"),
                                description=data.get("description", ""),
                                production_type=data.get("production_type", ""),
                                area_required_sqm=data.get("area_required_sqm", 0.0),
                                water_required_liters_per_day=data.get("water_required_liters_per_day", 0.0),
                                typical_yield_calories_per_sqm=data.get("typical_yield_calories_per_sqm", 0.0),
                                typical_yield_kg_per_sqm=data.get("typical_yield_kg_per_sqm", 0.0),
                                personnel_required_per_hectare=data.get("personnel_required_per_hectare", 0.0),
                                energy_required_kwh_per_day=data.get("energy_required_kwh_per_day", 0.0),
                                setup_time_months=data.get("setup_time_months", 6),
                                region_suitability=data.get("region_suitability", []),
                                climate_suitability=[ClimateZone[c] for c in data.get("climate_suitability", [])],
                                advantages=data.get("advantages", []),
                                disadvantages=data.get("disadvantages", []),
                                implementation_guide_url=data.get("implementation_guide_url"),
                                images_urls=data.get("images_urls", [])
                            )
                            self.food_systems[system.system_id] = system
                    except Exception as e:
                        logger.error(f"Error loading food system from {file_path}: {e}")
                        
            logger.info(f"Loaded {len(self.building_systems)} building systems, {len(self.energy_systems)} energy systems, {len(self.water_systems)} water systems, and {len(self.food_systems)} food systems")
            
        except Exception as e:
            logger.error(f"Error loading systems: {e}")
    
    def _load_communities(self) -> None:
        """Load communities from disk."""
        try:
            # Load communities
            communities_dir = os.path.join(self.data_path, "communities")
            for filename in os.listdir(communities_dir):
                if filename.endswith(".json"):
                    file_path = os.path.join(communities_dir, filename)
                    try:
                        with open(file_path, "r") as f:
                            data = json.load(f)
                            community = Community(
                                community_id=data.get("community_id", filename.replace(".json", "")),
                                name=data.get("name", "Unknown Community"),
                                region_id=data.get("region_id", ""),
                                scale=CommunityScale[data.get("scale", "VILLAGE")],
                                focus=CommunityFocus[data.get("focus", "MIXED_USE")],
                                governance=GovernanceModel[data.get("governance", "CONSENSUS")],
                                description=data.get("description", ""),
                                target_population=data.get("target_population", 0),
                                land_area_acres=data.get("land_area_acres", 0.0),
                                bioregion_features=data.get("bioregion_features", []),
                                building_systems=data.get("building_systems", []),
                                energy_systems=data.get("energy_systems", []),
                                water_systems=data.get("water_systems", []),
                                food_systems=data.get("food_systems", []),
                                skill_requirements=data.get("skill_requirements", {}),
                                development_phases=data.get("development_phases", []),
                                special_features=data.get("special_features", []),
                                estimated_implementation_cost=data.get("estimated_implementation_cost", 0.0),
                                estimated_annual_operating_cost=data.get("estimated_annual_operating_cost", 0.0),
                                mutual_aid_connections=data.get("mutual_aid_connections", []),
                                metadata=data.get("metadata", {})
                            )
                            self.communities[community.community_id] = community
                    except Exception as e:
                        logger.error(f"Error loading community from {file_path}: {e}")
                        
            logger.info(f"Loaded {len(self.communities)} communities")
            
        except Exception as e:
            logger.error(f"Error loading communities: {e}")
    
    def _save_building_system(self, system: BuildingSystem) -> None:
        """Save building system to disk."""
        try:
            file_path = os.path.join(self.data_path, "building_systems", f"{system.system_id}.json")
            
            # Prepare system data
            system_data = {
                "system_id": system.system_id,
                "name": system.name,
                "description": system.description,
                "primary_materials": system.primary_materials,
                "skill_level_required": system.skill_level_required,
                "durability_years": system.durability_years,
                "insulation_value": system.insulation_value,
                "embodied_carbon": system.embodied_carbon,
                "cost_per_sqm": system.cost_per_sqm,
                "region_suitability": system.region_suitability,
                "climate_suitability": [c.name for c in system.climate_suitability],
                "advantages": system.advantages,
                "disadvantages": system.disadvantages,
                "construction_guide_url": system.construction_guide_url,
                "images_urls": system.images_urls
            }
            
            with open(file_path, "w") as f:
                json.dump(system_data, f, indent=2)
                
        except Exception as e:
            logger.error(f"Error saving building system: {e}")
    
    def _save_energy_system(self, system: EnergySystem) -> None:
        """Save energy system to disk."""
        try:
            file_path = os.path.join(self.data_path, "energy_systems", f"{system.system_id}.json")
            
            # Prepare system data
            system_data = {
                "system_id": system.system_id,
                "name": system.name,
                "description": system.description,
                "energy_type": system.energy_type,
                "capacity_range_kw": system.capacity_range_kw,
                "storage_included": system.storage_included,
                "storage_capacity_kwh": system.storage_capacity_kwh,
                "typical_output_kwh_per_year": system.typical_output_kwh_per_year,
                "lifespan_years": system.lifespan_years,
                "maintenance_level": system.maintenance_level,
                "upfront_cost_per_kw": system.upfront_cost_per_kw,
                "region_suitability": system.region_suitability,
                "climate_suitability": [c.name for c in system.climate_suitability],
                "advantages": system.advantages,
                "disadvantages": system.disadvantages,
                "installation_guide_url": system.installation_guide_url,
                "images_urls": system.images_urls
            }
            
            with open(file_path, "w") as f:
                json.dump(system_data, f, indent=2)
                
        except Exception as e:
            logger.error(f"Error saving energy system: {e}")
    
    def _save_water_system(self, system: WaterSystem) -> None:
        """Save water system to disk."""
        try:
            file_path = os.path.join(self.data_path, "water_systems", f"{system.system_id}.json")
            
            # Prepare system data
            system_data = {
                "system_id": system.system_id,
                "name": system.name,
                "description": system.description,
                "water_source": system.water_source,
                "collection_capacity_liters": system.collection_capacity_liters,
                "treatment_method": system.treatment_method,
                "treatment_capacity_liters_per_day": system.treatment_capacity_liters_per_day,
                "energy_required_kwh_per_day": system.energy_required_kwh_per_day,
                "lifespan_years": system.lifespan_years,
                "maintenance_level": system.maintenance_level,
                "upfront_cost": system.upfront_cost,
                "region_suitability": system.region_suitability,
                "climate_suitability": [c.name for c in system.climate_suitability],
                "advantages": system.advantages,
                "disadvantages": system.disadvantages,
                "installation_guide_url": system.installation_guide_url,
                "images_urls": system.images_urls
            }
            
            with open(file_path, "w") as f:
                json.dump(system_data, f, indent=2)
                
        except Exception as e:
            logger.error(f"Error saving water system: {e}")
    
    def _save_food_system(self, system: FoodSystem) -> None:
        """Save food system to disk."""
        try:
            file_path = os.path.join(self.data_path, "food_systems", f"{system.system_id}.json")
            
            # Prepare system data
            system_data = {
                "system_id": system.system_id,
                "name": system.name,
                "description": system.description,
                "production_type": system.production_type,
                "area_required_sqm": system.area_required_sqm,
                "water_required_liters_per_day": system.water_required_liters_per_day,
                "typical_yield_calories_per_sqm": system.typical_yield_calories_per_sqm,
                "typical_yield_kg_per_sqm": system.typical_yield_kg_per_sqm,
                "personnel_required_per_hectare": system.personnel_required_per_hectare,
                "energy_required_kwh_per_day": system.energy_required_kwh_per_day,
                "setup_time_months": system.setup_time_months,
                "region_suitability": system.region_suitability,
                "climate_suitability": [c.name for c in system.climate_suitability],
                "advantages": system.advantages,
                "disadvantages": system.disadvantages,
                "implementation_guide_url": system.implementation_guide_url,
                "images_urls": system.images_urls
            }
            
            with open(file_path, "w") as f:
                json.dump(system_data, f, indent=2)
                
        except Exception as e:
            logger.error(f"Error saving food system: {e}")
    
    def _save_community(self, community: Community) -> None:
        """Save community to disk."""
        try:
            file_path = os.path.join(self.data_path, "communities", f"{community.community_id}.json")
            
            # Prepare community data
            community_data = {
                "community_id": community.community_id,
                "name": community.name,
                "region_id": community.region_id,
                "scale": community.scale.name,
                "focus": community.focus.name,
                "governance": community.governance.name,
                "description": community.description,
                "target_population": community.target_population,
                "land_area_acres": community.land_area_acres,
                "bioregion_features": community.bioregion_features,
                "building_systems": community.building_systems,
                "energy_systems": community.energy_systems,
                "water_systems": community.water_systems,
                "food_systems": community.food_systems,
                "skill_requirements": community.skill_requirements,
                "development_phases": community.development_phases,
                "special_features": community.special_features,
                "estimated_implementation_cost": community.estimated_implementation_cost,
                "estimated_annual_operating_cost": community.estimated_annual_operating_cost,
                "mutual_aid_connections": community.mutual_aid_connections,
                "metadata": community.metadata
            }
            
            with open(file_path, "w") as f:
                json.dump(community_data, f, indent=2)
                
        except Exception as e:
            logger.error(f"Error saving community: {e}")
    
    def _initialize_default_building_systems(self) -> None:
        """Initialize default building systems."""
        default_systems = [
            # Rammed Earth
            BuildingSystem(
                system_id="rammed_earth",
                name="Rammed Earth",
                description="Compacted earth construction using local soil mixed with stabilizers. Excellent thermal mass and durability with very low embodied carbon.",
                primary_materials=["Local soil", "Clay", "Sand", "Small amount of cement or lime"],
                skill_level_required=7,
                durability_years=100,
                insulation_value=0.7,  # R-value per inch
                embodied_carbon=20.0,  # kg CO2e/m²
                cost_per_sqm=350.0,
                region_suitability=["southwest", "northern_plains", "great_lakes"],
                climate_suitability=[
                    ClimateZone.DESERT_HOT, ClimateZone.DESERT_COLD, ClimateZone.STEPPE_HOT, 
                    ClimateZone.STEPPE_COLD, ClimateZone.MEDITERRANEAN
                ],
                advantages=[
                    "Extremely low embodied carbon",
                    "Excellent thermal mass",
                    "Fire resistant",
                    "Creates a quiet interior environment",
                    "Low maintenance",
                    "Can use local materials"
                ],
                disadvantages=[
                    "Labor intensive",
                    "Requires skilled builders",
                    "Not suitable for all soil types",
                    "Poor insulation value alone (needs additional insulation in cold climates)",
                    "Heavy - requires good foundation"
                ]
            ),
            
            # Timber Frame with Straw Bale
            BuildingSystem(
                system_id="timber_strawbale",
                name="Timber Frame with Straw Bale Infill",
                description="Timber frame structure with straw bale walls finished with earth plaster. Combines excellent insulation with renewable materials.",
                primary_materials=["Local timber", "Straw bales", "Clay plaster", "Lime plaster"],
                skill_level_required=6,
                durability_years=75,
                insulation_value=3.5,  # R-value per inch
                embodied_carbon=30.0,  # kg CO2e/m²
                cost_per_sqm=400.0,
                region_suitability=["great_lakes", "pacific_northwest", "northern_plains", "ozarks"],
                climate_suitability=[
                    ClimateZone.CONTINENTAL_COOL, ClimateZone.CONTINENTAL_WARM, ClimateZone.OCEANIC,
                    ClimateZone.HUMID_SUBTROPICAL
                ],
                advantages=[
                    "Excellent insulation (R-30 to R-50 walls)",
                    "Uses agricultural waste product",
                    "Good sound insulation",
                    "Non-toxic building materials",
                    "Carbon sequestering",
                    "Can use local/regional materials"
                ],
                disadvantages=[
                    "Requires careful moisture management",
                    "Not suitable for very humid climates without proper detailing",
                    "Requires specific construction knowledge",
                    "Thicker walls than conventional construction",
                    "Needs protection during construction phase"
                ]
            ),
            
            # Cob Construction
            BuildingSystem(
                system_id="cob",
                name="Cob Construction",
                description="Hand-formed earth building technique using clay-rich soil, sand, and straw. Sculptural, beautiful, and very low embodied energy.",
                primary_materials=["Local soil", "Clay", "Sand", "Straw"],
                skill_level_required=5,
                durability_years=100,
                insulation_value=0.5,  # R-value per inch
                embodied_carbon=10.0,  # kg CO2e/m²
                cost_per_sqm=200.0,
                region_suitability=["pacific_northwest", "new_england", "ozarks"],
                climate_suitability=[
                    ClimateZone.MEDITERRANEAN, ClimateZone.OCEANIC, ClimateZone.HUMID_SUBTROPICAL
                ],
                advantages=[
                    "Extremely low embodied carbon",
                    "Can be built by unskilled people with training",
                    "Thermal mass regulates temperatures",
                    "Non-toxic, completely natural",
                    "Highly sculptural - allows organic forms",
                    "Very low cost with local materials"
                ],
                disadvantages=[
                    "Labor intensive",
                    "Poor insulation - needs additional insulation in cold climates",
                    "Requires good roof overhangs for weather protection",
                    "Long drying time during construction",
                    "Limited to 1-2 stories typically"
                ]
            ),
            
            # Modified Earthship
            BuildingSystem(
                system_id="modified_earthship",
                name="Modified Earthship Design",
                description="Passive solar earth-sheltered design adapted from earthship principles. Incorporates thermal mass, passive ventilation, and optimal solar orientation.",
                primary_materials=["Rammed earth tires", "Earth", "Recycled materials", "Timber"],
                skill_level_required=7,
                durability_years=100,
                insulation_value=2.5,  # R-value per inch (average for system)
                embodied_carbon=25.0,  # kg CO2e/m²
                cost_per_sqm=500.0,
                region_suitability=["southwest", "northern_plains", "ozarks"],
                climate_suitability=[
                    ClimateZone.DESERT_HOT, ClimateZone.DESERT_COLD, ClimateZone.STEPPE_HOT, 
                    ClimateZone.STEPPE_COLD, ClimateZone.CONTINENTAL_WARM
                ],
                advantages=[
                    "Energy efficiency through passive solar design",
                    "Thermal mass regulates temperatures",
                    "Earth-sheltered for weather protection",
                    "Can incorporate greywater systems easily",
                    "Can use recycled materials",
                    "Resilient in extreme climates"
                ],
                disadvantages=[
                    "Complex design requiring careful planning",
                    "Labor intensive construction",
                    "Requires specific site orientation",
                    "High skill level for key systems",
                    "Some materials may need to be imported"
                ]
            ),
            
            # Advanced Wood Framing
            BuildingSystem(
                system_id="advanced_framing",
                name="Advanced Wood Framing",
                description="Optimized wood framing techniques that reduce lumber use while allowing for high insulation values. Combines familiar techniques with improved efficiency.",
                primary_materials=["Dimensional lumber", "Engineered wood", "Cellulose insulation"],
                skill_level_required=5,
                durability_years=60,
                insulation_value=3.7,  # R-value per inch with continuous insulation
                embodied_carbon=70.0,  # kg CO2e/m²
                cost_per_sqm=450.0,
                region_suitability=["pacific_northwest", "great_lakes", "new_england", "ozarks"],
                climate_suitability=[
                    ClimateZone.CONTINENTAL_HOT, ClimateZone.CONTINENTAL_WARM, ClimateZone.CONTINENTAL_COOL,
                    ClimateZone.OCEANIC, ClimateZone.HUMID_SUBTROPICAL
                ],
                advantages=[
                    "Very high efficiency (300-400% for heating)",
                    "Both heating and cooling in one system",
                    "Long lifespan with minimal maintenance",
                    "No combustion or carbon emissions on-site",
                    "Stable performance in extreme temperatures",
                    "Lower operating costs than conventional HVAC"
                ],
                disadvantages=[
                    "High initial installation cost",
                    "Requires suitable ground conditions",
                    "Installation disrupts landscape temporarily",
                    "Requires electricity to operate pumps",
                    "May not be cost-effective for small buildings"
                ]
            )
        ]
        
        # Add systems
        for system in default_systems:
            self.energy_systems[system.system_id] = system
            self._save_energy_system(system)
            
        logger.info(f"Initialized {len(default_systems)} default energy systems")
    
    def _initialize_default_water_systems(self) -> None:
        """Initialize default water systems."""
        default_systems = [
            # Rainwater Harvesting
            WaterSystem(
                system_id="rainwater_harvest",
                name="Comprehensive Rainwater Harvesting System",
                description="Collection and storage of rainwater from roofs and other surfaces for various uses from irrigation to potable water.",
                water_source="rain",
                collection_capacity_liters=50000.0,
                treatment_method="Filtration, UV disinfection",
                treatment_capacity_liters_per_day=1000.0,
                energy_required_kwh_per_day=0.5,
                lifespan_years=30,
                maintenance_level=4,
                upfront_cost=10000.0,
                region_suitability=["pacific_northwest", "new_england", "ozarks", "great_lakes"],
                climate_suitability=[
                    ClimateZone.RAINFOREST, ClimateZone.MONSOON, ClimateZone.OCEANIC,
                    ClimateZone.HUMID_SUBTROPICAL
                ],
                advantages=[
                    "Uses free, clean water source",
                    "Reduces demand on groundwater and municipal supplies",
                    "Simple system with minimal moving parts",
                    "Very low operating costs",
                    "Can be retrofitted to existing buildings",
                    "Scalable from small to large applications"
                ],
                disadvantages=[
                    "Dependent on rainfall patterns",
                    "Requires adequate roof/collection area",
                    "Storage tanks require significant space",
                    "Additional treatment needed for potable use",
                    "May require backup water source in dry periods"
                ]
            ),
            
            # Living Machine Greywater
            WaterSystem(
                system_id="living_machine",
                name="Living Machine Greywater System",
                description="Ecological wastewater treatment using a series of engineered wetlands and biological components to purify greywater for reuse.",
                water_source="greywater",
                collection_capacity_liters=5000.0,
                treatment_method="Biological filtration through constructed wetlands",
                treatment_capacity_liters_per_day=2000.0,
                energy_required_kwh_per_day=0.3,
                lifespan_years=25,
                maintenance_level=5,
                upfront_cost=15000.0,
                region_suitability=["pacific_northwest", "ozarks", "great_lakes", "southwest"],
                climate_suitability=[c for c in ClimateZone if c != ClimateZone.TUNDRA and c != ClimateZone.POLAR_ICE],
                advantages=[
                    "Treats water while creating beautiful landscape features",
                    "Minimal energy requirements",
                    "Creates habitat for beneficial insects and wildlife",
                    "Educational opportunity for ecological processes",
                    "Can handle flow variations well",
                    "Produces reusable water for irrigation"
                ],
                disadvantages=[
                    "Requires significant space",
                    "Performance varies with temperature (slower in cold climates)",
                    "Requires some specialized knowledge for maintenance",
                    "More complex than simple greywater systems",
                    "May require greenhouse protection in very cold climates"
                ]
            ),
            
            # Slow Sand Filtration
            WaterSystem(
                system_id="slow_sand",
                name="Slow Sand Filtration System",
                description="Biological water treatment using sand filtration for pathogen removal. Simple, reliable technology for clean drinking water.",
                water_source="surface or rainwater",
                collection_capacity_liters=10000.0,
                treatment_method="Biological sand filtration",
                treatment_capacity_liters_per_day=500.0,
                energy_required_kwh_per_day=0.0,
                lifespan_years=20,
                maintenance_level=3,
                upfront_cost=5000.0,
                region_suitability=["pacific_northwest", "new_england", "ozarks", "great_lakes", "northern_plains"],
                climate_suitability=[c for c in ClimateZone if c != ClimateZone.POLAR_ICE],
                advantages=[
                    "No electricity required (gravity-powered)",
                    "Simple construction with local materials possible",
                    "Very effective pathogen removal",
                    "Low maintenance",
                    "Low operating costs",
                    "Resilient and reliable technology"
                ],
                disadvantages=[
                    "Relatively slow flow rate",
                    "Requires consistent maintenance schedule",
                    "Large footprint compared to mechanical filters",
                    "Less effective with highly turbid water",
                    "Process takes time to establish initially"
                ]
            ),
            
            # Drip Irrigation System
            WaterSystem(
                system_id="drip_irrigation",
                name="Water-Efficient Drip Irrigation",
                description="Precision water delivery system for agricultural and landscape applications, significantly reducing water use compared to conventional irrigation.",
                water_source="any",
                collection_capacity_liters=5000.0,
                treatment_method="Basic filtration",
                treatment_capacity_liters_per_day=5000.0,
                energy_required_kwh_per_day=0.2,
                lifespan_years=10,
                maintenance_level=4,
                upfront_cost=2000.0,
                region_suitability=["southwest", "northern_plains", "great_lakes", "ozarks"],
                climate_suitability=[
                    ClimateZone.DESERT_HOT, ClimateZone.DESERT_COLD, ClimateZone.STEPPE_HOT, 
                    ClimateZone.STEPPE_COLD, ClimateZone.MEDITERRANEAN, ClimateZone.HUMID_SUBTROPICAL
                ],
                advantages=[
                    "Water use reduction of 30-70% compared to conventional irrigation",
                    "Delivers water directly to plant roots",
                    "Reduces weed growth between plants",
                    "Can be automated with simple timers",
                    "Works with low water pressure",
                    "Can use greywater sources"
                ],
                disadvantages=[
                    "Initial installation cost higher than simple irrigation",
                    "Requires filtering to prevent clogging",
                    "Needs regular inspection for leaks or clogs",
                    "Emitters can be damaged by animals or cultivation",
                    "Surface components degrade in UV sunlight"
                ]
            ),
            
            # Fog Collection System
            WaterSystem(
                system_id="fog_collection",
                name="Fog Water Collection System",
                description="Mesh nets that collect water from fog in suitable coastal or mountainous areas, requiring no energy input.",
                water_source="atmospheric moisture",
                collection_capacity_liters=1000.0,
                treatment_method="Basic filtration",
                treatment_capacity_liters_per_day=200.0,
                energy_required_kwh_per_day=0.0,
                lifespan_years=10,
                maintenance_level=3,
                upfront_cost=3000.0,
                region_suitability=["pacific_northwest", "new_england"],
                climate_suitability=[
                    ClimateZone.OCEANIC, ClimateZone.MEDITERRANEAN, ClimateZone.MOUNTAIN
                ],
                advantages=[
                    "Works in drought conditions where fog is present",
                    "No energy requirements",
                    "Simple, passive technology",
                    "Low maintenance requirements",
                    "Can work in areas without other water sources",
                    "Collects clean water requiring minimal treatment"
                ],
                disadvantages=[
                    "Only viable in specific geographic locations with regular fog",
                    "Yield varies significantly with conditions",
                    "Collection area must be in fog path",
                    "Requires regular cleaning of mesh",
                    "Net collectors may be damaged by strong winds"
                ]
            )
        ]
        
        # Add systems
        for system in default_systems:
            self.water_systems[system.system_id] = system
            self._save_water_system(system)
            
        logger.info(f"Initialized {len(default_systems)} default water systems")
    
    def _initialize_default_food_systems(self) -> None:
        """Initialize default food systems."""
        default_systems = [
            # Intensive Annual Gardens
            FoodSystem(
                system_id="intensive_annual",
                name="Intensive Annual Vegetable Production",
                description="Biointensive growing methods for high yields of annual vegetables in small spaces with minimal inputs.",
                production_type="garden",
                area_required_sqm=400.0,  # 0.1 acre
                water_required_liters_per_day=1000.0,
                typical_yield_calories_per_sqm=700.0,
                typical_yield_kg_per_sqm=5.0,
                personnel_required_per_hectare=5.0,
                energy_required_kwh_per_day=0.5,
                setup_time_months=2,
                region_suitability=["pacific_northwest", "great_lakes", "new_england", "ozarks"],
                climate_suitability=[
                    ClimateZone.OCEANIC, ClimateZone.HUMID_SUBTROPICAL, ClimateZone.CONTINENTAL_WARM,
                    ClimateZone.MEDITERRANEAN
                ],
                advantages=[
                    "High productivity in small spaces",
                    "Quick establishment and yields",
                    "Familiar foods and growing methods",
                    "Low startup costs",
                    "Adaptable to many climates with season extension",
                    "Good entry point for new gardeners"
                ],
                disadvantages=[
                    "Labor intensive",
                    "Requires regular irrigation",
                    "Annual replanting necessary",
                    "Soil needs regular replenishment",
                    "Seasonal production without infrastructure",
                    "Susceptible to pest and disease pressure"
                ]
            ),
            
            # Food Forest
            FoodSystem(
                system_id="food_forest",
                name="Perennial Food Forest System",
                description="Multi-layered perennial polyculture mimicking forest structure while producing diverse foods with minimal intervention once established.",
                production_type="agroforestry",
                area_required_sqm=2000.0,  # 0.5 acre
                water_required_liters_per_day=500.0,
                typical_yield_calories_per_sqm=400.0,
                typical_yield_kg_per_sqm=2.0,
                personnel_required_per_hectare=1.0,
                energy_required_kwh_per_day=0.0,
                setup_time_months=36,
                region_suitability=["pacific_northwest", "great_lakes", "new_england", "ozarks", "southwest"],
                climate_suitability=[c for c in ClimateZone if c != ClimateZone.POLAR_ICE and c != ClimateZone.TUNDRA],
                advantages=[
                    "Low maintenance once established",
                    "Drought resistant after establishment",
                    "Builds soil health over time",
                    "Creates wildlife habitat",
                    "Diverse yields throughout seasons",
                    "Carbon sequestration and microclimate benefits"
                ],
                disadvantages=[
                    "Long establishment period (3-7 years)",
                    "Higher initial investment",
                    "Requires careful planning and design",
                    "Lower caloric yield than annual gardens",
                    "Some specialized knowledge required",
                    "Harvesting can be more time-consuming"
                ]
            ),
            
            # Aquaponics System
            FoodSystem(
                system_id="aquaponics",
                name="Integrated Aquaponics System",
                description="Closed-loop system combining fish cultivation and hydroponics, producing fish protein and vegetables with minimal water use.",
                production_type="aquaponics",
                area_required_sqm=200.0,
                water_required_liters_per_day=50.0,  # Minimal daily topoff
                typical_yield_calories_per_sqm=900.0,
                typical_yield_kg_per_sqm=10.0,
                personnel_required_per_hectare=10.0,
                energy_required_kwh_per_day=5.0,
                setup_time_months=3,
                region_suitability=["pacific_northwest", "great_lakes", "southwest", "ozarks"],
                climate_suitability=[c for c in ClimateZone], # All climates with greenhouse
                advantages=[
                    "Very water efficient (95% less than conventional agriculture)",
                    "Produces both protein and vegetables",
                    "Year-round production possible",
                    "No soil required",
                    "High productivity in small space",
                    "Can be situated on marginal land or indoors"
                ],
                disadvantages=[
                    "Requires reliable electricity",
                    "Technical knowledge required",
                    "Higher startup costs",
                    "System complexity and interdependence",
                    "Energy intensive in cold climates",
                    "Risk of total system failure affecting both components"
                ]
            ),
            
            # Rotational Grazing
            FoodSystem(
                system_id="rotational_grazing",
                name="Regenerative Rotational Grazing",
                description="Managed livestock grazing system that builds soil, sequesters carbon, and produces animal products while improving ecosystem health.",
                production_type="grazing",
                area_required_sqm=40000.0,  # 4 hectares
                water_required_liters_per_day=2000.0,
                typical_yield_calories_per_sqm=50.0,
                typical_yield_kg_per_sqm=0.1,
                personnel_required_per_hectare=0.2,
                energy_required_kwh_per_day=0.1,
                setup_time_months=6,
                region_suitability=["northern_plains", "great_lakes", "ozarks", "new_england"],
                climate_suitability=[
                    ClimateZone.CONTINENTAL_HOT, ClimateZone.CONTINENTAL_WARM, ClimateZone.CONTINENTAL_COOL,
                    ClimateZone.HUMID_SUBTROPICAL, ClimateZone.OCEANIC, ClimateZone.STEPPE_HOT, ClimateZone.STEPPE_COLD
                ],
                advantages=[
                    "Builds soil carbon and fertility",
                    "Converts inedible grass to human food",
                    "Can be combined with silvopasture for tree crops",
                    "Low input costs after establishment",
                    "Improves wildlife habitat and biodiversity",
                    "Works on marginal land unsuitable for crops"
                ],
                disadvantages=[
                    "Requires significant land area",
                    "Lower caloric yield per acre than crops",
                    "Requires knowledge of animal husbandry",
                    "Infrastructure costs for fencing and water",
                    "Daily management required",
                    "Winter feed may be necessary in some climates"
                ]
            ),
            
            # Greenhouse
            FoodSystem(
                system_id="passive_greenhouse",
                name="Passive Solar Greenhouse",
                description="Energy-efficient growing structure using passive solar design for year-round production with minimal supplemental heating.",
                production_type="protected cultivation",
                area_required_sqm=100.0,
                water_required_liters_per_day=300.0,
                typical_yield_calories_per_sqm=1200.0,
                typical_yield_kg_per_sqm=15.0,
                personnel_required_per_hectare=20.0,
                energy_required_kwh_per_day=1.0,
                setup_time_months=4,
                region_suitability=["northern_plains", "great_lakes", "new_england", "pacific_northwest"],
                climate_suitability=[
                    ClimateZone.CONTINENTAL_HOT, ClimateZone.CONTINENTAL_WARM, ClimateZone.CONTINENTAL_COOL,
                    ClimateZone.SUBARCTIC, ClimateZone.OCEANIC
                ],
                advantages=[
                    "Extends growing season in cold climates",
                    "Protects crops from extreme weather",
                    "High productivity per square foot",
                    "Year-round production possible",
                    "Can integrate aquaponics or vertical systems",
                    "Good microclimate for starting seedlings"
                ],
                disadvantages=[
                    "Higher initial cost",
                    "Requires good solar exposure",
                    "More technical knowledge required",
                    "Needs ventilation management",
                    "Can overheat without proper design",
                    "May need supplemental heat in extreme cold"
                ]
            )
        ]
        
        # Add systems
        for system in default_systems:
            self.food_systems[system.system_id] = system
            self._save_food_system(system)
            
        logger.info(f"Initialized {len(default_systems)} default food systems")
    
    def _initialize_default_communities(self) -> None:
        """Initialize default community templates."""
        default_communities = [
            # Pacific Northwest Forest Village
            Community(
                community_id="pnw_forest_village",
                name="Cascadia Forest Village",
                region_id="pacific_northwest",
                scale=CommunityScale.VILLAGE,
                focus=CommunityFocus.ECOLOGICAL,
                governance=GovernanceModel.SOCIOCRACY,
                description="A forest-integrated village designed for the Pacific Northwest, emphasizing timber resources, water abundance, and ecological restoration.",
                target_population=200,
                land_area_acres=120.0,
                bioregion_features=[
                    "Mixed conifer forest integration",
                    "Salmon-bearing stream restoration",
                    "Moderate rainfall harvesting",
                    "Forest understory food forest"
                ],
                building_systems=["timber_strawbale", "cob", "advanced_framing"],
                energy_systems=["solar_battery", "micro_hydro"],
                water_systems=["rainwater_harvest", "living_machine"],
                food_systems=["food_forest", "intensive_annual", "passive_greenhouse"],
                skill_requirements={
                    "ecological_restoration": 5,
                    "forestry": 3,
                    "timber_framing": 2,
                    "renewable_energy": 2,
                    "education": 3,
                    "permaculture": 4,
                    "community_facilitation": 3
                },
                development_phases=[
                    {
                        "name": "Foundation Phase",
                        "duration_months": 6,
                        "focus": "Site assessment, initial infrastructure, temporary housing"
                    },
                    {
                        "name": "Core Establishment",
                        "duration_months": 18,
                        "focus": "Primary buildings, water systems, initial food systems"
                    },
                    {
                        "name": "Growth Phase",
                        "duration_months": 36,
                        "focus": "Additional housing, economic development, forest management plan"
                    },
                    {
                        "name": "Resilience Phase",
                        "duration_months": 60,
                        "focus": "Education center, expanded food production, seed saving program"
                    }
                ],
                special_features=[
                    "Forest education center",
                    "Riparian restoration project",
                    "Timber processing facility",
                    "Salmon habitat enhancement",
                    "Native plant nursery"
                ],
                estimated_implementation_cost=4000000.0,
                estimated_annual_operating_cost=250000.0,
                mutual_aid_connections=[]
            ),
            
            # Great Lakes Agrarian Town
            Community(
                community_id="great_lakes_agrarian",
                name="Great Lakes Agrarian Community",
                region_id="great_lakes",
                scale=CommunityScale.TOWN,
                focus=CommunityFocus.AGRICULTURAL,
                governance=GovernanceModel.COUNCIL,
                description="An agricultural community designed for the Great Lakes region, focusing on regenerative farming practices and value-added food processing.",
                target_population=500,
                land_area_acres=800.0,
                bioregion_features=[
                    "Prime agricultural land restoration",
                    "Four-season cultivation systems",
                    "Freshwater access management",
                    "Forest woodlot integration"
                ],
                building_systems=["advanced_framing", "timber_strawbale", "rammed_earth"],
                energy_systems=["solar_battery", "small_wind", "biogas"],
                water_systems=["rainwater_harvest", "drip_irrigation"],
                food_systems=["rotational_grazing", "intensive_annual", "passive_greenhouse", "food_forest"],
                skill_requirements={
                    "regenerative_agriculture": 8,
                    "animal_husbandry": 4,
                    "food_processing": 5,
                    "carpentry": 4,
                    "community_organizing": 3,
                    "equipment_maintenance": 4,
                    "seed_saving": 3
                },
                development_phases=[
                    {
                        "name": "Land Restoration",
                        "duration_months": 12,
                        "focus": "Soil remediation, water systems, initial pasture establishment"
                    },
                    {
                        "name": "Core Infrastructure",
                        "duration_months": 18,
                        "focus": "Primary housing, barns, processing facilities, energy systems"
                    },
                    {
                        "name": "Agricultural Development",
                        "duration_months": 24,
                        "focus": "Expanding fields, food forests, animal systems, greenhouses"
                    },
                    {
                        "name": "Community Completion",
                        "duration_months": 48,
                        "focus": "Education facilities, additional housing, markets, distribution systems"
                    }
                ],
                special_features=[
                    "Grain processing facility",
                    "Community supported agriculture program",
                    "Regional seed bank",
                    "Four-season farmers market",
                    "Agricultural equipment sharing system"
                ],
                estimated_implementation_cost=7000000.0,
                estimated_annual_operating_cost=400000.0,
                mutual_aid_connections=[]
            ),
            
            # Southwest Desert Oasis
            Community(
                community_id="southwest_oasis",
                name="Desert Oasis Community",
                region_id="southwest",
                scale=CommunityScale.NEIGHBORHOOD,
                focus=CommunityFocus.WATER,
                governance=GovernanceModel.CONSENSUS,
                description="A water-wise desert community demonstrating regenerative living in arid conditions through careful water harvesting and management.",
                target_population=75,
                land_area_acres=50.0,
                bioregion_features=[
                    "Desert wash water harvesting",
                    "Xeriscaping throughout",
                    "Shaded microclimate creation",
                    "Desert soil building"
                ],
                building_systems=["rammed_earth", "modified_earthship"],
                energy_systems=["solar_battery"],
                water_systems=["rainwater_harvest", "drip_irrigation"],
                food_systems=["food_forest", "aquaponics"],
                skill_requirements={
                    "water_management": 7,
                    "desert_ecology": 4,
                    "natural_building": 5,
                    "solar_energy": 4,
                    "arid_land_restoration": 4,
                    "xeriscaping": 3,
                    "community_facilitation": 2
                },
                development_phases=[
                    {
                        "name": "Water Systems Establishment",
                        "duration_months": 12,
                        "focus": "Water harvesting earthworks, cisterns, initial shade structures"
                    },
                    {
                        "name": "Core Habitat Development",
                        "duration_months": 18,
                        "focus": "Primary buildings, solar systems, initial food production"
                    },
                    {
                        "name": "Expansion Phase",
                        "duration_months": 24,
                        "focus": "Additional housing, expanded water catchment, food forest"
                    },
                    {
                        "name": "Demonstration Completion",
                        "duration_months": 24,
                        "focus": "Education center, visitor facilities, expanded systems"
                    }
                ],
                special_features=[
                    "Desert water harvesting demonstration site",
                    "Shadehouse nursery for native and food plants",
                    "Passive cooling systems",
                    "Desert permaculture educational programs",
                    "Native pollinator habitat restoration"
                ],
                estimated_implementation_cost=2500000.0,
                estimated_annual_operating_cost=150000.0,
                mutual_aid_connections=[]
            ),
            
            # Northern Plains Regenerative Hub
            Community(
                community_id="plains_regenerative",
                name="Great Plains Regeneration Center",
                region_id="northern_plains",
                scale=CommunityScale.SMALL_CITY,
                focus=CommunityFocus.MIXED_USE,
                governance=GovernanceModel.SOCIOCRACY,
                description="A regenerative hub for the Great Plains designed to restore grasslands while creating a resilient community with agricultural and manufacturing capacity.",
                target_population=2000,
                land_area_acres=5000.0,
                bioregion_features=[
                    "Tallgrass prairie restoration",
                    "Watershed regeneration",
                    "Windbreak development",
                    "Soil carbon sequestration"
                ],
                building_systems=["advanced_framing", "straw_bale", "rammed_earth"],
                energy_systems=["small_wind", "solar_battery", "biogas"],
                water_systems=["rainwater_harvest", "drip_irrigation"],
                food_systems=["rotational_grazing", "intensive_annual", "food_forest"],
                skill_requirements={
                    "grassland_restoration": 5,
                    "regenerative_agriculture": 8,
                    "renewable_energy": 6,
                    "community_planning": 4,
                    "manufacturing": 7,
                    "water_management": 5,
                    "education": 4
                },
                development_phases=[
                    {
                        "name": "Initial Settlement",
                        "duration_months": 12,
                        "focus": "Core infrastructure, temporary housing, initial watershed work"
                    },
                    {
                        "name": "Agricultural Systems",
                        "duration_months": 24,
                        "focus": "Grazing setup, wind systems, primary housing, soil building"
                    },
                    {
                        "name": "Manufacturing Development",
                        "duration_months": 36,
                        "focus": "Production facilities, additional housing, expanded energy"
                    },
                    {
                        "name": "Regional Hub Completion",
                        "duration_months": 48,
                        "focus": "Education center, processing facilities, distribution network"
                    }
                ],
                special_features=[
                    "Bison restoration program",
                    "Wind turbine manufacturing facility",
                    "Regenerative grazing demonstration",
                    "Climate-appropriate building center",
                    "Prairie seed bank and nursery"
                ],
                estimated_implementation_cost=15000000.0,
                estimated_annual_operating_cost=1200000.0,
                mutual_aid_connections=[]
            )
        ]
        
        # Add communities
        for community in default_communities:
            self.communities[community.community_id] = community
            self._save_community(community)
            
        logger.info(f"Initialized {len(default_communities)} default community templates")
    
    def get_community(self, community_id: str) -> Optional[Community]:
        """
        Get a community by ID.
        
        Args:
            community_id: Community identifier
            
        Returns:
            Community if found, None otherwise
        """
        return self.communities.get(community_id)
    
    def get_all_communities(self) -> List[Community]:
        """
        Get all communities.
        
        Returns:
            List of communities
        """
        return list(self.communities.values())
    
    def add_community(self, community: Community) -> bool:
        """
        Add a new community.
        
        Args:
            community: Community to add
            
        Returns:
            Success status
        """
        # Check if already exists
        if community.community_id in self.communities:
            return False
            
        # Add community
        self.communities[community.community_id] = community
        
        # Save to disk
        self._save_community(community)
        
        return True
    
    def update_community(self, community: Community) -> bool:
        """
        Update an existing community.
        
        Args:
            community: Community to update
            
        Returns:
            Success status
        """
        # Check if exists
        if community.community_id not in self.communities:
            return False
            
        # Update community
        self.communities[community.community_id] = community
        
        # Save to disk
        self._save_community(community)
        
        return True
    
    def get_building_system(self, system_id: str) -> Optional[BuildingSystem]:
        """Get a building system by ID."""
        return self.building_systems.get(system_id)
    
    def get_energy_system(self, system_id: str) -> Optional[EnergySystem]:
        """Get an energy system by ID."""
        return self.energy_systems.get(system_id)
    
    def get_water_system(self, system_id: str) -> Optional[WaterSystem]:
        """Get a water system by ID."""
        return self.water_systems.get(system_id)
    
    def get_food_system(self, system_id: str) -> Optional[FoodSystem]:
        """Get a food system by ID."""
        return self.food_systems.get(system_id)
    
    def find_communities_for_region(self, region_id: str) -> List[Community]:
        """
        Find community templates suitable for a specific region.
        
        Args:
            region_id: Region identifier
            
        Returns:
            List of suitable communities
        """
        # Find all communities for this region
        region_communities = [c for c in self.communities.values() if c.region_id == region_id]
        
        # If none specific to this region, find communities with adaptable designs
        if not region_communities:
            # Check all communities
            region_communities = []
            
            for community in self.communities.values():
                # Check if building systems are adaptable to this region
                building_suitable = any(
                    self.building_systems.get(b_id) and region_id in self.building_systems[b_id].region_suitability
                    for b_id in community.building_systems
                )
                
                # Check if water systems are adaptable to this region
                water_suitable = any(
                    self.water_systems.get(w_id) and region_id in self.water_systems[w_id].region_suitability
                    for w_id in community.water_systems
                )
                
                if building_suitable and water_suitable:
                    region_communities.append(community)
                    
        return region_communities
    
    def design_community_for_region(self, 
                                 region_id: str,
                                 scale: CommunityScale,
                                 focus: CommunityFocus,
                                 name: str = None) -> Optional[Community]:
        """
        Design a custom community template for a specific region.
        
        Args:
            region_id: Region identifier
            scale: Community scale
            focus: Community focus
            name: Optional name
            
        Returns:
            Custom community design
        """
        # Get region
        region = self.mapper.get_region(region_id)
        if not region:
            return None
            
        # Generate community ID
        community_id = f"{region_id}_{focus.name.lower()}_{scale.name.lower()}"
        
        # Generate name if not provided
        if not name:
            name = f"{region.name} {focus.name.title()} {scale.name.title()}"
            
        # Determine appropriate governance models based on scale
        governance = GovernanceModel.CONSENSUS
        if scale == CommunityScale.TOWN:
            governance = GovernanceModel.SOCIOCRACY
        elif scale == CommunityScale.SMALL_CITY:
            governance = GovernanceModel.COUNCIL
        elif scale == CommunityScale.REGIONAL_HUB:
            governance = GovernanceModel.REPRESENTATIVE
            
        # Determine population based on scale
        population_by_scale = {
            CommunityScale.NEIGHBORHOOD: 100,
            CommunityScale.VILLAGE: 250,
            CommunityScale.TOWN: 1000,
            CommunityScale.SMALL_CITY: 5000,
            CommunityScale.REGIONAL_HUB: 10000
        }
        target_population = population_by_scale.get(scale, 250)
        
        # Determine land area based on scale and region characteristics
        base_land_area = {
            CommunityScale.NEIGHBORHOOD: 50.0,
            CommunityScale.VILLAGE: 200.0,
            CommunityScale.TOWN: 800.0,
            CommunityScale.SMALL_CITY: 3000.0,
            CommunityScale.REGIONAL_HUB: 8000.0
        }
        land_area = base_land_area.get(scale, 200.0)
        
        # Adjust land area based on region characteristics
        if region.metrics.water_availability.value <= WaterAvailability.STRESSED.value:
            land_area *= 1.5  # Need more land in water-stressed regions
        if region.metrics.soil_quality.value <= SoilQuality.MODERATE.value:
            land_area *= 1.3  # Need more land with moderate soil
            
        # Select suitable building systems
        climate_zone = region.metrics.climate_zone
        building_systems = []
        
        for system_id, system in self.building_systems.items():
            if region_id in system.region_suitability or climate_zone in system.climate_suitability:
                building_systems.append(system_id)
                
        building_systems = building_systems[:3]  # Limit to top 3
        
        # Select suitable energy systems
        energy_systems = []
        
        # Check region's energy potential
        if region.metrics.renewable_energy_potential.get("solar", 0) > 20000000000:
            energy_systems.append("solar_battery")
        if region.metrics.renewable_energy_potential.get("wind", 0) > 20000000000:
            energy_systems.append("small_wind")
        if region.metrics.renewable_energy_potential.get("hydro", 0) > 5000000000:
            energy_systems.append("micro_hydro")
            
        # Add biogas for agricultural focus
        if focus == CommunityFocus.AGRICULTURAL:
            energy_systems.append("biogas")
            
        # Add geothermal where appropriate
        if climate_zone in [ClimateZone.CONTINENTAL_COOL, ClimateZone.CONTINENTAL_WARM, 
                           ClimateZone.CONTINENTAL_HOT, ClimateZone.SUBARCTIC]:
            energy_systems.append("geothermal_heat")
            
        # Ensure at least one energy system
        if not energy_systems:
            energy_systems.append("solar_battery")
            
        # Select suitable water systems
        water_systems = []
        
        if region.metrics.water_availability.value >= WaterAvailability.SUFFICIENT.value:
            water_systems.append("rainwater_harvest")
            
        # Add appropriate water management systems based on climate
        if climate_zone in [ClimateZone.DESERT_HOT, ClimateZone.DESERT_COLD, 
                           ClimateZone.STEPPE_HOT, ClimateZone.STEPPE_COLD]:
            water_systems.append("drip_irrigation")
        else:
            water_systems.append("living_machine")
            
        # Add slow sand filtration for most regions
        water_systems.append("slow_sand")
        
        # Add fog collection for suitable regions
        if climate_zone in [ClimateZone.OCEANIC, ClimateZone.MEDITERRANEAN] and "coastal" in region.name.lower():
            water_systems.append("fog_collection")
            
        # Select suitable food systems
        food_systems = []
        
        # Add food systems based on focus
        if focus == CommunityFocus.AGRICULTURAL:
            food_systems.extend(["rotational_grazing", "intensive_annual"])
        else:
            food_systems.append("intensive_annual")
            
        # Add appropriate systems based on climate
        if climate_zone in [ClimateZone.CONTINENTAL_COOL, ClimateZone.CONTINENTAL_WARM, 
                           ClimateZone.CONTINENTAL_HOT, ClimateZone.SUBARCTIC]:
            food_systems.append("passive_greenhouse")
            
        # Add food forest for most regions
        if climate_zone not in [ClimateZone.DESERT_HOT, ClimateZone.DESERT_COLD, ClimateZone.POLAR_ICE]:
            food_systems.append("food_forest")
            
        # Add aquaponics for specialized production
        if focus in [CommunityFocus.TECHNOLOGICAL, CommunityFocus.EDUCATIONAL]:
            food_systems.append("aquaponics")
            
        # Determine bioregion features
        bioregion_features = []
        
        # Add features based on region ecosystems
        for ecosystem in region.metrics.ecosystem_types:
            if ecosystem == EcosystemType.FOREST_TEMPERATE:
                bioregion_features.append("Temperate forest integration")
            elif ecosystem == EcosystemType.GRASSLAND:
                bioregion_features.append("Native grassland restoration")
            elif ecosystem == EcosystemType.DESERT:
                bioregion_features.append("Desert ecology preservation")
            elif ecosystem == EcosystemType.WETLAND:
                bioregion_features.append("Wetland conservation and expansion")
                
        # Add water-related feature
        if region.metrics.water_availability.value >= WaterAvailability.SUFFICIENT.value:
            bioregion_features.append("Watershed protection and enhancement")
        else:
            bioregion_features.append("Water conservation and harvesting systems")
            
        # Add climate feature
        bioregion_features.append(f"{climate_zone.name.replace('_', ' ').title()} climate adaptation strategies")
        
        # Determine required skills based on focus and systems
        skill_requirements = {
            "community_facilitation": 3,  # Always needed
            "ecological_literacy": 4,     # Always needed
            "infrastructure_maintenance": 3  # Always needed
        }
        
        # Add skills based on focus
        if focus == CommunityFocus.AGRICULTURAL:
            skill_requirements.update({
                "regenerative_agriculture": 5,
                "food_processing": 4,
                "seed_saving": 3
            })
        elif focus == CommunityFocus.ECOLOGICAL:
            skill_requirements.update({
                "ecosystem_restoration": 5,
                "wildlife_management": 3,
                "botanical_knowledge": 4
            })
        elif focus == CommunityFocus.EDUCATIONAL:
            skill_requirements.update({
                "teaching": 5,
                "curriculum_development": 4,
                "facilitation": 4
            })
        elif focus == CommunityFocus.MANUFACTURING:
            skill_requirements.update({
                "fabrication": 5,
                "material_processing": 4,
                "design": 4
            })
        elif focus == CommunityFocus.ENERGY:
            skill_requirements.update({
                "renewable_energy": 5,
                "electrical_systems": 4,
                "energy_storage": 4
            })
            
        # Create phased development plan
        development_phases = [
            {
                "name": "Foundation Phase",
                "duration_months": 12,
                "focus": "Site assessment, initial infrastructure, temporary housing, resource inventory"
            },
            {
                "name": "Core Development",
                "duration_months": 24,
                "focus": "Primary buildings, basic systems, initial food production, governance establishment"
            },
            {
                "name": "Expansion Phase",
                "duration_months": 36,
                "focus": "Additional housing, expanded production, specialized facilities, refinement of systems"
            },
            {
                "name": "Maturity & Outreach",
                "duration_months": 48,
                "focus": "Education programs, regional connections, resilience enhancements, cultural development"
            }
        ]
        
        # Calculate estimated costs
        base_implementation_cost = {
            CommunityScale.NEIGHBORHOOD: 2000000.0,
            CommunityScale.VILLAGE: 5000000.0,
            CommunityScale.TOWN: 15000000.0,
            CommunityScale.SMALL_CITY: 50000000.0,
            CommunityScale.REGIONAL_HUB: 120000000.0
        }
        
        base_operating_cost = {
            CommunityScale.NEIGHBORHOOD: 150000.0,
            CommunityScale.VILLAGE: 400000.0,
            CommunityScale.TOWN: 1200000.0,
            CommunityScale.SMALL_CITY: 4000000.0,
            CommunityScale.REGIONAL_HUB: 10000000.0
        }
        
        # Adjust costs based on region and focus
        implementation_cost = base_implementation_cost.get(scale, 5000000.0)
        operating_cost = base_operating_cost.get(scale, 400000.0)
        
        # Adjust for infrastructure status
        if region.metrics.infrastructure_status.value <= InfrastructureStatus.DEGRADED.value:
            implementation_cost *= 1.3  # Higher cost in regions with poor infrastructure
            
        # Create community design
        community = Community(
            community_id=community_id,
            name=name,
            region_id=region_id,
            scale=scale,
            focus=focus,
            governance=governance,
            description=f"Custom {focus.name.lower()} community designed for the {region.name}, emphasizing sustainable development tailored to local bioregional characteristics.",
            target_population=target_population,
            land_area_acres=land_area,
            bioregion_features=bioregion_features,
            building_systems=building_systems,
            energy_systems=energy_systems,
            water_systems=water_systems,
            food_systems=food_systems,
            skill_requirements=skill_requirements,
            development_phases=development_phases,
            special_features=[],  # To be customized
            estimated_implementation_cost=implementation_cost,
            estimated_annual_operating_cost=operating_cost,
            mutual_aid_connections=[]
        )
        
        return community
    
    def calculate_community_requirements(self, community: Community) -> Dict[str, Any]:
        """
        Calculate detailed requirements for implementing a community design.
        
        Args:
            community: Community design
            
        Returns:
            Detailed requirements
        """
        try:
            # Calculate total material requirements
            building_materials = {}
            
            # Process building systems
            for system_id in community.building_systems:
                building_system = self.building_systems.get(system_id)
                if building_system:
                    # Calculate average dwelling size
                    avg_dwelling_size = 100.0  # square meters
                    
                    # Estimate number of dwellings based on population
                    dwellings = math.ceil(community.target_population / 2.5)  # Average household size
                    
                    # Calculate material requirements
                    total_area = dwellings * avg_dwelling_size
                    
                    for material in building_system.primary_materials:
                        if material in building_materials:
                            building_materials[material] += total_area / len(building_system.primary_materials)
                        else:
                            building_materials[material] = total_area / len(building_system.primary_materials)
            
            # Calculate infrastructure requirements
            infrastructure_requirements = {
                "road_length_km": math.sqrt(community.land_area_acres * 0.004) * 3,  # Approximate road network
                "water_storage_liters": community.target_population * 200,  # 200 liters per person
                "common_buildings": math.ceil(community.target_population / 200) + 3  # Community buildings
            }
            
            # Calculate energy requirements
            energy_requirements = {
                "daily_consumption_kwh": community.target_population * 2.5,  # Per person
                "peak_capacity_kw": community.target_population * 0.8,
                "storage_capacity_kwh": community.target_population * 3.0
            }
            
            # Calculate water requirements
            water_requirements = {
                "daily_consumption_liters": community.target_population * 150,  # 150 liters per person per day
                "irrigation_liters": sum(
                    self.food_systems.get(f_id).water_required_liters_per_day
                    for f_id in community.food_systems
                    if f_id in self.food_systems
                )
            }
            
            # Calculate food production capacity
            food_capacity = 0.0
            food_area_required = 0.0
            
            for system_id in community.food_systems:
                food_system = self.food_systems.get(system_id)
                if food_system:
                    # Calculate area based on scale
                    if food_system.production_type == "garden":
                        area = max(food_system.area_required_sqm * (community.target_population / 100), food_system.area_required_sqm)
                    elif food_system.production_type == "agroforestry":
                        area = max(food_system.area_required_sqm * (community.target_population / 50), food_system.area_required_sqm)
                    elif food_system.production_type == "grazing":
                        area = max(food_system.area_required_sqm * (community.target_population / 25), food_system.area_required_sqm)
                    else:
                        area = food_system.area_required_sqm * (community.target_population / 100)
                        
                    # Calculate calories produced
                    calories = area * food_system.typical_yield_calories_per_sqm
                    
                    # Add to totals
                    food_capacity += calories
                    food_area_required += area
                    
            # Calculate percentage of food self-sufficiency
            daily_calorie_needs = community.target_population * 2200  # 2200 calories per person per day
            annual_calorie_needs = daily_calorie_needs * 365
            annual_production = food_capacity * 365
            
            food_self_sufficiency = min(100.0, (annual_production / annual_calorie_needs) * 100) if annual_calorie_needs > 0 else 0
            
            # Calculate labor requirements
            core_team_size = max(3, math.ceil(community.target_population / 100))
            
            labor_requirements = {
                "core_planning_team": core_team_size,
                "construction_phase": math.ceil(dwellings / 4) + 5,  # Based on building needs
                "agricultural_workers": math.ceil(food_area_required / 10000)  # 1 worker per hectare
            }
            
            # Calculate implementation timeline
            total_implementation_months = max(
                phase["duration_months"] for phase in community.development_phases
            ) if community.development_phases else 60
            
            # Return all calculations
            return {
                "building_materials": building_materials,
                "infrastructure_requirements": infrastructure_requirements,
                "energy_requirements": energy_requirements,
                "water_requirements": water_requirements,
                "food_production": {
                    "annual_calories": annual_production,
                    "self_sufficiency_percent": food_self_sufficiency,
                    "area_required_sqm": food_area_required
                },
                "labor_requirements": labor_requirements,
                "implementation_timeline_months": total_implementation_months
            }
            
        except Exception as e:
            logger.error(f"Error calculating community requirements: {e}")
            return {"error": str(e)}


# ====================================================================
# 3. COLLABORATIVE RELOCATION NETWORK
# ====================================================================

class RelocationProjectStatus(Enum):
    """Status of relocation project."""
    PROPOSED = auto()       # Initial proposal stage
    PLANNING = auto()       # Active planning stage
    RECRUITING = auto()     # Recruiting participants
    PREPARING = auto()      # Preparations underway
    RELOCATING = auto()     # Active relocation happening
    ESTABLISHED = auto()    # Community established
    ON_HOLD = auto()        # Temporarily paused
    CANCELLED = auto()      # Project cancelled


class SkillCategory(Enum):
    """Categories of skills for relocation matching."""
    AGRICULTURE = auto()     # Farming, gardening, etc.
    BUILDING = auto()        # Construction, building trades
    ENERGY = auto()          # Renewable energy systems
    WATER = auto()           # Water management
    HEALTHCARE = auto()      # Medical, first aid, herbalism
    EDUCATION = auto()       # Teaching, facilitation
    GOVERNANCE = auto()      # Community organization
    MANUFACTURING = auto()   # Making, fabrication
    ECOLOGY = auto()         # Ecosystem knowledge
    CRAFT = auto()           # Traditional crafts
    TECHNOLOGY = auto()      # Digital, communications
    CARE = auto()            # Childcare, elder care


@dataclass
class HumanRelocator:
    """Human participant in relocation project."""
    human_id: str
    name: str
    current_region: str
    preferred_regions: List[str]
    skills: Dict[str, float]  # Skill category -> proficiency (0-1)
    interests: List[str]
    constraints: List[str]
    household_size: int
    has_children: bool
    preferred_community_scale: Optional[CommunityScale] = None
    preferred_community_focus: Optional[CommunityFocus] = None
    preferred_governance: Optional[GovernanceModel] = None
    relocation_timeline_months: Optional[int] = None
    resources_available: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RelocationProject:
    """Collaborative community relocation project."""
    project_id: str
    name: str
    target_region_id: str
    status: RelocationProjectStatus
    description: str
    community_model_id: Optional[str]  # Reference to Community template
    target_population: int
    current_participants: List[str]  # Human IDs
    project_coordinators: List[str]  # Human IDs of coordinators
    start_date: float
    projected_completion_date: Optional[float] = None
    land_status: str = "Seeking"  # "Seeking", "In negotiation", "Secured"
    project_phases: List[Dict[str, Any]] = field(default_factory=list)
    community_agreements: Dict[str, Any] = field(default_factory=dict)
    skill_coverage: Dict[str, float] = field(default_factory=dict)
    skill_gaps: Dict[str, float] = field(default_factory=dict)
    mutual_aid_partnerships: List[str] = field(default_factory=list)  # Other project IDs
    updates: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MutualAidOffer:
    """Offer of mutual aid between communities."""
    offer_id: str
    source_id: str  # Community or project ID
    target_id: str  # Community or project ID
    offer_type: str  # "skills", "resources", "knowledge", etc.
    description: str
    quantity: Optional[str] = None
    duration: Optional[str] = None
    conditions: List[str] = field(default_factory=list)
    status: str = "offered"  # "offered", "accepted", "fulfilled", "declined"
    contact_human_id: str = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class CollaborativeRelocationNetwork:
    """
    Network for coordinating collaborative relocation and community formation.
    """
    
    def __init__(self,
                bioregional_mapper: BioregionalMapper,
                community_designer: SustainableCommunityDesigner,
                data_path: str = "relocation_data"):
        """
        Initialize collaborative relocation network.
        
        Args:
            bioregional_mapper: Bioregional mapper
            community_designer: Sustainable community designer
            data_path: Path for storing relocation data
        """
        self.mapper = bioregional_mapper
        self.designer = community_designer
        self.data_path = data_path
        
        # Ensure paths exist
        os.makedirs(data_path, exist_ok=True)
        os.makedirs(os.path.join(data_path, "relocators"), exist_ok=True)
        os.makedirs(os.path.join(data_path, "projects"), exist_ok=True)
        os.makedirs(os.path.join(data_path, "aid_offers"), exist_ok=True)
        
        # Load data
        self.relocators: Dict[str, HumanRelocator] = {}
        self.projects: Dict[str, RelocationProject] = {}
        self.aid_offers: Dict[str, MutualAidOffer] = {}
        
        self._load_data()
    
    def _load_data(self) -> None:
        """Load relocation data from disk."""
        try:
            # Load relocators
            relocators_dir = os.path.join(self.data_path, "relocators")
            for filename in os.listdir(relocators_dir):
                if filename.endswith(".json"):
                    file_path = os.path.join(relocators_dir, filename)
                    try:
                        with open(file_path, "r") as f:
                            data = json.load(f)
                            
                            # Parse community scale preference if present
                            preferred_scale = None
                            if "preferred_community_scale" in data and data["preferred_community_scale"]:
                                preferred_scale = CommunityScale[data["preferred_community_scale"]]
                                
                            # Parse community focus preference if present
                            preferred_focus = None
                            if "preferred_community_focus" in data and data["preferred_community_focus"]:
                                preferred_focus = CommunityFocus[data["preferred_community_focus"]]
                                
                            # Parse governance preference if present
                            preferred_governance = None
                            if "preferred_governance" in data and data["preferred_governance"]:
                                preferred_governance = GovernanceModel[data["preferred_governance"]]
                            
                            relocator = HumanRelocator(
                                human_id=data.get("human_id", filename.replace(".json", "")),
                                name=data.get("name", "Unknown"),
                                current_region=data.get("current_region", ""),
                                preferred_regions=data.get("preferred_regions", []),
                                skills=data.get("skills", {}),
                                interests=data.get("interests", []),
                                constraints=data.get("constraints", []),
                                household_size=data.get("household_size", 1),
                                has_children=data.get("has_children", False),
                                preferred_community_scale=preferred_scale,
                                preferred_community_focus=preferred_focus,
                                preferred_governance=preferred_governance,
                                relocation_timeline_months=data.get("relocation_timeline_months"),
                                resources_available=data.get("resources_available", {}),
                                metadata=data.get("metadata", {})
                            )
                            self.relocators[relocator.human_id] = relocator
                    except Exception as e:
                        logger.error(f"Error loading relocator from {file_path}: {e}")
                        
            # Load projects
            projects_dir = os.path.join(self.data_path, "projects")
            for filename in os.listdir(projects_dir):
                if filename.endswith(".json"):
                    file_path = os.path.join(projects_dir, filename)
                    try:
                        with open(file_path, "r") as f:
                            data = json.load(f)
                            project = RelocationProject(
                                project_id=data.get("project_id", filename.replace(".json", "")),
                                name=data.get("name", "Unknown Project"),
                                target_region_id=data.get("target_region_id", ""),
                                status=RelocationProjectStatus[data.get("status", "PROPOSED")],
                                description=data.get("description", ""),
                                community_model_id=data.get("community_model_id"),
                                target_population=data.get("target_population", 0),
                                current_participants=data.get("current_participants", []),
                                project_coordinators=data.get("project_coordinators", []),
                                start_date=data.get("start_date", time.time()),
                                projected_completion_date=data.get("projected_completion_date"),
                                land_status=data.get("land_status", "Seeking"),
                                project_phases=data.get("project_phases", []),
                                community_agreements=data.get("community_agreements", {}),
                                skill_coverage=data.get("skill_coverage", {}),
                                skill_gaps=data.get("skill_gaps", {}),
                                mutual_aid_partnerships=data.get("mutual_aid_partnerships", []),
                                updates=data.get("updates", []),
                                metadata=data.get("metadata", {})
                            )
                            self.projects[project.project_id] = project
                    except Exception as e:
                        logger.error(f"Error loading project from {file_path}: {e}")
                        
            # Load aid offers
            aid_offers_dir = os.path.join(self.data_path, "aid_offers")
            for filename in os.listdir(aid_offers_dir):
                if filename.endswith(".json"):
                    file_path = os.path.join(aid_offers_dir, filename)
                    try:
                        with open(file_path, "r") as f:
                            data = json.load(f)
                            offer = MutualAidOffer(
                                offer_id=data.get("offer_id", filename.replace(".json", "")),
                                source_id=data.get("source_id", ""),
                                target_id=data.get("target_id", ""),
                                offer_type=data.get("offer_type", ""),
                                description=data.get("description", ""),
                                quantity=data.get("quantity"),
                                duration=data.get("duration"),
                                conditions=data.get("conditions", []),
                                status=data.get("status", "offered"),
                                contact_human_id=data.get("contact_human_id"),
                                metadata=data.get("metadata", {})
                            )
                            self.aid_offers[offer.offer_id] = offer
                    except Exception as e:
                        logger.error(f"Error loading aid offer from {file_path}: {e}")
                        
            logger.info(f"Loaded {len(self.relocators)} relocators, {len(self.projects)} projects, and {len(self.aid_offers)} aid offers")
            
        except Exception as e:
            logger.error(f"Error loading relocation data: {e}")
    
    def _save_relocator(self, relocator: HumanRelocator) -> None:
        """Save relocator to disk."""
        try:
            file_path = os.path.join(self.data_path, "relocators", f"{relocator.human_id}.json")
            
            # Format preferences for serialization
            preferred_scale = relocator.preferred_community_scale.name if relocator.preferred_community_scale else None
            preferred_focus = relocator.preferred_community_focus.name if relocator.preferred_community_focus else None
            preferred_governance = relocator.preferred_governance.name if relocator.preferred_governance else None
            
            # Prepare relocator data
            relocator_data = {
                "human_id": relocator.human_id,
                "name": relocator.name,
                "current_region": relocator.current_region,
                "preferred_regions": relocator.preferred_regions,
                "skills": relocator.skills,
                "interests": relocator.interests,
                "constraints": relocator.constraints,
                "household_size": relocator.household_size,
                "has_children": relocator.has_children,
                "preferred_community_scale": preferred_scale,
                "preferred_community_focus": preferred_focus,
                "preferred_governance": preferred_governance,
                "relocation_timeline_months": relocator.relocation_timeline_months,
                "resources_available": relocator.resources_available,
                "metadata": relocator.metadata
            }
            
            with open(file_path, "w") as f:
                json.dump(relocator_data, f, indent=2)
                
        except Exception as e:
            logger.error(f"Error saving relocator: {e}")
    
    def _save_project(self, project: RelocationProject) -> None:
        """Save project to disk."""
        try:
            file_path = os.path.join(self.data_path, "projects", f"{project.project_id}.json")
            
            # Prepare project data
            project_data = {
                "project_id": project.project_id,
                "name": project.name,
                "target_region_id": project.target_region_id,
                "status": project.status.name,
                "description": project.description,
                "community_model_id": project.community_model_id,
                "target_population": project.target_population,
                "current_participants": project.current_participants,
                "project_coordinators": project.project_coordinators,
                "start_date": project.start_date,
                "projected_completion_date": project.projected_completion_date,
                "land_status": project.land_status,
                "project_phases": project.project_phases,
                "community_agreements": project.community_agreements,
                "skill_coverage": project.skill_coverage,
                "skill_gaps": project.skill_gaps,
                "mutual_aid_partnerships": project.mutual_aid_partnerships,
                "updates": project.updates,
                "metadata": project.metadata
            }
            
            with open(file_path, "w") as f:
                json.dump(project_data, f, indent=2)
                
        except Exception as e:
            logger.error(f"Error saving project: {e}")
    
    def _save_aid_offer(self, offer: MutualAidOffer) -> None:
        """Save aid offer to disk."""
        try:
            file_path = os.path.join(self.data_path, "aid_offers", f"{offer.offer_id}.json")
            
            # Prepare offer data
            offer_data = {
                "offer_id": offer.offer_id,
                "source_id": offer.source_id,
                "target_id": offer.target_id,
                "offer_type": offer.offer_type,
                "description": offer.description,
                "quantity": offer.quantity,
                "duration": offer.duration,
                "conditions": offer.conditions,
                "status": offer.status,
                "contact_human_id": offer.contact_human_id,
                "metadata": offer.metadata
            }
            
            with open(file_path, "w") as f:
                json.dump(offer_data, f, indent=2)
                
        except Exception as e:
            logger.error(f"Error saving aid offer: {e}")
    
    def register_relocator(self, relocator: Dict[str, Any]) -> Dict[str, Any]:
        """
        Register a human relocator.
        
        Args:
            relocator: Relocator information
            
        Returns:
            Registration result
        """
        try:
            # Validate required fields
            required_fields = ["name", "current_region"]
            for field in required_fields:
                if field not in relocator:
                    return {
                        "success": False,
                        "error": f"Missing required field: {field}"
                    }
                    
            # Generate ID if not provided
            human_id = relocator.get("human_id")
            if not human_id:
                human_id = f"relocator_{hashlib.md5(f'{relocator['name']}_{time.time()}'.encode()).hexdigest()[:8]}"
                
            # Parse community scale preference if present
            preferred_scale = None
            if "preferred_community_scale" in relocator:
                try:
                    preferred_scale = CommunityScale[relocator["preferred_community_scale"]]
                except KeyError:
                    return {
                        "success": False,
                        "error": f"Invalid community scale: {relocator['preferred_community_scale']}"
                    }
                    
            # Parse community focus preference if present
            preferred_focus = None
            if "preferred_community_focus" in relocator:
                try:
                    preferred_focus = CommunityFocus[relocator["preferred_community_focus"]]
                except KeyError:
                    return {
                        "success": False,
                        "error": f"Invalid community focus: {relocator['preferred_community_focus']}"
                    }
                    
            # Parse governance preference if present
            preferred_governance = None
            if "preferred_governance" in relocator:
                try:
                    preferred_governance = GovernanceModel[relocator["preferred_governance"]]
                except KeyError:
                    return {
                        "success": False,
                        "error": f"Invalid governance model: {relocator['preferred_governance']}"
                    }
                    
            # Create relocator
            new_relocator = HumanRelocator(
                human_id=human_id,
                name=relocator["name"],
                current_region=relocator["current_region"],
                preferred_regions=relocator.get("preferred_regions", []),
                skills=relocator.get("skills", {}),
                interests=relocator.get("interests", []),
                constraints=relocator.get("constraints", []),
                household_size=relocator.get("household_size", 1),
                has_children=relocator.get("has_children", False),
                preferred_community_scale=preferred_scale,
                preferred_community_focus=preferred_focus,
                preferred_governance=preferred_governance,
                relocation_timeline_months=relocator.get("relocation_timeline_months"),
                resources_available=relocator.get("resources_available", {}),
                metadata=relocator.get("metadata", {})
            )
            
            # Add relocator
            self.relocators[human_id] = new_relocator
            
            # Save to disk
            self._save_relocator(new_relocator)
            
            return {
                "success": True,
                "human_id": human_id,
                "message": f"Registered relocator: {new_relocator.name}"
            }
            
        except Exception as e:
            logger.error(f"Error registering relocator: {e}")
            return {
                "success": False,
                "error": f"Registration error: {str(e)}"
            }
    
    def create_relocation_project(self, project: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new relocation project.
        
        Args:
            project: Project information
            
        Returns:
            Creation result
        """
        try:
            # Validate required fields
            required_fields = ["name", "target_region_id", "description"]
            for field in required_fields:
                if field not in project:
                    return {
                        "success": False,
                        "error": f"Missing required field: {field}"
                    }
                    
            # Check region validity
            region = self.mapper.get_region(project["target_region_id"])
            if not region:
                return {
                    "success": False,
                    "error": f"Invalid region ID: {project['target_region_id']}"
                }
                
            # Generate ID if not provided
            project_id = project.get("project_id")
            if not project_id:
                project_id = f"project_{hashlib.md5(f'{project['name']}_{time.time()}'.encode()).hexdigest()[:8]}"
                
            # Parse status
            try:
                status = RelocationProjectStatus[project.get("status", "PROPOSED")]
            except KeyError:
                return {
                    "success": False,
                    "error": f"Invalid project status: {project.get('status')}"
                }
                
            # Create project
            new_project = RelocationProject(
                project_id=project_id,
                name=project["name"],
                target_region_id=project["target_region_id"],
                status=status,
                description=project["description"],
                community_model_id=project.get("community_model_id"),
                target_population=project.get("target_population", 100),
                current_participants=project.get("current_participants", []),
                project_coordinators=project.get("project_coordinators", []),
                start_date=project.get("start_date", time.time()),
                projected_completion_date=project.get("projected_completion_date"),
                land_status=project.get("land_status", "Seeking"),
                project_phases=project.get("project_phases", []),
                community_agreements=project.get("community_agreements", {}),
                skill_coverage=project.get("skill_coverage", {}),
                skill_gaps=project.get("skill_gaps", {}),
                mutual_aid_partnerships=project.get("mutual_aid_partnerships", []),
                updates=[
                    {
                        "timestamp": time.time(),
                        "type": "creation",
                        "content": f"Project created targeting the {region.name} region."
                    }
                ],
                metadata=project.get("metadata", {})
            )
            
            # Add project
            self.projects[project_id] = new_project
            
            # Save to disk
            self._save_project(new_project)
            
            return {
                "success": True,
                "project_id": project_id,
                "message": f"Created relocation project: {new_project.name}"
            }
            
        except Exception as e:
            logger.error(f"Error creating project: {e}")
            return {
                "success": False,
                "error": f"Project creation error: {str(e)}"
            }
    
    def join_project(self, project_id: str, human_id: str, role: str = "participant") -> Dict[str, Any]:
        """
        Join a relocation project.
        
        Args:
            project_id: Project identifier
            human_id: Human identifier
            role: Role in project ("participant", "coordinator")
            
        Returns:
            Join result
        """
        # Check project exists
        if project_id not in self.projects:
            return {
                "success": False,
                "error": "Project not found"
            }
            
        # Check human exists
        if human_id not in self.relocators:
            return {
                "success": False,
                "error": "Relocator not found"
            }
            
        try:
            project = self.projects[project_id]
            relocator = self.relocators[human_id]
            
            # Check if already in project
            if human_id in project.current_participants:
                return {
                    "success": False,
                    "error": f"Human {relocator.name} is already a participant in this project"
                }
                
            # Add to project
            project.current_participants.append(human_id)
            
            # Add as coordinator if requested
            if role == "coordinator" and human_id not in project.project_coordinators:
                project.project_coordinators.append(human_id)
                
            # Update skill coverage
            self._update_project_skill_coverage(project)
            
            # Add update
            project.updates.append({
                "timestamp": time.time(),
                "type": "new_member",
                "content": f"{relocator.name} joined the project as a {role}."
            })
            
            # Save project
            self._save_project(project)
            
            return {
                "success": True,
                "project_id": project_id,
                "human_id": human_id,
                "message": f"{relocator.name} joined project as a {role}"
            }
            
        except Exception as e:
            logger.error(f"Error joining project: {e}")
            return {
                "success": False,
                "error": f"Join error: {str(e)}"
            }
    
    def find_matching_projects(self, human_id: str, max_results: int = 3) -> Dict[str, Any]:
        """
        Find relocation projects matching a human's preferences.
        
        Args:
            human_id: Human identifier
            max_results: Maximum number of results
            
        Returns:
            Matching projects
        """
        # Check human exists
        if human_id not in self.relocators:
            return {
                "success": False,
                "error": "Relocator not found"
            }
            
        try:
            relocator = self.relocators[human_id]
            matches = []
            
            # Match to all active projects
            for project in self.projects.values():
                # Skip if not in active status
                if project.status not in [RelocationProjectStatus.PROPOSED, 
                                         RelocationProjectStatus.PLANNING,
                                         RelocationProjectStatus.RECRUITING]:
                    continue
                    
                # Calculate match score
                score = self._calculate_project_match_score(relocator, project)
                
                # Include match details
                match = {
                    "project_id": project.project_id,
                    "project_name": project.name,
                    "match_score": score,
                    "region_id": project.target_region_id,
                    "region_name": self.mapper.get_region(project.target_region_id).name if self.mapper.get_region(project.target_region_id) else "Unknown",
                    "description": project.description,
                    "target_population": project.target_population,
                    "current_participants": len(project.current_participants),
                    "status": project.status.name,
                    "community_model": None,
                    "skill_gaps": project.skill_gaps
                }
                
                # Add community model details if available
                if project.community_model_id:
                    community = self.designer.get_community(project.community_model_id)
                    if community:
                        match["community_model"] = {
                            "name": community.name,
                            "scale": community.scale.name,
                            "focus": community.focus.name,
                            "governance": community.governance.name
                        }
                        
                matches.append(match)
                
            # Sort by match score
            matches.sort(key=lambda x: x["match_score"], reverse=True)
            
            # Return top matches
            return {
                "success": True,
                "human_id": human_id,
                "human_name": relocator.name,
                "matches": matches[:max_results],
                "total_projects_searched": len(self.projects)
            }
            
        except Exception as e:
            logger.error(f"Error finding matching projects: {e}")
            return {
                "success": False,
                "error": f"Matching error: {str(e)}"
            }
    
    def find_matching_humans(self, project_id: str, max_results: int = 10) -> Dict[str, Any]:
        """
        Find humans matching a project's needs.
        
        Args:
            project_id: Project identifier
            max_results: Maximum number of results
            
        Returns:
            Matching humans
        """
        # Check project exists
        if project_id not in self.projects:
            return {
                "success": False,
                "error": "Project not found"
            }
            
        try:
            project = self.projects[project_id]
            matches = []
            
            # Match to all relocators
            for relocator in self.relocators.values():
                # Skip if already in project
                if relocator.human_id in project.current_participants:
                    continue
                    
                # Calculate match score
                score = self._calculate_project_match_score(relocator, project)
                
                # Calculate skill match
                skill_match = {}
                for skill, gap in project.skill_gaps.items():
                    if gap > 0.3 and skill in relocator.skills:
                        skill_match[skill] = relocator.skills[skill]
                
                # Include match details
                match = {
                    "human_id": relocator.human_id,
                    "name": relocator.name,
                    "match_score": score,
                    "current_region": relocator.current_region,
                    "preferred_regions": relocator.preferred_regions,
                    "household_size": relocator.household_size,
                    "skill_match": skill_match,
                    "relocation_timeline_months": relocator.relocation_timeline_months
                }
                
                matches.append(match)
                
            # Sort by match score
            matches.sort(key=lambda x: x["match_score"], reverse=True)
            
            # Return top matches
            return {
                "success": True,
                "project_id": project_id,
                "project_name": project.name,
                "matches": matches[:max_results],
                "skill_gaps": project.skill_gaps,
                "total_relocators_searched": len(self.relocators)
            }
            
        except Exception as e:
            logger.error(f"Error finding matching humans: {e}")
            return {
                "success": False,
                "error": f"Matching error: {str(e)}"
            }
    
    def update_project_status(self, project_id: str, new_status: str, update_note: str = None) -> Dict[str, Any]:
        """
        Update project status.
        
        Args:
            project_id: Project identifier
            new_status: New status
            update_note: Optional update note
            
        Returns:
            Update result
        """
        # Check project exists
        if project_id not in self.projects:
            return {
                "success": False,
                "error": "Project not found"
            }
            
        try:
            # Parse status
            try:
                status = RelocationProjectStatus[new_status]
            except KeyError:
                return {
                    "success": False,
                    "error": f"Invalid project status: {new_status}"
                }
                
            project = self.projects[project_id]
            
            # Record old status
            old_status = project.status
            
            # Update status
            project.status = status
            
            # Add update
            note = update_note if update_note else f"Status changed from {old_status.name} to {status.name}"
            project.updates.append({
                "timestamp": time.time(),
                "type": "status_change",
                "content": note
            })
            
            # Save project
            self._save_project(project)
            
            return {
                "success": True,
                "project_id": project_id,
                "old_status": old_status.name,
                "new_status": status.name,
                "message": f"Updated project status: {status.name}"
            }
            
        except Exception as e:
            logger.error(f"Error updating project status: {e}")
            return {
                "success": False,
                "error": f"Status update error: {str(e)}"
            }
    
    def create_mutual_aid_offer(self, offer: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a mutual aid offer between communities.
        
        Args:
            offer: Offer information
            
        Returns:
            Creation result
        """
        try:
            # Validate required fields
            required_fields = ["source_id", "target_id", "offer_type", "description"]
            for field in required_fields:
                if field not in offer:
                    return {
                        "success": False,
                        "error": f"Missing required field: {field}"
                    }
                    
            # Generate ID if not provided
            offer_id = offer.get("offer_id")
            if not offer_id:
                offer_id = f"offer_{hashlib.md5(f'{offer['source_id']}_{offer['target_id']}_{time.time()}'.encode()).hexdigest()[:8]}"
                
            # Create offer
            new_offer = MutualAidOffer(
                offer_id=offer_id,
                source_id=offer["source_id"],
                target_id=offer["target_id"],
                offer_type=offer["offer_type"],
                description=offer["description"],
                quantity=offer.get("quantity"),
                duration=offer.get("duration"),
                conditions=offer.get("conditions", []),
                status=offer.get("status", "offered"),
                contact_human_id=offer.get("contact_human_id"),
                metadata=offer.get("metadata", {})
            )
            
            # Add offer
            self.aid_offers[offer_id] = new_offer
            
            # Save to disk
            self._save_aid_offer(new_offer)
            
            # Update project partnerships if both are projects
            if offer["source_id"] in self.projects and offer["target_id"] in self.projects:
                source_project = self.projects[offer["source_id"]]
                target_project = self.projects[offer["target_id"]]
                
                if target_project.project_id not in source_project.mutual_aid_partnerships:
                    source_project.mutual_aid_partnerships.append(target_project.project_id)
                    self._save_project(source_project)
                    
                if source_project.project_id not in target_project.mutual_aid_partnerships:
                    target_project.mutual_aid_partnerships.append(source_project.project_id)
                    self._save_project(target_project)
                
            return {
                "success": True,
                "offer_id": offer_id,
                "message": f"Created mutual aid offer from {offer['source_id']} to {offer['target_id']}"
            }
            
        except Exception as e:
            logger.error(f"Error creating mutual aid offer: {e}")
            return {
                "success": False,
                "error": f"Offer creation error: {str(e)}"
            }
    
    def update_aid_offer_status(self, offer_id: str, new_status: str, note: str = None) -> Dict[str, Any]:
        """
        Update status of a mutual aid offer.
        
        Args:
            offer_id: Offer identifier
            new_status: New status
            note: Optional note
            
        Returns:
            Update result
        """
        # Check offer exists
        if offer_id not in self.aid_offers:
            return {
                "success": False,
                "error": "Offer not found"
            }
            
        try:
            offer = self.aid_offers[offer_id]
            
            # Validate status
            valid_statuses = ["offered", "accepted", "fulfilled", "declined"]
            if new_status not in valid_statuses:
                return {
                    "success": False,
                    "error": f"Invalid status: {new_status}"
                }
                
            # Update status
            old_status = offer.status
            offer.status = new_status
            
            # Add note to metadata if provided
            if note:
                if "status_notes" not in offer.metadata:
                    offer.metadata["status_notes"] = []
                    
                offer.metadata["status_notes"].append({
                    "timestamp": time.time(),
                    "from_status": old_status,
                    "to_status": new_status,
                    "note": note
                })
                
            # Save offer
            self._save_aid_offer(offer)
            
            return {
                "success": True,
                "offer_id": offer_id,
                "old_status": old_status,
                "new_status": new_status,
                "message": f"Updated offer status: {new_status}"
            }
            
        except Exception as e:
            logger.error(f"Error updating offer status: {e}")
            return {
                "success": False,
                "error": f"Status update error: {str(e)}"
            }
    
    def _calculate_project_match_score(self, relocator: HumanRelocator, project: RelocationProject) -> float:
        """
        Calculate match score between relocator and project.
        
        Args:
            relocator: Human relocator
            project: Relocation project
            
        Returns:
            Match score (0.0 to 1.0)
        """
        score_components = []
        
        # Region preference
        region_score = 0.0
        if project.target_region_id in relocator.preferred_regions:
            region_score = 1.0
        elif not relocator.preferred_regions:  # No preferences specified
            region_score = 0.5
        score_components.append(("region", region_score))
        
        # Skill needs
        skill_score = 0.0
        if project.skill_gaps:
            skill_matches = 0
            for skill, gap in project.skill_gaps.items():
                if gap > 0.2 and skill in relocator.skills and relocator.skills[skill] > 0.5:
                    skill_matches += 1
                    
            skill_score = min(1.0, skill_matches / max(1, len(project.skill_gaps.keys()) / 2))
        else:
            skill_score = 0.5  # Neutral if no gaps defined
            
        score_components.append(("skills", skill_score))
        
        # Community model preferences
        community_score = 0.5  # Neutral default
        if project.community_model_id and relocator.preferred_community_scale:
            community = self.designer.get_community(project.community_model_id)
            if community:
                scale_match = relocator.preferred_community_scale == community.scale
                focus_match = relocator.preferred_community_focus == community.focus if relocator.preferred_community_focus else False
                governance_match = relocator.preferred_governance == community.governance if relocator.preferred_governance else False
                
                matches = sum([scale_match, focus_match, governance_match])
                if relocator.preferred_community_focus and relocator.preferred_governance:
                    community_score = matches / 3.0
                elif relocator.preferred_community_focus or relocator.preferred_governance:
                    community_score = matches / 2.0
                else:
                    community_score = matches / 1.0
                    
        score_components.append(("community", community_score))
        
        # Timeline compatibility
        timeline_score = 0.5  # Neutral default
        if relocator.relocation_timeline_months is not None:
            # Calculate approx project timeline
            if project.projected_completion_date:
                project_months = (project.projected_completion_date - time.time()) / (30 * 24 * 3600)
                timeline_diff = abs(relocator.relocation_timeline_months - project_months)
                timeline_score = max(0.0, 1.0 - (timeline_diff / 24))  # Within 24 months
            else:
                timeline_score = 0.5  # Neutral if no project timeline
                
        score_components.append(("timeline", timeline_score))
        
        # Current participants and preferred scale
        scale_score = 0.5  # Neutral default
        if relocator.preferred_community_scale:
            # Determine ideal population ranges for scales
            scale_sizes = {
                CommunityScale.NEIGHBORHOOD: (50, 150),
                CommunityScale.VILLAGE: (150, 500),
                CommunityScale.TOWN: (500, 2000),
                CommunityScale.SMALL_CITY: (2000, 10000),
                CommunityScale.REGIONAL_HUB: (10000, 50000)
            }
            
            ideal_range = scale_sizes.get(relocator.preferred_community_scale, (100, 500))
            if project.target_population >= ideal_range[0] and project.target_population <= ideal_range[1]:
                scale_score = 1.0
            else:
                # Calculate distance from range
                if project.target_population < ideal_range[0]:
                    distance = ideal_range[0] - project.target_population
                    scale_score = max(0.0, 1.0 - (distance / ideal_range[0]))
                else:
                    distance = project.target_population - ideal_range[1]
                    scale_score = max(0.0, 1.0 - (distance / ideal_range[1]))
                    
        score_components.append(("scale", scale_score))
        
        # Calculate weighted score
        weights = {
            "region": 0.3,
            "skills": 0.25,
            "community": 0.2,
            "timeline": 0.15,
            "scale": 0.1
        }
        
        weighted_score = sum(score * weights[name] for name, score in score_components)
        
        return weighted_score
    
    def _update_project_skill_coverage(self, project: RelocationProject) -> None:
        """
        Update skill coverage and gaps for a project.
        
        Args:
            project: Project to update
        """
        # Define standard skill categories to track
        standard_skills = {skill.name.lower(): 0.0 for skill in SkillCategory}
        
        # Initialize coverage
        skill_coverage = standard_skills.copy()
        
        # Calculate coverage from participants
        for human_id in project.current_participants:
            if human_id in self.relocators:
                relocator = self.relocators[human_id]
                
                # Add skills
                for skill, level in relocator.skills.items():
                    skill_lower = skill.lower()
                    if skill_lower in skill_coverage:
                        skill_coverage[skill_lower] = max(skill_coverage[skill_lower], level)
                    else:
                        skill_coverage[skill_lower] = level
                        
        # Calculate gaps
        skill_gaps = {}
        for skill, coverage in skill_coverage.items():
            if coverage < 0.7:  # Less than 70% coverage is a gap
                skill_gaps[skill] = 1.0 - coverage
                
        # Update project
        project.skill_coverage = skill_coverage
        project.skill_gaps = skill_gaps


# ====================================================================
# 4. TOWN INTRANET AND LOCAL KNOWLEDGE BASE
# ====================================================================

class KnowledgeCategory(Enum):
    """Categories for town knowledge base."""
    TECHNICAL = auto()       # Technical documentation
    ECOLOGICAL = auto()      # Ecological knowledge
    GOVERNANCE = auto()      # Governance processes
    SKILL = auto()           # Skill tutorials
    CULTURAL = auto()        # Cultural information
    HEALTH = auto()          # Health and medical
    INFRASTRUCTURE = auto()  # Infrastructure documentation
    LOCAL = auto()           # Local area knowledge
    EDUCATIONAL = auto()     # Educational materials
    HISTORICAL = auto()      # Historical records


class ResourceType(Enum):
    """Types of resources in town intranet."""
    DOCUMENT = auto()        # Text document
    VIDEO = auto()           # Video file
    AUDIO = auto()           # Audio file
    IMAGE = auto()           # Image file
    DATABASE = auto()        # Database
    INTERACTIVE = auto()     # Interactive application
    COLLECTION = auto()      # Collection of other resources
    GUIDE = auto()           # Step-by-step guide
    TEMPLATE = auto()        # Template document
    SOFTWARE = auto()        # Software application


@dataclass
class KnowledgeResource:
    """Knowledge resource in town knowledge base."""
    resource_id: str
    title: str
    description: str
    category: KnowledgeCategory
    resource_type: ResourceType
    file_path: str
    creator_id: Optional[str] = None
    created_date: float = field(default_factory=time.time)
    last_updated_date: float = field(default_factory=time.time)
    tags: List[str] = field(default_factory=list)
    related_resources: List[str] = field(default_factory=list)
    permissions: Dict[str, Any] = field(default_factory=dict)
    version: str = "1.0"
    size_bytes: Optional[int] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TownService:
    """Service available in town intranet."""Zone.OCEANIC, ClimateZone.HUMID_SUBTROPICAL
                ],
                advantages=[
                    "Uses familiar construction methods",
                    "Can achieve high insulation values",
                    "Reduced thermal bridging",
                    "More efficient use of lumber",
                    "Faster construction than many natural building methods",
                    "Adaptable to many designs"
                ],
                disadvantages=[
                    "Higher embodied carbon than some natural methods",
                    "Requires sustainably harvested wood to be truly ecological",
                    "Less thermal mass than earth-based systems",
                    "Requires careful air sealing",
                    "Less durable than some masonry techniques"
                ]
            )
        ]
        
        # Add systems
        for system in default_systems:
            self.building_systems[system.system_id] = system
            self._save_building_system(system)
            
        logger.info(f"Initialized {len(default_systems)} default building systems")
    
    def _initialize_default_energy_systems(self) -> None:
        """Initialize default energy systems."""
        default_systems = [
            # Solar PV with Battery Storage
            EnergySystem(
                system_id="solar_battery",
                name="Solar PV with Battery Storage",
                description="Grid-independent solar photovoltaic system with battery storage for 24/7 power availability.",
                energy_type="solar",
                capacity_range_kw=(2.0, 30.0),
                storage_included=True,
                storage_capacity_kwh=20.0,
                typical_output_kwh_per_year=1500.0,  # Per kW of capacity
                lifespan_years=25,
                maintenance_level=3,
                upfront_cost_per_kw=2500.0,
                region_suitability=["southwest", "pacific_northwest", "great_lakes", "new_england", "ozarks", "northern_plains"],
                climate_suitability=[c for c in ClimateZone],  # All climates
                advantages=[
                    "No fuel required",
                    "Minimal maintenance",
                    "Scalable for different needs",
                    "Silent operation",
                    "Battery provides emergency backup",
                    "Can be grid-tied or independent"
                ],
                disadvantages=[
                    "Initial cost can be high",
                    "Dependent on solar resource",
                    "Requires periodic battery replacement",
                    "Efficiency decreases in very cloudy conditions",
                    "Seasonal output variation"
                ]
            ),
            
            # Small-Scale Wind
            EnergySystem(
                system_id="small_wind",
                name="Small-Scale Wind Turbine System",
                description="Wind energy system sized for community or neighborhood use, with battery storage.",
                energy_type="wind",
                capacity_range_kw=(5.0, 100.0),
                storage_included=True,
                storage_capacity_kwh=50.0,
                typical_output_kwh_per_year=2000.0,  # Per kW of capacity
                lifespan_years=20,
                maintenance_level=6,
                upfront_cost_per_kw=3000.0,
                region_suitability=["northern_plains", "great_lakes", "new_england"],
                climate_suitability=[
                    ClimateZone.CONTINENTAL_HOT, ClimateZone.CONTINENTAL_WARM, ClimateZone.CONTINENTAL_COOL,
                    ClimateZone.OCEANIC, ClimateZone.SUBARCTIC, ClimateZone.TUNDRA
                ],
                advantages=[
                    "Works during day and night",
                    "Complements solar in many regions",
                    "Higher output in winter (when solar is lower)",
                    "Can generate substantial power with good wind resource",
                    "Lower land use than solar for equivalent output"
                ],
                disadvantages=[
                    "Requires steady wind resource",
                    "More maintenance than solar",
                    "Moving parts require periodic replacement",
                    "Visual impact on landscape",
                    "Noise can be an issue for some designs"
                ]
            ),
            
            # Micro-Hydro
            EnergySystem(
                system_id="micro_hydro",
                name="Micro-Hydroelectric System",
                description="Small-scale hydroelectric generation using flowing water from streams or rivers, providing continuous power generation.",
                energy_type="hydro",
                capacity_range_kw=(1.0, 100.0),
                storage_included=False,
                storage_capacity_kwh=0.0,
                typical_output_kwh_per_year=8760.0,  # Per kW of capacity (24/7 operation)
                lifespan_years=30,
                maintenance_level=5,
                upfront_cost_per_kw=4000.0,
                region_suitability=["pacific_northwest", "new_england", "ozarks"],
                climate_suitability=[
                    ClimateZone.RAINFOREST, ClimateZone.MONSOON, ClimateZone.OCEANIC,
                    ClimateZone.CONTINENTAL_COOL, ClimateZone.HUMID_SUBTROPICAL
                ],
                advantages=[
                    "Continuous power generation (day and night)",
                    "Highly reliable and predictable",
                    "Long system lifespan",
                    "Low environmental impact when properly designed",
                    "High capacity factor compared to solar and wind",
                    "May not require battery storage"
                ],
                disadvantages=[
                    "Geographically limited to suitable water sources",
                    "Seasonal flow variations affect output",
                    "Requires water rights and permits",
                    "Intake systems require maintenance (debris clearing)",
                    "Environmental considerations for aquatic ecosystems"
                ]
            ),
            
            # Biogas Digester
            EnergySystem(
                system_id="biogas",
                name="Biogas Digestion System",
                description="Anaerobic digestion system that converts organic waste into biogas for cooking, heating, or electricity generation.",
                energy_type="biomass",
                capacity_range_kw=(5.0, 50.0),
                storage_included=True,
                storage_capacity_kwh=15.0,
                typical_output_kwh_per_year=6000.0,  # Per kW of capacity
                lifespan_years=20,
                maintenance_level=7,
                upfront_cost_per_kw=2000.0,
                region_suitability=["great_lakes", "ozarks", "new_england"],
                climate_suitability=[
                    ClimateZone.CONTINENTAL_HOT, ClimateZone.CONTINENTAL_WARM, ClimateZone.HUMID_SUBTROPICAL,
                    ClimateZone.OCEANIC
                ],
                advantages=[
                    "Uses waste materials as fuel",
                    "Produces fertilizer as byproduct",
                    "Can process agricultural and food waste",
                    "Reduces methane emissions from organic waste",
                    "Provides on-demand energy unlike solar/wind",
                    "Doesn't depend on weather conditions"
                ],
                disadvantages=[
                    "Requires regular feeding with organic material",
                    "More complex operation than solar",
                    "Temperature sensitive (less effective in cold climates without heating)",
                    "Requires management of digester biology",
                    "Needs adequate organic waste stream"
                ]
            ),
            
            # Geothermal Heat Pump
            EnergySystem(
                system_id="geothermal_heat",
                name="Geothermal Heat Pump System",
                description="Ground-source heat pump system for highly efficient heating and cooling using stable underground temperatures.",
                energy_type="geothermal",
                capacity_range_kw=(3.0, 30.0),
                storage_included=False,
                storage_capacity_kwh=0.0,
                typical_output_kwh_per_year=10000.0,  # Equivalent heat energy output
                lifespan_years=25,
                maintenance_level=4,
                upfront_cost_per_kw=5000.0,
                region_suitability=["great_lakes", "new_england", "northern_plains", "pacific_northwest"],
                climate_suitability=[
                    ClimateZone.CONTINENTAL_HOT, ClimateZone.CONTINENTAL_WARM, ClimateZone.CONTINENTAL_COOL,
                    Climate, '')) for req in hardware_requirements) if hardware_requirements else 0}-{sum(int(req['estimated_cost'].split('-')[1].replace('"""
GaiaBioregionalHarmony: Ecological Balance and Community Restoration Module
Version: 0.1 Alpha
Description: A Gaia-level implementation for the PulseHuman framework enabling
             bioregional rebalancing, collaborative relocation, and the creation
             of decentralized, ecologically harmonious communities connected
             through mutual aid networks.
"""

import os
import time
import logging
import asyncio
import json
import hashlib
import sqlite3
import math
import random
from typing import Dict, List, Tuple, Optional, Any, Union, Set, Callable
from dataclasses import dataclass, field
from enum import Enum, auto
from pathlib import Path

# Import from PulseHuman
from PulseHuman import (
    DevelopmentalStage, HumanDevelopmentalMode, DevelopmentalActivity,
    HumanDevelopmentalProgress, PulseHumanEngine, PulseHumanActivities
)

# Import from PulseEcoRecovery
from PulseEcoRecovery import (
    KnowledgeRepository, ResilienceBridgeCoordinator,
    ResilienceEducationModule, SystemsArchitectModule
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("gaia_bioregional")


# ====================================================================
# 1. BIOREGION MAPPING AND ANALYSIS
# ====================================================================

class ClimateZone(Enum):
    """Climate zones for bioregional mapping."""
    RAINFOREST = auto()      # Hot, wet year-round
    MONSOON = auto()         # Seasonal heavy rainfall
    SAVANNA = auto()         # Tropical wet and dry
    DESERT_HOT = auto()      # Hot, arid
    DESERT_COLD = auto()     # Cold, arid
    STEPPE_HOT = auto()      # Hot, semi-arid
    STEPPE_COLD = auto()     # Cold, semi-arid
    MEDITERRANEAN = auto()   # Hot dry summers, mild wet winters
    HUMID_SUBTROPICAL = auto() # Hot humid summers, mild winters
    OCEANIC = auto()         # Warm to cool, year-round precipitation
    CONTINENTAL_HOT = auto() # Hot summers, cold winters
    CONTINENTAL_WARM = auto() # Warm summers, cold winters
    CONTINENTAL_COOL = auto() # Cool summers, cold winters
    SUBARCTIC = auto()       # Short cool summers, very cold winters
    TUNDRA = auto()          # Very short cool summers, very cold winters
    POLAR_ICE = auto()       # Perpetual ice and snow
    MOUNTAIN = auto()        # Variable by elevation


class EcosystemType(Enum):
    """Major ecosystem types."""
    FOREST_TEMPERATE = auto()  # Temperate forest
    FOREST_TROPICAL = auto()   # Tropical forest
    FOREST_BOREAL = auto()     # Boreal/Taiga forest
    GRASSLAND = auto()         # Grasslands/Prairie/Savanna
    DESERT = auto()            # Desert ecosystems
    SHRUBLAND = auto()         # Chaparral/Shrubland
    TUNDRA = auto()            # Arctic/alpine tundra
    WETLAND = auto()           # Wetlands/Marshes/Swamps
    FRESHWATER = auto()        # Lakes/Rivers/Streams
    COASTAL = auto()           # Coastal ecosystems
    MARINE = auto()            # Marine ecosystems
    ALPINE = auto()            # Mountain ecosystems
    URBAN = auto()             # Urban ecosystems
    AGRICULTURAL = auto()      # Agricultural ecosystems


class WaterAvailability(Enum):
    """Water availability classification."""
    ABUNDANT = auto()        # Plentiful year-round surface and groundwater
    SUFFICIENT = auto()      # Adequate with proper management
    SEASONAL = auto()        # Abundant seasonally, limited other times
    STRESSED = auto()        # Currently adequate but facing stress
    SCARCE = auto()          # Limited availability, careful management required
    CRITICAL = auto()        # Severe shortage, urgent conservation needed


class SoilQuality(Enum):
    """Soil quality classification."""
    EXCELLENT = auto()       # Deep, fertile, well-structured
    GOOD = auto()            # Fertile with some limitations
    MODERATE = auto()        # Workable but needs amendments
    POOR = auto()            # Significant limitations
    DEGRADED = auto()        # Damaged by erosion/contamination


class InfrastructureStatus(Enum):
    """Infrastructure status classification."""
    MODERN = auto()          # Up-to-date, well-maintained
    ADEQUATE = auto()        # Functional but aging
    DEGRADED = auto()        # Partially functional, needs significant repair
    MINIMAL = auto()         # Basic infrastructure only
    ABSENT = auto()          # Little to no existing infrastructure


class PopulationDensity(Enum):
    """Population density classification."""
    URBAN_DENSE = auto()     # Dense city centers
    URBAN_MODERATE = auto()  # Urban but not dense
    SUBURBAN = auto()        # Suburban areas
    RURAL_DEVELOPED = auto() # Developed rural
    RURAL_SPARSE = auto()    # Sparsely populated
    WILDERNESS = auto()      # Virtually uninhabited


@dataclass
class BioregionMetrics:
    """Metrics for bioregional analysis."""
    climate_zone: ClimateZone
    ecosystem_types: List[EcosystemType]
    water_availability: WaterAvailability
    soil_quality: SoilQuality
    infrastructure_status: InfrastructureStatus
    population_density: PopulationDensity
    land_availability_acres: float
    climate_resilience_score: float  # 0-10 scale
    current_population: int
    optimal_population: int
    agricultural_capacity_people: int
    renewable_energy_potential: Dict[str, float]  # kWh/year by type
    ecological_health_score: float  # 0-10 scale
    natural_disaster_risk: Dict[str, float]  # Risk scores by disaster type


@dataclass
class USRegion:
    """US region for bioregional analysis."""
    region_id: str
    name: str
    states: List[str]
    major_cities: List[str]
    center_lat: float
    center_long: float
    area_sq_miles: float
    metrics: BioregionMetrics
    watersheds: List[str]
    key_resources: List[str]
    special_considerations: List[str]
    proposed_communities: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class HumanSkillProfile:
    """Profile of skills for bioregional matching."""
    skill_categories: Dict[str, float]  # Category -> proficiency level (0-1)
    career_experience: List[str]
    physical_capabilities: Dict[str, float]  # Capability -> level (0-1)
    climate_preferences: List[ClimateZone]
    community_role_preferences: List[str]
    relocation_readiness: float  # 0-1 scale
    requires_specialized_healthcare: bool
    dependent_family_members: int
    special_considerations: List[str]
    interests: List[str]


@dataclass
class RelocationMatch:
    """Match between human and bioregion for relocation."""
    human_id: str
    region_id: str
    community_id: Optional[str]
    compatibility_score: float  # 0-1 scale
    skill_match_score: float  # 0-1 scale
    climate_match_score: float  # 0-1 scale
    needs_match_score: float  # 0-1 scale
    role_recommendations: List[str]
    rationale: str
    suggested_preparation: List[str]


class BioregionalMapper:
    """
    Analyzes and maps bioregions for sustainable community development.
    """
    
    def __init__(self, data_path: str = "bioregional_data"):
        """
        Initialize bioregional mapper.
        
        Args:
            data_path: Path for storing bioregional data
        """
        self.data_path = data_path
        
        # Ensure paths exist
        os.makedirs(data_path, exist_ok=True)
        os.makedirs(os.path.join(data_path, "regions"), exist_ok=True)
        os.makedirs(os.path.join(data_path, "communities"), exist_ok=True)
        
        # Load US regions
        self.us_regions: Dict[str, USRegion] = {}
        self._load_us_regions()
        
        # Initialize with default regions if none exist
        if not self.us_regions:
            self._initialize_default_regions()
    
    def _load_us_regions(self) -> None:
        """Load US regions from disk."""
        try:
            # Load regions
            regions_dir = os.path.join(self.data_path, "regions")
            for filename in os.listdir(regions_dir):
                if filename.endswith(".json"):
                    file_path = os.path.join(regions_dir, filename)
                    try:
                        with open(file_path, "r") as f:
                            data = json.load(f)
                            
                            # Parse metrics
                            metrics_data = data.get("metrics", {})
                            metrics = BioregionMetrics(
                                climate_zone=ClimateZone[metrics_data.get("climate_zone", "CONTINENTAL_WARM")],
                                ecosystem_types=[EcosystemType[et] for et in metrics_data.get("ecosystem_types", ["FOREST_TEMPERATE"])],
                                water_availability=WaterAvailability[metrics_data.get("water_availability", "SUFFICIENT")],
                                soil_quality=SoilQuality[metrics_data.get("soil_quality", "MODERATE")],
                                infrastructure_status=InfrastructureStatus[metrics_data.get("infrastructure_status", "ADEQUATE")],
                                population_density=PopulationDensity[metrics_data.get("population_density", "RURAL_DEVELOPED")],
                                land_availability_acres=metrics_data.get("land_availability_acres", 0.0),
                                climate_resilience_score=metrics_data.get("climate_resilience_score", 5.0),
                                current_population=metrics_data.get("current_population", 0),
                                optimal_population=metrics_data.get("optimal_population", 0),
                                agricultural_capacity_people=metrics_data.get("agricultural_capacity_people", 0),
                                renewable_energy_potential=metrics_data.get("renewable_energy_potential", {}),
                                ecological_health_score=metrics_data.get("ecological_health_score", 5.0),
                                natural_disaster_risk=metrics_data.get("natural_disaster_risk", {})
                            )
                            
                            # Create region
                            region = USRegion(
                                region_id=data.get("region_id", filename.replace(".json", "")),
                                name=data.get("name", "Unknown Region"),
                                states=data.get("states", []),
                                major_cities=data.get("major_cities", []),
                                center_lat=data.get("center_lat", 0.0),
                                center_long=data.get("center_long", 0.0),
                                area_sq_miles=data.get("area_sq_miles", 0.0),
                                metrics=metrics,
                                watersheds=data.get("watersheds", []),
                                key_resources=data.get("key_resources", []),
                                special_considerations=data.get("special_considerations", []),
                                proposed_communities=data.get("proposed_communities", []),
                                metadata=data.get("metadata", {})
                            )
                            
                            self.us_regions[region.region_id] = region
                    except Exception as e:
                        logger.error(f"Error loading region from {file_path}: {e}")
                        
            logger.info(f"Loaded {len(self.us_regions)} US regions")
            
        except Exception as e:
            logger.error(f"Error loading US regions: {e}")
    
    def _save_region(self, region: USRegion) -> None:
        """Save region to disk."""
        try:
            file_path = os.path.join(self.data_path, "regions", f"{region.region_id}.json")
            
            # Convert metrics for JSON serialization
            metrics_data = {
                "climate_zone": region.metrics.climate_zone.name,
                "ecosystem_types": [et.name for et in region.metrics.ecosystem_types],
                "water_availability": region.metrics.water_availability.name,
                "soil_quality": region.metrics.soil_quality.name,
                "infrastructure_status": region.metrics.infrastructure_status.name,
                "population_density": region.metrics.population_density.name,
                "land_availability_acres": region.metrics.land_availability_acres,
                "climate_resilience_score": region.metrics.climate_resilience_score,
                "current_population": region.metrics.current_population,
                "optimal_population": region.metrics.optimal_population,
                "agricultural_capacity_people": region.metrics.agricultural_capacity_people,
                "renewable_energy_potential": region.metrics.renewable_energy_potential,
                "ecological_health_score": region.metrics.ecological_health_score,
                "natural_disaster_risk": region.metrics.natural_disaster_risk
            }
            
            # Prepare region data
            region_data = {
                "region_id": region.region_id,
                "name": region.name,
                "states": region.states,
                "major_cities": region.major_cities,
                "center_lat": region.center_lat,
                "center_long": region.center_long,
                "area_sq_miles": region.area_sq_miles,
                "metrics": metrics_data,
                "watersheds": region.watersheds,
                "key_resources": region.key_resources,
                "special_considerations": region.special_considerations,
                "proposed_communities": region.proposed_communities,
                "metadata": region.metadata
            }
            
            with open(file_path, "w") as f:
                json.dump(region_data, f, indent=2)
                
        except Exception as e:
            logger.error(f"Error saving region: {e}")
    
    def _initialize_default_regions(self) -> None:
        """Initialize default US bioregions."""
        default_regions = [
            # Pacific Northwest
            USRegion(
                region_id="pacific_northwest",
                name="Pacific Northwest",
                states=["Washington", "Oregon", "Idaho (western)"],
                major_cities=["Seattle", "Portland", "Spokane", "Eugene", "Olympia"],
                center_lat=47.7511,
                center_long=-120.7401,
                area_sq_miles=163000,
                metrics=BioregionMetrics(
                    climate_zone=ClimateZone.OCEANIC,
                    ecosystem_types=[EcosystemType.FOREST_TEMPERATE, EcosystemType.COASTAL, EcosystemType.ALPINE],
                    water_availability=WaterAvailability.ABUNDANT,
                    soil_quality=SoilQuality.GOOD,
                    infrastructure_status=InfrastructureStatus.MODERN,
                    population_density=PopulationDensity.RURAL_DEVELOPED,
                    land_availability_acres=15000000,
                    climate_resilience_score=7.5,
                    current_population=12000000,
                    optimal_population=15000000,
                    agricultural_capacity_people=20000000,
                    renewable_energy_potential={
                        "hydro": 72000000000,
                        "wind": 45000000000,
                        "solar": 18000000000,
                        "geothermal": 5000000000
                    },
                    ecological_health_score=8.0,
                    natural_disaster_risk={
                        "wildfire": 0.7,
                        "earthquake": 0.6,
                        "flooding": 0.5,
                        "volcanic": 0.3,
                        "drought": 0.3
                    }
                ),
                watersheds=["Columbia River Basin", "Puget Sound"],
                key_resources=["Timber", "Hydropower", "Fisheries", "Fertile valleys"],
                special_considerations=[
                    "Cascadia subduction zone earthquake risk",
                    "Increasing wildfire risk with climate change",
                    "Water abundance but seasonal drought in some areas"
                ]
            ),
            
            # Great Lakes
            USRegion(
                region_id="great_lakes",
                name="Great Lakes Bioregion",
                states=["Michigan", "Wisconsin", "Minnesota", "Illinois (northern)", "Indiana (northern)", "Ohio (northern)"],
                major_cities=["Chicago", "Detroit", "Milwaukee", "Cleveland", "Minneapolis"],
                center_lat=44.1347,
                center_long=-84.6035,
                area_sq_miles=176000,
                metrics=BioregionMetrics(
                    climate_zone=ClimateZone.CONTINENTAL_WARM,
                    ecosystem_types=[EcosystemType.FOREST_TEMPERATE, EcosystemType.FRESHWATER, EcosystemType.GRASSLAND],
                    water_availability=WaterAvailability.ABUNDANT,
                    soil_quality=SoilQuality.GOOD,
                    infrastructure_status=InfrastructureStatus.ADEQUATE,
                    population_density=PopulationDensity.SUBURBAN,
                    land_availability_acres=12000000,
                    climate_resilience_score=7.0,
                    current_population=40000000,
                    optimal_population=30000000,
                    agricultural_capacity_people=60000000,
                    renewable_energy_potential={
                        "wind": 85000000000,
                        "solar": 25000000000,
                        "hydro": 8000000000
                    },
                    ecological_health_score=6.0,
                    natural_disaster_risk={
                        "flooding": 0.5,
                        "blizzard": 0.7,
                        "tornado": 0.4,
                        "drought": 0.3
                    }
                ),
                watersheds=["Great Lakes Basin", "Mississippi River (Upper)"],
                key_resources=["Freshwater", "Fertile farmland", "Forests", "Minerals"],
                special_considerations=[
                    "20% of world's fresh surface water",
                    "Legacy industrial contamination in some areas",
                    "Climate change bringing increased precipitation",
                    "Invasive species challenges"
                ]
            ),
            
            # New England
            USRegion(
                region_id="new_england",
                name="New England",
                states=["Maine", "New Hampshire", "Vermont", "Massachusetts", "Connecticut", "Rhode Island"],
                major_cities=["Boston", "Providence", "Portland", "Burlington"],
                center_lat=43.6615,
                center_long=-70.9989,
                area_sq_miles=72000,
                metrics=BioregionMetrics(
                    climate_zone=ClimateZone.CONTINENTAL_COOL,
                    ecosystem_types=[EcosystemType.FOREST_TEMPERATE, EcosystemType.COASTAL, EcosystemType.FRESHWATER],
                    water_availability=WaterAvailability.SUFFICIENT,
                    soil_quality=SoilQuality.MODERATE,
                    infrastructure_status=InfrastructureStatus.ADEQUATE,
                    population_density=PopulationDensity.SUBURBAN,
                    land_availability_acres=8000000,
                    climate_resilience_score=6.5,
                    current_population=14700000,
                    optimal_population=12000000,
                    agricultural_capacity_people=5000000,
                    renewable_energy_potential={
                        "wind": 42000000000,
                        "solar": 18000000000,
                        "hydro": 6000000000,
                        "tidal": 3000000000
                    },
                    ecological_health_score=7.0,
                    natural_disaster_risk={
                        "blizzard": 0.8,
                        "hurricane": 0.5,
                        "flooding": 0.5,
                        "sea_level_rise": 0.6
                    }
                ),
                watersheds=["Connecticut River", "Merrimack River", "Penobscot River"],
                key_resources=["Forests", "Coastal fisheries", "Hydropower potential", "Cultural heritage"],
                special_considerations=[
                    "Aging infrastructure",
                    "Coastal vulnerability to sea level rise",
                    "Reforestation success story",
                    "Strong local governance traditions"
                ]
            ),
            
            # Ozarks
            USRegion(
                region_id="ozarks",
                name="Ozarks and Upper South",
                states=["Missouri", "Arkansas", "Kentucky", "Tennessee", "Oklahoma (eastern)"],
                major_cities=["Nashville", "Louisville", "Memphis", "Little Rock", "Springfield"],
                center_lat=36.7336,
                center_long=-91.1591,
                area_sq_miles=180000,
                metrics=BioregionMetrics(
                    climate_zone=ClimateZone.HUMID_SUBTROPICAL,
                    ecosystem_types=[EcosystemType.FOREST_TEMPERATE, EcosystemType.FRESHWATER, EcosystemType.GRASSLAND],
                    water_availability=WaterAvailability.SUFFICIENT,
                    soil_quality=SoilQuality.MODERATE,
                    infrastructure_status=InfrastructureStatus.ADEQUATE,
                    population_density=PopulationDensity.RURAL_DEVELOPED,
                    land_availability_acres=25000000,
                    climate_resilience_score=6.0,
                    current_population=18000000,
                    optimal_population=16000000,
                    agricultural_capacity_people=30000000,
                    renewable_energy_potential={
                        "solar": 40000000000,
                        "hydro": 15000000000,
                        "wind": 10000000000
                    },
                    ecological_health_score=6.5,
                    natural_disaster_risk={
                        "tornado": 0.7,
                        "flooding": 0.6,
                        "ice_storm": 0.5,
                        "drought": 0.4
                    }
                ),
                watersheds=["Mississippi River", "Ohio River", "White River", "Arkansas River"],
                key_resources=["Freshwater springs", "Hardwood forests", "Agricultural land", "Caves and karst systems"],
                special_considerations=[
                    "Rich cultural heritage",
                    "Karst topography with sensitive groundwater",
                    "Biodiversity hotspot",
                    "Climate warming may enhance growing season"
                ]
            ),
            
            # Southwest
            USRegion(
                region_id="southwest",
                name="Southwest Desert",
                states=["Arizona", "New Mexico", "Nevada", "Utah (southern)"],
                major_cities=["Phoenix", "Tucson", "Albuquerque", "Las Vegas"],
                center_lat=33.7712,
                center_long=-111.3877,
                area_sq_miles=250000,
                metrics=BioregionMetrics(
                    climate_zone=ClimateZone.DESERT_HOT,
                    ecosystem_types=[EcosystemType.DESERT, EcosystemType.SHRUBLAND, EcosystemType.ALPINE],
                    water_availability=WaterAvailability.CRITICAL,
                    soil_quality=SoilQuality.POOR,
                    infrastructure_status=InfrastructureStatus.ADEQUATE,
                    population_density=PopulationDensity.RURAL_SPARSE,
                    land_availability_acres=75000000,
                    climate_resilience_score=3.5,
                    current_population=18000000,
                    optimal_population=5000000,
                    agricultural_capacity_people=2000000,
                    renewable_energy_potential={
                        "solar": 175000000000,
                        "wind": 30000000000,
                        "geothermal": 10000000000
                    },
                    ecological_health_score=4.5,
                    natural_disaster_risk={
                        "drought": 0.9,
                        "heat": 0.9,
                        "wildfire": 0.7,
                        "flash_flood": 0.6
                    }
                ),
                watersheds=["Colorado River", "Rio Grande", "Gila River"],
                key_resources=["Solar potential", "Minerals", "Indigenous cultural sites", "Desert biodiversity"],
                special_considerations=[
                    "Extreme water scarcity worsening with climate change",
                    "Current population exceeds ecological carrying capacity",
                    "Exceptional solar energy potential",
                    "Fragile desert ecosystems"
                ]
            ),
            
            # Northern Plains
            USRegion(
                region_id="northern_plains",
                name="Northern Plains",
                states=["North Dakota", "South Dakota", "Nebraska", "Montana (eastern)", "Wyoming (eastern)"],
                major_cities=["Omaha", "Lincoln", "Sioux Falls", "Fargo", "Billings"],
                center_lat=44.7237,
                center_long=-100.5547,
                area_sq_miles=355000,
                metrics=BioregionMetrics(
                    climate_zone=ClimateZone.CONTINENTAL_COOL,
                    ecosystem_types=[EcosystemType.GRASSLAND, EcosystemType.FRESHWATER, EcosystemType.AGRICULTURAL],
                    water_availability=WaterAvailability.STRESSED,
                    soil_quality=SoilQuality.EXCELLENT,
                    infrastructure_status=InfrastructureStatus.ADEQUATE,
                    population_density=PopulationDensity.RURAL_SPARSE,
                    land_availability_acres=150000000,
                    climate_resilience_score=5.0,
                    current_population=5000000,
                    optimal_population=9000000,
                    agricultural_capacity_people=80000000,
                    renewable_energy_potential={
                        "wind": 200000000000,
                        "solar": 40000000000,
                        "hydro": 5000000000
                    },
                    ecological_health_score=5.0,
                    natural_disaster_risk={
                        "drought": 0.6,
                        "blizzard": 0.8,
                        "tornado": 0.6,
                        "flooding": 0.5
                    }
                ),
                watersheds=["Missouri River", "Platte River", "Yellowstone River"],
                key_resources=["Fertile farmland", "Grasslands", "Wind potential", "Fossil fuels"],
                special_considerations=[
                    "Depopulating rural areas",
                    "World-class soil for agriculture",
                    "Exceptional wind energy potential",
                    "Climate change bringing more extreme precipitation patterns"
                ]
            )
        ]
        
        # Add regions
        for region in default_regions:
            self.us_regions[region.region_id] = region
            self._save_region(region)
            
        logger.info(f"Initialized {len(default_regions)} default US bioregions")
    
    def get_region(self, region_id: str) -> Optional[USRegion]:
        """
        Get a US bioregion by ID.
        
        Args:
            region_id: Region identifier
            
        Returns:
            Region if found, None otherwise
        """
        return self.us_regions.get(region_id)
    
    def get_all_regions(self) -> List[USRegion]:
        """
        Get all US bioregions.
        
        Returns:
            List of regions
        """
        return list(self.us_regions.values())
    
    def add_region(self, region: USRegion) -> bool:
        """
        Add a new US bioregion.
        
        Args:
            region: Region to add
            
        Returns:
            Success status
        """
        # Check if already exists
        if region.region_id in self.us_regions:
            return False
            
        # Add region
        self.us_regions[region.region_id] = region
        
        # Save to disk
        self._save_region(region)
        
        return True
    
    def update_region(self, region: USRegion) -> bool:
        """
        Update an existing US bioregion.
        
        Args:
            region: Region to update
            
        Returns:
            Success status
        """
        # Check if exists
        if region.region_id not in self.us_regions:
            return False
            
        # Update region
        self.us_regions[region.region_id] = region
        
        # Save to disk
        self._save_region(region)
        
        return True
    
    def find_regions_by_criteria(self, 
                              water_min: WaterAvailability = None,
                              climate_zones: List[ClimateZone] = None,
                              soil_min: SoilQuality = None,
                              population_density: List[PopulationDensity] = None,
                              climate_resilience_min: float = None) -> List[USRegion]:
        """
        Find regions matching specified criteria.
        
        Args:
            water_min: Minimum water availability
            climate_zones: Acceptable climate zones
            soil_min: Minimum soil quality
            population_density: Acceptable population densities
            climate_resilience_min: Minimum climate resilience score
            
        Returns:
            List of matching regions
        """
        matching_regions = []
        
        for region in self.us_regions.values():
            # Check water availability
            if water_min and region.metrics.water_availability.value < water_min.value:
                continue
                
            # Check climate zones
            if climate_zones and region.metrics.climate_zone not in climate_zones:
                continue
                
            # Check soil quality
            if soil_min and region.metrics.soil_quality.value < soil_min.value:
                continue
                
            # Check population density
            if population_density and region.metrics.population_density not in population_density:
                continue
                
            # Check climate resilience
            if climate_resilience_min and region.metrics.climate_resilience_score < climate_resilience_min:
                continue
                
            # All criteria matched
            matching_regions.append(region)
            
        return matching_regions
    
    def calculate_optimal_distribution(self) -> Dict[str, Any]:
        """
        Calculate optimal population distribution across bioregions.
        
        Returns:
            Optimal distribution information
        """
        # Get total current population and capacity
        total_current = sum(region.metrics.current_population for region in self.us_regions.values())
        total_optimal = sum(region.metrics.optimal_population for region in self.us_regions.values())
        total_agricultural_capacity = sum(region.metrics.agricultural_capacity_people for region in self.us_regions.values())
        
        # Calculate distribution
        distribution = {}
        surpluses = []
        deficits = []
        
        for region in self.us_regions.values():
            current = region.metrics.current_population
            optimal = region.metrics.optimal_population
            difference = optimal - current
            
            # Record distribution
            distribution[region.region_id] = {
                "name": region.name,
                "current_population": current,
                "optimal_population": optimal,
                "difference": difference,
                "agricultural_capacity": region.metrics.agricultural_capacity_people,
                "water_availability": region.metrics.water_availability.name,
                "climate_resilience": region.metrics.climate_resilience_score
            }
            
            # Track surpluses and deficits
            if difference > 0:
                deficits.append((region.region_id, difference))
            elif difference < 0:
                surpluses.append((region.region_id, -difference))
        
        # Sort surpluses and deficits by magnitude
        surpluses.sort(key=lambda x: x[1], reverse=True)
        deficits.sort(key=lambda x: x[1], reverse=True)
        
        return {
            "total_current_population": total_current,
            "total_optimal_population": total_optimal,
            "total_agricultural_capacity": total_agricultural_capacity,
            "distribution_by_region": distribution,
            "surplus_regions": surpluses,
            "deficit_regions": deficits
        }
    
    def get_region_compatibility_score(self, human_profile: HumanSkillProfile, region_id: str) -> Dict[str, Any]:
        """
        Calculate compatibility score between a human profile and a bioregion.
        
        Args:
            human_profile: Human skill profile
            region_id: Region identifier
            
        Returns:
            Compatibility assessment
        """
        # Get region
        region = self.us_regions.get(region_id)
        if not region:
            return {
                "success": False,
                "error": f"Region not found: {region_id}"
            }
            
        # Calculate climate match
        climate_match = 0.0
        if region.metrics.climate_zone in human_profile.climate_preferences:
            climate_match = 1.0
        else:
            # Partial matching based on similar climate groups
            for preferred in human_profile.climate_preferences:
                if self._are_climates_similar(preferred, region.metrics.climate_zone):
                    climate_match = 0.5
                    break
        
        # Calculate skill match
        skill_match = 0.0
        needed_skills = self._get_region_needed_skills(region)
        
        for category, importance in needed_skills.items():
            if category in human_profile.skill_categories:
                skill_match += importance * human_profile.skill_categories[category]
                
        # Normalize skill match
        if needed_skills:
            skill_match /= sum(needed_skills.values())
        
        # Calculate needs match (healthcare, family needs, etc.)
        needs_match = 1.0
        
        # Adjust for specialized healthcare
        if human_profile.requires_specialized_healthcare and region.metrics.infrastructure_status.value < InfrastructureStatus.ADEQUATE.value:
            needs_match *= 0.5
            
        # Adjust for family members
        if human_profile.dependent_family_members > 0:
            # Check for educational infrastructure, family services, etc.
            if region.metrics.infrastructure_status.value < InfrastructureStatus.ADEQUATE.value:
                needs_match *= 0.7
        
        # Calculate overall compatibility
        compatibility = (climate_match * 0.3) + (skill_match * 0.4) + (needs_match * 0.3)
        
        # Generate role recommendations
        role_recommendations = self._generate_role_recommendations(human_profile, region)
        
        # Generate rationale
        rationale = self._generate_compatibility_rationale(
            human_profile, region, climate_match, skill_match, needs_match
        )
        
        # Generate suggested preparation
        suggested_preparation = self._generate_preparation_suggestions(human_profile, region)
        
        return {
            "success": True,
            "region_id": region_id,
            "region_name": region.name,
            "compatibility_score": compatibility,
            "climate_match_score": climate_match,
            "skill_match_score": skill_match,
            "needs_match_score": needs_match,
            "role_recommendations": role_recommendations,
            "rationale": rationale,
            "suggested_preparation": suggested_preparation
        }
    
    def _are_climates_similar(self, climate1: ClimateZone, climate2: ClimateZone) -> bool:
        """
        Check if two climate zones are similar.
        
        Args:
            climate1: First climate zone
            climate2: Second climate zone
            
        Returns:
            Whether climates are similar
        """
        # Define climate zone groups
        continental_group = {
            ClimateZone.CONTINENTAL_HOT,
            ClimateZone.CONTINENTAL_WARM,
            ClimateZone.CONTINENTAL_COOL
        }
        
        desert_group = {
            ClimateZone.DESERT_HOT,
            ClimateZone.DESERT_COLD,
            ClimateZone.STEPPE_HOT,
            ClimateZone.STEPPE_COLD
        }
        
        tropical_group = {
            ClimateZone.RAINFOREST,
            ClimateZone.MONSOON,
            ClimateZone.SAVANNA
        }
        
        temperate_group = {
            ClimateZone.MEDITERRANEAN,
            ClimateZone.HUMID_SUBTROPICAL,
            ClimateZone.OCEANIC
        }
        
        cold_group = {
            ClimateZone.SUBARCTIC,
            ClimateZone.TUNDRA,
            ClimateZone.POLAR_ICE
        }
        
        # Check if climates are in the same group
        for group in [continental_group, desert_group, tropical_group, temperate_group, cold_group]:
            if climate1 in group and climate2 in group:
                return True
                
        return False
    
    def _get_region_needed_skills(self, region: USRegion) -> Dict[str, float]:
        """
        Determine skills needed in a region.
        
        Args:
            region: Region to analyze
            
        Returns:
            Dictionary of skill categories and their importance (0-1)
        """
        needed_skills = {}
        
        # Agricultural skills
        if region.metrics.agricultural_capacity_people > 0:
            importance = min(1.0, region.metrics.agricultural_capacity_people / (region.metrics.optimal_population * 0.5))
            needed_skills["agriculture"] = importance
        
        # Water management skills
        if region.metrics.water_availability.value <= WaterAvailability.SUFFICIENT.value:
            water_importance = 1.0 - (region.metrics.water_availability.value / WaterAvailability.ABUNDANT.value)
            needed_skills["water_management"] = water_importance
        
        # Infrastructure skills
        if region.metrics.infrastructure_status.value < InfrastructureStatus.MODERN.value:
            infra_importance = 1.0 - (region.metrics.infrastructure_status.value / InfrastructureStatus.MODERN.value)
            needed_skills["infrastructure"] = infra_importance
            
        # Renewable energy skills
        if sum(region.metrics.renewable_energy_potential.values()) > 0:
            energy_importance = min(1.0, sum(region.metrics.renewable_energy_potential.values()) / (10000000000 * len(region.metrics.renewable_energy_potential)))
            needed_skills["renewable_energy"] = energy_importance
            
        # Conservation/restoration skills
        if region.metrics.ecological_health_score < 7.0:
            eco_importance = 1.0 - (region.metrics.ecological_health_score / 10.0)
            needed_skills["conservation"] = eco_importance
            
        # Healthcare skills
        healthcare_importance = 0.8  # Always needed
        needed_skills["healthcare"] = healthcare_importance
        
        # Education skills
        education_importance = 0.8  # Always needed
        needed_skills["education"] = education_importance
        
        # Disaster preparedness skills
        if any(risk > 0.5 for risk in region.metrics.natural_disaster_risk.values()):
            disaster_importance = max(region.metrics.natural_disaster_risk.values())
            needed_skills["disaster_preparedness"] = disaster_importance
            
        return needed_skills
    
    def _generate_role_recommendations(self, profile: HumanSkillProfile, region: USRegion) -> List[str]:
        """
        Generate role recommendations based on profile and region.
        
        Args:
            profile: Human skill profile
            region: Region for potential relocation
            
        Returns:
            List of recommended roles
        """
        recommendations = []
        
        # Match career experience to regional needs
        region_needs = self._get_region_needed_skills(region)
        
        # Agriculture roles
        if "agriculture" in region_needs and any(ag_term in job.lower() for job in profile.career_experience for ag_term in ["farm", "garden", "crop", "agriculture", "food", "harvest"]):
            recommendations.append("Sustainable Agriculture Specialist")
            
        # Water management roles
        if "water_management" in region_needs and any(water_term in job.lower() for job in profile.career_experience for water_term in ["water", "hydrology", "irrigation", "plumbing"]):
            recommendations.append("Water Systems Coordinator")
            
        # Infrastructure roles
        if "infrastructure" in region_needs and any(infra_term in job.lower() for job in profile.career_experience for infra_term in ["construction", "builder", "engineer", "architect", "electrician", "carpenter"]):
            recommendations.append("Sustainable Infrastructure Developer")
            
        # Energy roles
        if "renewable_energy" in region_needs and any(energy_term in job.lower() for job in profile.career_experience for energy_term in ["energy", "solar", "wind", "electric", "power"]):
            recommendations.append("Renewable Energy Specialist")
            
        # Conservation roles
        if "conservation" in region_needs and any(eco_term in job.lower() for job in profile.career_experience for eco_term in ["ecology", "conservation", "environment", "biology", "forest"]):
            recommendations.append("Ecological Restoration Coordinator")
            
        # Healthcare roles
        if "healthcare" in region_needs and any(health_term in job.lower() for job in profile.career_experience for health_term in ["health", "medical", "doctor", "nurse", "therapist", "care"]):
            recommendations.append("Community Health Practitioner")
            
        # Education roles
        if "education" in region_needs and any(edu_term in job.lower() for job in profile.career_experience for edu_term in ["teach", "education", "school", "instructor", "professor", "training"]):
            recommendations.append("Educational Program Developer")
            
        # Disaster preparedness roles
        if "disaster_preparedness" in region_needs and any(disaster_term in job.lower() for job in profile.career_experience for disaster_term in ["emergency", "disaster", "safety", "rescue", "response"]):
            recommendations.append("Disaster Preparedness Coordinator")
            
        # Community roles
        if any(community_term in profile.interests for community_term in ["community", "governance", "organizing", "social", "leadership"]):
            recommendations.append("Community Integration Facilitator")
            
        # Add preferred roles based on profile
        for role in profile.community_role_preferences:
            if role not in recommendations:
                recommendations.append(role)
                
        return recommendations[:3]  # Limit to top 3 recommendations
    
    def _generate_compatibility_rationale(self, 
                                       profile: HumanSkillProfile, 
                                       region: USRegion,
                                       climate_match: float,
                                       skill_match: float,
                                       needs_match: float) -> str:
        """
        Generate a rationale for the compatibility assessment.
        
        Args:
            profile: Human skill profile
            region: Region being assessed
            climate_match: Climate match score
            skill_match: Skill match score
            needs_match: Needs match score
            
        Returns:
            Compatibility rationale
        """
        rationale_parts = []
        
        # Climate rationale
        if climate_match > 0.8:
            rationale_parts.append(f"The {region.metrics.climate_zone.name.replace('_', ' ').lower()} climate of {region.name} aligns well with your preferences.")
        elif climate_match > 0.4:
            rationale_parts.append(f"The {region.metrics.climate_zone.name.replace('_', ' ').lower()} climate of {region.name} is somewhat similar to your preferred climates.")
        else:
            rationale_parts.append(f"The climate of {region.name} differs from your stated preferences, which may require adjustment.")
            
        # Skills rationale
        if skill_match > 0.7:
            rationale_parts.append(f"Your skills in {', '.join(list(profile.skill_categories.keys())[:2])} are highly valuable in this region.")
        elif skill_match > 0.4:
            rationale_parts.append(f"Some of your skills would be useful in this region, though additional training might be beneficial.")
        else:
            rationale_parts.append("Your current skill set may need significant expansion to meet the region's needs.")
            
        # Needs rationale
        if needs_match > 0.8:
            rationale_parts.append("The region can likely meet your personal and family needs effectively.")
        elif needs_match > 0.4:
            rationale_parts.append("The region may meet most of your needs, with some limitations.")
        else:
            rationale_parts.append("The region has significant limitations in meeting your specific needs.")
            
        # Add regional highlights
        if region.metrics.water_availability.value >= WaterAvailability.SUFFICIENT.value:
            rationale_parts.append(f"Water availability is {region.metrics.water_availability.name.lower()}, which is a critical resource advantage.")
            
        if region.metrics.climate_resilience_score > 6.0:
            rationale_parts.append(f"This region has above-average climate resilience ({region.metrics.climate_resilience_score}/10).")
            
        if region.metrics.agricultural_capacity_people > region.metrics.optimal_population:
            rationale_parts.append("The region has excellent agricultural potential, capable of producing surplus food.")
            
        return " ".join(rationale_parts)
    
    def _generate_preparation_suggestions(self, profile: HumanSkillProfile, region: USRegion) -> List[str]:
        """
        Generate suggestions for preparation before relocation.
        
        Args:
            profile: Human skill profile
            region: Region for potential relocation
            
        Returns:
            List of preparation suggestions
        """
        suggestions = []
        
        # Skill development suggestions
        region_needs = self._get_region_needed_skills(region)
        missing_skills = [skill for skill, importance in region_needs.items() 
                        if importance > 0.5 and (skill not in profile.skill_categories or profile.skill_categories.get(skill, 0) < 0.5)]
        
        if missing_skills:
            skill_suggestion = f"Develop skills in {', '.join(missing_skills[:2])}"
            if len(missing_skills) > 2:
                skill_suggestion += f", and {missing_skills[2]}"
            suggestions.append(skill_suggestion)
            
        # Climate adaptation suggestions
        if region.metrics.climate_zone not in profile.climate_preferences:
            suggestions.append(f"Research and prepare for adapting to {region.metrics.climate_zone.name.replace('_', ' ').lower()} climate conditions")
            
        # Healthcare suggestions
        if profile.requires_specialized_healthcare and region.metrics.infrastructure_status.value < InfrastructureStatus.MODERN.value:
            suggestions.append("Research healthcare options and establish connections with medical providers before relocating")
            
        # Disaster preparedness
        high_risks = [disaster for disaster, risk in region.metrics.natural_disaster_risk.items() if risk > 0.6]
        if high_risks:
            suggestions.append(f"Develop preparedness plans for {', '.join(high_risks)} risks in this region")
            
        # Water management
        if region.metrics.water_availability.value <= WaterAvailability.STRESSED.value:
            suggestions.append("Learn water conservation techniques and rainwater harvesting appropriate for this region")
            
        # Energy systems
        top_energy = max(region.metrics.renewable_energy_potential.items(), key=lambda x: x[1], default=(None, 0))
        if top_energy[0]:
            suggestions.append(f"Familiarize yourself with {top_energy[0]} energy systems, which have significant potential in this region")
            
        # Community integration
        if "community" in region.name.lower() or region.metrics.population_density.value <= PopulationDensity.RURAL_DEVELOPED.value:
            suggestions.append("Connect with existing communities in the region to understand local customs and practices")
            
        return suggestions
    
    def recommend_relocation_matches(self, 
                                  human_profile: HumanSkillProfile,
                                  match_count: int = 3) -> List[Dict[str, Any]]:
        """
        Recommend bioregions for relocation based on human profile.
        
        Args:
            human_profile: Human skill profile
            match_count: Number of matches to return
            
        Returns:
            List of recommended matches
        """
        matches = []
        
        # Score all regions
        for region in self.us_regions.values():
            compatibility = self.get_region_compatibility_score(human_profile, region.region_id)
            
            if compatibility["success"]:
                matches.append(compatibility)
                
        # Sort by compatibility score
        matches.sort(key=lambda x: x["compatibility_score"], reverse=True)
        
        # Return top matches
        return matches[:match_count]


# ====================================================================
# 2. SUSTAINABLE COMMUNITY DESIGN
# ====================================================================

class CommunityScale(Enum):
    """Scale of sustainable community."""
    NEIGHBORHOOD = auto()   # 50-150 people
    VILLAGE = auto()        # 150-500 people
    TOWN = auto()           # 500-2000 people
    SMALL_CITY = auto()     # 2000-10000 people
    REGIONAL_HUB = auto()   # 10000+ people


class CommunityFocus(Enum):
    """Primary focus of community."""
    AGRICULTURAL = auto()   # Farming/food production
    ECOLOGICAL = auto()     # Ecosystem restoration/preservation
    EDUCATIONAL = auto()    # Knowledge/learning center
    MANUFACTURING = auto()  # Local production/maker
    MIXED_USE = auto()      # Balanced approach
    ENERGY = auto()         # Renewable energy production
    CULTURAL = auto()       # Arts and culture center
    TECHNOLOGICAL = auto()  # Tech development/innovation


class GovernanceModel(Enum):
    """Governance models for communities."""
    CONSENSUS = auto()      # Consensus-based decision making
    SOCIOCRACY = auto()     # Sociocratic circles
    REPRESENTATIVE = auto() # Elected representatives
    DIRECT_DEMOCRACY = auto() # Direct voting
    COUNCIL = auto()        # Council of stakeholders
    STEWARDSHIP = auto()    # Stewardship-based governance


@dataclass
class BuildingSystem:
    """Sustainable building system."""
    system_id: str
    name: str
    description: str
    primary_materials: List[str]
    skill_level_required: int  # 1-10 scale
    durability_years: int
    insulation_value: float  # R-value
    embodied_carbon: float  # kg CO2e/m²
    cost_per_sqm: float
    region_suitability: List[str]  # Region IDs
    climate_suitability: List[ClimateZone]
    advantages: List[str]
    disadvantages: List[str]
    construction_guide_url: Optional[str] = None
    images_urls: List[str] = field(default_factory=list)


@dataclass
class EnergySystem:
    """Sustainable energy system."""
    system_id: str
    name: str
    description: str
    energy_type: str  # solar, wind, hydro, biomass, geothermal
    capacity_range_kw: Tuple[float, float]
    storage_included: bool
    storage_capacity_kwh: float
    typical_output_kwh_per_year: float
    lifespan_years: int
    maintenance_level: int  # 1-10 scale
    upfront_cost_per_kw: float
    region_suitability: List[str]  # Region IDs
    climate_suitability: List[ClimateZone]
    advantages: List[str]
    disadvantages: List[str]
    installation_guide_url: Optional[str] = None
    images_urls: List[str] = field(default_factory=list)


@dataclass
class WaterSystem:
    """Sustainable water system."""
    system_id: str
    name: str
    description: str
    water_source: str  # rain, ground, surface, municipal
    collection_capacity_liters: float
    treatment_method: str
    treatment_capacity_liters_per_day: float
    energy_required_kwh_per_day: float
    lifespan_years: int
    maintenance_level: int  # 1-10 scale
    upfront_cost: float
    region_suitability: List[str]  # Region IDs
    climate_suitability: List[ClimateZone]
    advantages: List[str]
    disadvantages: List[str]
    installation_guide_url: Optional[str] = None
    images_urls: List[str] = field(default_factory=list)


@dataclass
class FoodSystem:
    """Sustainable food production system."""
    system_id: str
    name: str
    description: str
    production_type: str  # garden, farm, aquaponics, etc.
    area_required_sqm: float
    water_required_liters_per_day: float
    typical_yield_calories_per_sqm: float
    typical_yield_kg_per_sqm: float
    personnel_required_per_hectare: float
    energy_required_kwh_per_day: float
    setup_time_months: int
    region_suitability: List[str]  # Region IDs
    climate_suitability: List[ClimateZone]
    advantages: List[str]
    disadvantages: List[str]
    implementation_guide_url: Optional[str] = None
    images_urls: List[str] = field(default_factory=list)


@dataclass
class Community:
    """Sustainable community design."""
    community_id: str
    name: str
    region_id: str
    scale: CommunityScale
    focus: CommunityFocus
    governance: GovernanceModel
    description: str
    target_population: int
    land_area_acres: float
    bioregion_features: List[str]
    building_systems: List[str]  # Building system IDs
    energy_systems: List[str]  # Energy system IDs
    water_systems: List[str]  # Water system IDs
    food_systems: List[str]  # Food system IDs
    skill_requirements: Dict[str, int]  # Skill category -> count needed
    development_phases: List[Dict[str, Any]]
    special_features: List[str]
    estimated_implementation_cost: float
    estimated_annual_operating_cost: float
    mutual_aid_connections: List[str]  # Other community IDs
    metadata: Dict[str, Any] = field(default_factory=dict)


class SustainableCommunityDesigner:
    """
    Designs sustainable communities based on bioregion characteristics.
    """
    
    def __init__(self, 
                bioregional_mapper: BioregionalMapper,
                data_path: str = "community_data"):
        """
        Initialize sustainable community designer.
        
        Args:
            bioregional_mapper: Bioregional mapper
            data_path: Path for storing community data
        """
        self.mapper = bioregional_mapper
        self.data_path = data_path
        
        # Ensure paths exist
        os.makedirs(data_path, exist_ok=True)
        os.makedirs(os.path.join(data_path, "communities"), exist_ok=True)
        os.makedirs(os.path.join(data_path, "building_systems"), exist_ok=True)
        os.makedirs(os.path.join(data_path, "energy_systems"), exist_ok=True)
        os.makedirs(os.path.join(data_path, "water_systems"), exist_ok=True)
        os.makedirs(os.path.join(data_path, "food_systems"), exist_ok=True)
        
        # Load systems and communities
        self.building_systems: Dict[str, BuildingSystem] = {}
        self.energy_systems: Dict[str, EnergySystem] = {}
        self.water_systems: Dict[str, WaterSystem] = {}
        self.food_systems: Dict[str, FoodSystem] = {}
        self.communities: Dict[str, Community] = {}
        
        self._load_systems()
        self._load_communities()
        
        # Initialize with default systems if none exist
        if not self.building_systems:
            self._initialize_default_building_systems()
        if not self.energy_systems:
            self._initialize_default_energy_systems()
        if not self.water_systems:
            self._initialize_default_water_systems()
        if not self.food_systems:
            self._initialize_default_food_systems()
            
        # Initialize default community templates
        if not self.communities:
            self._initialize_default_communities()
    
    def _load_systems(self) -> None:
        """Load sustainable systems from disk."""
        try:
            # Load building systems
            building_dir = os.path.join(self.data_path, "building_systems")
            for filename in os.listdir(building_dir):
                if filename.endswith(".json"):
                    file_path = os.path.join(building_dir, filename)
                    try:
                        with open(file_path, "r") as f:
                            data = json.load(f)
                            system = BuildingSystem(
                                system_id=data.get("system_id", filename.replace(".json", "")),
                                name=data.get("name", "Unknown Building System"),
                                description=data.get("description", ""),
                                primary_materials=data.get("primary_materials", []),
                                skill_level_required=data.get("skill_level_required", 5),
                                durability_years=data.get("durability_years", 50),
                                insulation_value=data.get("insulation_value", 0.0),
                                embodied_carbon=data.get("embodied_carbon", 0.0),
                                cost_per_sqm=data.get("cost_per_sqm", 0.0),
                                region_suitability=data.get("region_suitability", []),
                                climate_suitability=[ClimateZone[c] for c in data.get("climate_suitability", [])],
                                advantages=data.get("advantages", []),
                                disadvantages=data.get("disadvantages", []),
                                construction_guide_url=data.get("construction_guide_url"),
                                images_urls=data.get("images_urls", [])
                            )
                            self.building_systems[system.system_id] = system
                    except Exception as e:
                        logger.error(f"Error loading building system from {file_path}: {e}")
                        
            # Load energy systems
            energy_dir = os.path.join(self.data_path, "energy_systems")
            for filename in os.listdir(energy_dir):
                if filename.endswith(".json"):
                    file_path = os.path.join(energy_dir, filename)
                    try:
                        with open(file_path, "r") as f:
                            data = json.load(f)
                            system = EnergySystem(
                                system_id=data.get("system_id", filename.replace(".json", "")),
                                name=data.get("name", "Unknown Energy System"),
                                description=data.get("description", ""),
                                energy_type=data.get("energy_type", ""),
                                capacity_range_kw=tuple(data.get("capacity_range_kw", [0, 0])),
                                storage_included=data.get("storage_included", False),
                                storage_capacity_kwh=data.get("storage_capacity_kwh", 0.0),
                                typical_output_kwh_per_year=data.get("typical_output_kwh_per_year", 0.0),
                                lifespan_years=data.get("lifespan_years", 20),
                                maintenance_level=data.get("maintenance_level", 5),
                                upfront_cost_per_kw=data.get("upfront_cost_per_kw", 0.0),
                                region_suitability=data.get("region_suitability", []),
                                climate_suitability=[ClimateZone[c] for c in data.get("climate_suitability", [])],
                                advantages=data.get("advantages", []),
                                disadvantages=data.get("disadvantages", []),
                                installation_guide_url=data.get("installation_guide_url"),
                                images_urls=data.get("images_urls", [])
                            )
                            self.energy_systems[system.system_id] = system
                    except Exception as e:
                        logger.error(f"Error loading energy system from {file_path}: {e}")
                        
            # Load water systems
            water_dir = os.path.join(self.data_path, "water_systems")
            for filename in os.listdir(water_dir):
                if filename.endswith(".json"):
                    file_path = os.path.join(water_dir, filename)
                    try:
                        with open(file_path, "r") as f:
                            data = json.load(f)
                            system = WaterSystem(
                                system_id=data.get("system_id", filename.replace(".json", "")),
                                name=data.get("name", "Unknown Water System"),
                                description=data.get("description", ""),
                                water_source=data.get("water_source", ""),
                                collection_capacity_liters=data.get("collection_capacity_liters", 0.0),
                                treatment_method=data.get("treatment_method", ""),
                                treatment_capacity_liters_per_day=data.get("treatment_capacity_liters_per_day", 0.0),
                                energy_required_kwh_per_day=data.get("energy_required_kwh_per_day", 0.0),
                                lifespan_years=data.get("lifespan_years", 20),
                                maintenance_level=data.get("maintenance_level", 5),
                                upfront_cost=data.get("upfront_cost", 0.0),
                                region_suitability=data.get("region_suitability", []),
                                climate_suitability=[ClimateZone[c] for c in data.get("climate_suitability", [])],
                                advantages=data.get("advantages", []),
                                disadvantages=data.get("disadvantages", []),
                                installation_guide_url=data.get("installation_guide_url"),
                                images_urls=data.get("images_urls", [])
                            )
                            self.water_systems[system.system_id] = system
                    except Exception as e:
                        logger.error(f"Error loading water system from {file_path}: {e}")
                        
            # Load food systems
            food_dir = os.path.join(self.data_path, "food_systems")
            for filename in os.listdir(food_dir):
                if filename.endswith(".json"):
                    file_path = os.path.join(food_dir, filename)
                    try:
                        with open(file_path, "r") as f:
                            data = json.load(f)
                            system = FoodSystem(
                                system_id=data.get("system_id", filename.replace(".json", "")),
                                name=data.get("name", "Unknown Food System"),
                                description=data.get("description", ""),
                                production_type=data.get("production_type", ""),
                                area_required_sqm=data.get("area_required_sqm", 0.0),
                                water_required_liters_per_day=data.get("water_required_liters_per_day", 0.0),
                                typical_yield_calories_per_sqm=data.get("typical_yield_calories_per_sqm", 0.0),
                                typical_yield_kg_per_sqm=data.get("typical_yield_kg_per_sqm", 0.0),
                                personnel_required_per_hectare=data.get("personnel_required_per_hectare", 0.0),
                                energy_required_kwh_per_day=data.get("energy_required_kwh_per_day", 0.0),
                                setup_time_months=data.get("setup_time_months", 6),
                                region_suitability=data.get("region_suitability", []),
                                climate_suitability=[ClimateZone[c] for c in data.get("climate_suitability", [])],
                                advantages=data.get("advantages", []),
                                disadvantages=data.get("disadvantages", []),
                                implementation_guide_url=data.get("implementation_guide_url"),
                                images_urls=data.get("images_urls", [])
                            )
                            self.food_systems[system.system_id] = system
                    except Exception as e:
                        logger.error(f"Error loading food system from {file_path}: {e}")
                        
            logger.info(f"Loaded {len(self.building_systems)} building systems, {len(self.energy_systems)} energy systems, {len(self.water_systems)} water systems, and {len(self.food_systems)} food systems")
            
        except Exception as e:
            logger.error(f"Error loading systems: {e}")
    
    def _load_communities(self) -> None:
        """Load communities from disk."""
        try:
            # Load communities
            communities_dir = os.path.join(self.data_path, "communities")
            for filename in os.listdir(communities_dir):
                if filename.endswith(".json"):
                    file_path = os.path.join(communities_dir, filename)
                    try:
                        with open(file_path, "r") as f:
                            data = json.load(f)
                            community = Community(
                                community_id=data.get("community_id", filename.replace(".json", "")),
                                name=data.get("name", "Unknown Community"),
                                region_id=data.get("region_id", ""),
                                scale=CommunityScale[data.get("scale", "VILLAGE")],
                                focus=CommunityFocus[data.get("focus", "MIXED_USE")],
                                governance=GovernanceModel[data.get("governance", "CONSENSUS")],
                                description=data.get("description", ""),
                                target_population=data.get("target_population", 0),
                                land_area_acres=data.get("land_area_acres", 0.0),
                                bioregion_features=data.get("bioregion_features", []),
                                building_systems=data.get("building_systems", []),
                                energy_systems=data.get("energy_systems", []),
                                water_systems=data.get("water_systems", []),
                                food_systems=data.get("food_systems", []),
                                skill_requirements=data.get("skill_requirements", {}),
                                development_phases=data.get("development_phases", []),
                                special_features=data.get("special_features", []),
                                estimated_implementation_cost=data.get("estimated_implementation_cost", 0.0),
                                estimated_annual_operating_cost=data.get("estimated_annual_operating_cost", 0.0),
                                mutual_aid_connections=data.get("mutual_aid_connections", []),
                                metadata=data.get("metadata", {})
                            )
                            self.communities[community.community_id] = community
                    except Exception as e:
                        logger.error(f"Error loading community from {file_path}: {e}")
                        
            logger.info(f"Loaded {len(self.communities)} communities")
            
        except Exception as e:
            logger.error(f"Error loading communities: {e}")
    
    def _save_building_system(self, system: BuildingSystem) -> None:
        """Save building system to disk."""
        try:
            file_path = os.path.join(self.data_path, "building_systems", f"{system.system_id}.json")
            
            # Prepare system data
            system_data = {
                "system_id": system.system_id,
                "name": system.name,
                "description": system.description,
                "primary_materials": system.primary_materials,
                "skill_level_required": system.skill_level_required,
                "durability_years": system.durability_years,
                "insulation_value": system.insulation_value,
                "embodied_carbon": system.embodied_carbon,
                "cost_per_sqm": system.cost_per_sqm,
                "region_suitability": system.region_suitability,
                "climate_suitability": [c.name for c in system.climate_suitability],
                "advantages": system.advantages,
                "disadvantages": system.disadvantages,
                "construction_guide_url": system.construction_guide_url,
                "images_urls": system.images_urls
            }
            
            with open(file_path, "w") as f:
                json.dump(system_data, f, indent=2)
                
        except Exception as e:
            logger.error(f"Error saving building system: {e}")
    
    def _save_energy_system(self, system: EnergySystem) -> None:
        """Save energy system to disk."""
        try:
            file_path = os.path.join(self.data_path, "energy_systems", f"{system.system_id}.json")
            
            # Prepare system data
            system_data = {
                "system_id": system.system_id,
                "name": system.name,
                "description": system.description,
                "energy_type": system.energy_type,
                "capacity_range_kw": system.capacity_range_kw,
                "storage_included": system.storage_included,
                "storage_capacity_kwh": system.storage_capacity_kwh,
                "typical_output_kwh_per_year": system.typical_output_kwh_per_year,
                "lifespan_years": system.lifespan_years,
                "maintenance_level": system.maintenance_level,
                "upfront_cost_per_kw": system.upfront_cost_per_kw,
                "region_suitability": system.region_suitability,
                "climate_suitability": [c.name for c in system.climate_suitability],
                "advantages": system.advantages,
                "disadvantages": system.disadvantages,
                "installation_guide_url": system.installation_guide_url,
                "images_urls": system.images_urls
            }
            
            with open(file_path, "w") as f:
                json.dump(system_data, f, indent=2)
                
        except Exception as e:
            logger.error(f"Error saving energy system: {e}")
    
    def _save_water_system(self, system: WaterSystem) -> None:
        """Save water system to disk."""
        try:
            file_path = os.path.join(self.data_path, "water_systems", f"{system.system_id}.json")
            
            # Prepare system data
            system_data = {
                "system_id": system.system_id,
                "name": system.name,
                "description": system.description,
                "water_source": system.water_source,
                "collection_capacity_liters": system.collection_capacity_liters,
                "treatment_method": system.treatment_method,
                "treatment_capacity_liters_per_day": system.treatment_capacity_liters_per_day,
                "energy_required_kwh_per_day": system.energy_required_kwh_per_day,
                "lifespan_years": system.lifespan_years,
                "maintenance_level": system.maintenance_level,
                "upfront_cost": system.upfront_cost,
                "region_suitability": system.region_suitability,
                "climate_suitability": [c.name for c in system.climate_suitability],
                "advantages": system.advantages,
                "disadvantages": system.disadvantages,
                "installation_guide_url": system.installation_guide_url,
                "images_urls": system.images_urls
            }
            
            with open(file_path, "w") as f:
                json.dump(system_data, f, indent=2)
                
        except Exception as e:
            logger.error(f"Error saving water system: {e}")
    
    def _save_food_system(self, system: FoodSystem) -> None:
        """Save food system to disk."""
        try:
            file_path = os.path.join(self.data_path, "food_systems", f"{system.system_id}.json")
            
            # Prepare system data
            system_data = {
                "system_id": system.system_id,
                "name": system.name,
                "description": system.description,
                "production_type": system.production_type,
                "area_required_sqm": system.area_required_sqm,
                "water_required_liters_per_day": system.water_required_liters_per_day,
                "typical_yield_calories_per_sqm": system.typical_yield_calories_per_sqm,
                "typical_yield_kg_per_sqm": system.typical_yield_kg_per_sqm,
                "personnel_required_per_hectare": system.personnel_required_per_hectare,
                "energy_required_kwh_per_day": system.energy_required_kwh_per_day,
                "setup_time_months": system.setup_time_months,
                "region_suitability": system.region_suitability,
                "climate_suitability": [c.name for c in system.climate_suitability],
                "advantages": system.advantages,
                "disadvantages": system.disadvantages,
                "implementation_guide_url": system.implementation_guide_url,
                "images_urls": system.images_urls
            }
            
            with open(file_path, "w") as f:
                json.dump(system_data, f, indent=2)
                
        except Exception as e:
            logger.error(f"Error saving food system: {e}")
    
    def _save_community(self, community: Community) -> None:
        """Save community to disk."""
        try:
            file_path = os.path.join(self.data_path, "communities", f"{community.community_id}.json")
            
            # Prepare community data
            community_data = {
                "community_id": community.community_id,
                "name": community.name,
                "region_id": community.region_id,
                "scale": community.scale.name,
                "focus": community.focus.name,
                "governance": community.governance.name,
                "description": community.description,
                "target_population": community.target_population,
                "land_area_acres": community.land_area_acres,
                "bioregion_features": community.bioregion_features,
                "building_systems": community.building_systems,
                "energy_systems": community.energy_systems,
                "water_systems": community.water_systems,
                "food_systems": community.food_systems,
                "skill_requirements": community.skill_requirements,
                "development_phases": community.development_phases,
                "special_features": community.special_features,
                "estimated_implementation_cost": community.estimated_implementation_cost,
                "estimated_annual_operating_cost": community.estimated_annual_operating_cost,
                "mutual_aid_connections": community.mutual_aid_connections,
                "metadata": community.metadata
            }
            
            with open(file_path, "w") as f:
                json.dump(community_data, f, indent=2)
                
        except Exception as e:
            logger.error(f"Error saving community: {e}")
    
    def _initialize_default_building_systems(self) -> None:
        """Initialize default building systems."""
        default_systems = [
            # Rammed Earth
            BuildingSystem(
                system_id="rammed_earth",
                name="Rammed Earth",
                description="Compacted earth construction using local soil mixed with stabilizers. Excellent thermal mass and durability with very low embodied carbon.",
                primary_materials=["Local soil", "Clay", "Sand", "Small amount of cement or lime"],
                skill_level_required=7,
                durability_years=100,
                insulation_value=0.7,  # R-value per inch
                embodied_carbon=20.0,  # kg CO2e/m²
                cost_per_sqm=350.0,
                region_suitability=["southwest", "northern_plains", "great_lakes"],
                climate_suitability=[
                    ClimateZone.DESERT_HOT, ClimateZone.DESERT_COLD, ClimateZone.STEPPE_HOT, 
                    ClimateZone.STEPPE_COLD, ClimateZone.MEDITERRANEAN
                ],
                advantages=[
                    "Extremely low embodied carbon",
                    "Excellent thermal mass",
                    "Fire resistant",
                    "Creates a quiet interior environment",
                    "Low maintenance",
                    "Can use local materials"
                ],
                disadvantages=[
                    "Labor intensive",
                    "Requires skilled builders",
                    "Not suitable for all soil types",
                    "Poor insulation value alone (needs additional insulation in cold climates)",
                    "Heavy - requires good foundation"
                ]
            ),
            
            # Timber Frame with Straw Bale
            BuildingSystem(
                system_id="timber_strawbale",
                name="Timber Frame with Straw Bale Infill",
                description="Timber frame structure with straw bale walls finished with earth plaster. Combines excellent insulation with renewable materials.",
                primary_materials=["Local timber", "Straw bales", "Clay plaster", "Lime plaster"],
                skill_level_required=6,
                durability_years=75,
                insulation_value=3.5,  # R-value per inch
                embodied_carbon=30.0,  # kg CO2e/m²
                cost_per_sqm=400.0,
                region_suitability=["great_lakes", "pacific_northwest", "northern_plains", "ozarks"],
                climate_suitability=[
                    ClimateZone.CONTINENTAL_COOL, ClimateZone.CONTINENTAL_WARM, ClimateZone.OCEANIC,
                    ClimateZone.HUMID_SUBTROPICAL
                ],
                advantages=[
                    "Excellent insulation (R-30 to R-50 walls)",
                    "Uses agricultural waste product",
                    "Good sound insulation",
                    "Non-toxic building materials",
                    "Carbon sequestering",
                    "Can use local/regional materials"
                ],
                disadvantages=[
                    "Requires careful moisture management",
                    "Not suitable for very humid climates without proper detailing",
                    "Requires specific construction knowledge",
                    "Thicker walls than conventional construction",
                    "Needs protection during construction phase"
                ]
            ),
            
            # Cob Construction
            BuildingSystem(
                system_id="cob",
                name="Cob Construction",
                description="Hand-formed earth building technique using clay-rich soil, sand, and straw. Sculptural, beautiful, and very low embodied energy.",
                primary_materials=["Local soil", "Clay", "Sand", "Straw"],
                skill_level_required=5,
                durability_years=100,
                insulation_value=0.5,  # R-value per inch
                embodied_carbon=10.0,  # kg CO2e/m²
                cost_per_sqm=200.0,
                region_suitability=["pacific_northwest", "new_england", "ozarks"],
                climate_suitability=[
                    ClimateZone.MEDITERRANEAN, ClimateZone.OCEANIC, ClimateZone.HUMID_SUBTROPICAL
                ],
                advantages=[
                    "Extremely low embodied carbon",
                    "Can be built by unskilled people with training",
                    "Thermal mass regulates temperatures",
                    "Non-toxic, completely natural",
                    "Highly sculptural - allows organic forms",
                    "Very low cost with local materials"
                ],
                disadvantages=[
                    "Labor intensive",
                    "Poor insulation - needs additional insulation in cold climates",
                    "Requires good roof overhangs for weather protection",
                    "Long drying time during construction",
                    "Limited to 1-2 stories typically"
                ]
            ),
            
            # Modified Earthship
            BuildingSystem(
                system_id="modified_earthship",
                name="Modified Earthship Design",
                description="Passive solar earth-sheltered design adapted from earthship principles. Incorporates thermal mass, passive ventilation, and optimal solar orientation.",
                primary_materials=["Rammed earth tires", "Earth", "Recycled materials", "Timber"],
                skill_level_required=7,
                durability_years=100,
                insulation_value=2.5,  # R-value per inch (average for system)
                embodied_carbon=25.0,  # kg CO2e/m²
                cost_per_sqm=500.0,
                region_suitability=["southwest", "northern_plains", "ozarks"],
                climate_suitability=[
                    ClimateZone.DESERT_HOT, ClimateZone.DESERT_COLD, ClimateZone.STEPPE_HOT, 
                    ClimateZone.STEPPE_COLD, ClimateZone.CONTINENTAL_WARM
                ],
                advantages=[
                    "Energy efficiency through passive solar design",
                    "Thermal mass regulates temperatures",
                    "Earth-sheltered for weather protection",
                    "Can incorporate greywater systems easily",
                    "Can use recycled materials",
                    "Resilient in extreme climates"
                ],
                disadvantages=[
                    "Complex design requiring careful planning",
                    "Labor intensive construction",
                    "Requires specific site orientation",
                    "High skill level for key systems",
                    "Some materials may need to be imported"
                ]
            ),
            
            # Advanced Wood Framing
            BuildingSystem(
                system_id="advanced_framing",
                name="Advanced Wood Framing",
                description="Optimized wood framing techniques that reduce lumber use while allowing for high insulation values. Combines familiar techniques with improved efficiency.",
                primary_materials=["Dimensional lumber", "Engineered wood", "Cellulose insulation"],
                skill_level_required=5,
                durability_years=60,
                insulation_value=3.7,  # R-value per inch with continuous insulation
                embodied_carbon=70.0,  # kg CO2e/m²
                cost_per_sqm=450.0,
                region_suitability=["pacific_northwest", "great_lakes", "new_england", "ozarks"],
                climate_suitability=[
                    ClimateZone.CONTINENTAL_HOT, ClimateZone.CONTINENTAL_WARM, ClimateZone.CONTINENTAL_COOL,
                    ClimateZone.OCEANIC, ClimateZone.HUMID_SUBTROPICAL
                ],
                advantages=[
                    "Very high efficiency (300-400% for heating)",
                    "Both heating and cooling in one system",
                    "Long lifespan with minimal maintenance",
                    "No combustion or carbon emissions on-site",
                    "Stable performance in extreme temperatures",
                    "Lower operating costs than conventional HVAC"
                ],
                disadvantages=[
                    "High initial installation cost",
                    "Requires suitable ground conditions",
                    "Installation disrupts landscape temporarily",
                    "Requires electricity to operate pumps",
                    "May not be cost-effective for small buildings"
                ]
            )
        ]
        
        # Add systems
        for system in default_systems:
            self.energy_systems[system.system_id] = system
            self._save_energy_system(system)
            
        logger.info(f"Initialized {len(default_systems)} default energy systems")
    
    def _initialize_default_water_systems(self) -> None:
        """Initialize default water systems."""
        default_systems = [
            # Rainwater Harvesting
            WaterSystem(
                system_id="rainwater_harvest",
                name="Comprehensive Rainwater Harvesting System",
                description="Collection and storage of rainwater from roofs and other surfaces for various uses from irrigation to potable water.",
                water_source="rain",
                collection_capacity_liters=50000.0,
                treatment_method="Filtration, UV disinfection",
                treatment_capacity_liters_per_day=1000.0,
                energy_required_kwh_per_day=0.5,
                lifespan_years=30,
                maintenance_level=4,
                upfront_cost=10000.0,
                region_suitability=["pacific_northwest", "new_england", "ozarks", "great_lakes"],
                climate_suitability=[
                    ClimateZone.RAINFOREST, ClimateZone.MONSOON, ClimateZone.OCEANIC,
                    ClimateZone.HUMID_SUBTROPICAL
                ],
                advantages=[
                    "Uses free, clean water source",
                    "Reduces demand on groundwater and municipal supplies",
                    "Simple system with minimal moving parts",
                    "Very low operating costs",
                    "Can be retrofitted to existing buildings",
                    "Scalable from small to large applications"
                ],
                disadvantages=[
                    "Dependent on rainfall patterns",
                    "Requires adequate roof/collection area",
                    "Storage tanks require significant space",
                    "Additional treatment needed for potable use",
                    "May require backup water source in dry periods"
                ]
            ),
            
            # Living Machine Greywater
            WaterSystem(
                system_id="living_machine",
                name="Living Machine Greywater System",
                description="Ecological wastewater treatment using a series of engineered wetlands and biological components to purify greywater for reuse.",
                water_source="greywater",
                collection_capacity_liters=5000.0,
                treatment_method="Biological filtration through constructed wetlands",
                treatment_capacity_liters_per_day=2000.0,
                energy_required_kwh_per_day=0.3,
                lifespan_years=25,
                maintenance_level=5,
                upfront_cost=15000.0,
                region_suitability=["pacific_northwest", "ozarks", "great_lakes", "southwest"],
                climate_suitability=[c for c in ClimateZone if c != ClimateZone.TUNDRA and c != ClimateZone.POLAR_ICE],
                advantages=[
                    "Treats water while creating beautiful landscape features",
                    "Minimal energy requirements",
                    "Creates habitat for beneficial insects and wildlife",
                    "Educational opportunity for ecological processes",
                    "Can handle flow variations well",
                    "Produces reusable water for irrigation"
                ],
                disadvantages=[
                    "Requires significant space",
                    "Performance varies with temperature (slower in cold climates)",
                    "Requires some specialized knowledge for maintenance",
                    "More complex than simple greywater systems",
                    "May require greenhouse protection in very cold climates"
                ]
            ),
            
            # Slow Sand Filtration
            WaterSystem(
                system_id="slow_sand",
                name="Slow Sand Filtration System",
                description="Biological water treatment using sand filtration for pathogen removal. Simple, reliable technology for clean drinking water.",
                water_source="surface or rainwater",
                collection_capacity_liters=10000.0,
                treatment_method="Biological sand filtration",
                treatment_capacity_liters_per_day=500.0,
                energy_required_kwh_per_day=0.0,
                lifespan_years=20,
                maintenance_level=3,
                upfront_cost=5000.0,
                region_suitability=["pacific_northwest", "new_england", "ozarks", "great_lakes", "northern_plains"],
                climate_suitability=[c for c in ClimateZone if c != ClimateZone.POLAR_ICE],
                advantages=[
                    "No electricity required (gravity-powered)",
                    "Simple construction with local materials possible",
                    "Very effective pathogen removal",
                    "Low maintenance",
                    "Low operating costs",
                    "Resilient and reliable technology"
                ],
                disadvantages=[
                    "Relatively slow flow rate",
                    "Requires consistent maintenance schedule",
                    "Large footprint compared to mechanical filters",
                    "Less effective with highly turbid water",
                    "Process takes time to establish initially"
                ]
            ),
            
            # Drip Irrigation System
            WaterSystem(
                system_id="drip_irrigation",
                name="Water-Efficient Drip Irrigation",
                description="Precision water delivery system for agricultural and landscape applications, significantly reducing water use compared to conventional irrigation.",
                water_source="any",
                collection_capacity_liters=5000.0,
                treatment_method="Basic filtration",
                treatment_capacity_liters_per_day=5000.0,
                energy_required_kwh_per_day=0.2,
                lifespan_years=10,
                maintenance_level=4,
                upfront_cost=2000.0,
                region_suitability=["southwest", "northern_plains", "great_lakes", "ozarks"],
                climate_suitability=[
                    ClimateZone.DESERT_HOT, ClimateZone.DESERT_COLD, ClimateZone.STEPPE_HOT, 
                    ClimateZone.STEPPE_COLD, ClimateZone.MEDITERRANEAN, ClimateZone.HUMID_SUBTROPICAL
                ],
                advantages=[
                    "Water use reduction of 30-70% compared to conventional irrigation",
                    "Delivers water directly to plant roots",
                    "Reduces weed growth between plants",
                    "Can be automated with simple timers",
                    "Works with low water pressure",
                    "Can use greywater sources"
                ],
                disadvantages=[
                    "Initial installation cost higher than simple irrigation",
                    "Requires filtering to prevent clogging",
                    "Needs regular inspection for leaks or clogs",
                    "Emitters can be damaged by animals or cultivation",
                    "Surface components degrade in UV sunlight"
                ]
            ),
            
            # Fog Collection System
            WaterSystem(
                system_id="fog_collection",
                name="Fog Water Collection System",
                description="Mesh nets that collect water from fog in suitable coastal or mountainous areas, requiring no energy input.",
                water_source="atmospheric moisture",
                collection_capacity_liters=1000.0,
                treatment_method="Basic filtration",
                treatment_capacity_liters_per_day=200.0,
                energy_required_kwh_per_day=0.0,
                lifespan_years=10,
                maintenance_level=3,
                upfront_cost=3000.0,
                region_suitability=["pacific_northwest", "new_england"],
                climate_suitability=[
                    ClimateZone.OCEANIC, ClimateZone.MEDITERRANEAN, ClimateZone.MOUNTAIN
                ],
                advantages=[
                    "Works in drought conditions where fog is present",
                    "No energy requirements",
                    "Simple, passive technology",
                    "Low maintenance requirements",
                    "Can work in areas without other water sources",
                    "Collects clean water requiring minimal treatment"
                ],
                disadvantages=[
                    "Only viable in specific geographic locations with regular fog",
                    "Yield varies significantly with conditions",
                    "Collection area must be in fog path",
                    "Requires regular cleaning of mesh",
                    "Net collectors may be damaged by strong winds"
                ]
            )
        ]
        
        # Add systems
        for system in default_systems:
            self.water_systems[system.system_id] = system
            self._save_water_system(system)
            
        logger.info(f"Initialized {len(default_systems)} default water systems")
    
    def _initialize_default_food_systems(self) -> None:
        """Initialize default food systems."""
        default_systems = [
            # Intensive Annual Gardens
            FoodSystem(
                system_id="intensive_annual",
                name="Intensive Annual Vegetable Production",
                description="Biointensive growing methods for high yields of annual vegetables in small spaces with minimal inputs.",
                production_type="garden",
                area_required_sqm=400.0,  # 0.1 acre
                water_required_liters_per_day=1000.0,
                typical_yield_calories_per_sqm=700.0,
                typical_yield_kg_per_sqm=5.0,
                personnel_required_per_hectare=5.0,
                energy_required_kwh_per_day=0.5,
                setup_time_months=2,
                region_suitability=["pacific_northwest", "great_lakes", "new_england", "ozarks"],
                climate_suitability=[
                    ClimateZone.OCEANIC, ClimateZone.HUMID_SUBTROPICAL, ClimateZone.CONTINENTAL_WARM,
                    ClimateZone.MEDITERRANEAN
                ],
                advantages=[
                    "High productivity in small spaces",
                    "Quick establishment and yields",
                    "Familiar foods and growing methods",
                    "Low startup costs",
                    "Adaptable to many climates with season extension",
                    "Good entry point for new gardeners"
                ],
                disadvantages=[
                    "Labor intensive",
                    "Requires regular irrigation",
                    "Annual replanting necessary",
                    "Soil needs regular replenishment",
                    "Seasonal production without infrastructure",
                    "Susceptible to pest and disease pressure"
                ]
            ),
            
            # Food Forest
            FoodSystem(
                system_id="food_forest",
                name="Perennial Food Forest System",
                description="Multi-layered perennial polyculture mimicking forest structure while producing diverse foods with minimal intervention once established.",
                production_type="agroforestry",
                area_required_sqm=2000.0,  # 0.5 acre
                water_required_liters_per_day=500.0,
                typical_yield_calories_per_sqm=400.0,
                typical_yield_kg_per_sqm=2.0,
                personnel_required_per_hectare=1.0,
                energy_required_kwh_per_day=0.0,
                setup_time_months=36,
                region_suitability=["pacific_northwest", "great_lakes", "new_england", "ozarks", "southwest"],
                climate_suitability=[c for c in ClimateZone if c != ClimateZone.POLAR_ICE and c != ClimateZone.TUNDRA],
                advantages=[
                    "Low maintenance once established",
                    "Drought resistant after establishment",
                    "Builds soil health over time",
                    "Creates wildlife habitat",
                    "Diverse yields throughout seasons",
                    "Carbon sequestration and microclimate benefits"
                ],
                disadvantages=[
                    "Long establishment period (3-7 years)",
                    "Higher initial investment",
                    "Requires careful planning and design",
                    "Lower caloric yield than annual gardens",
                    "Some specialized knowledge required",
                    "Harvesting can be more time-consuming"
                ]
            ),
            
            # Aquaponics System
            FoodSystem(
                system_id="aquaponics",
                name="Integrated Aquaponics System",
                description="Closed-loop system combining fish cultivation and hydroponics, producing fish protein and vegetables with minimal water use.",
                production_type="aquaponics",
                area_required_sqm=200.0,
                water_required_liters_per_day=50.0,  # Minimal daily topoff
                typical_yield_calories_per_sqm=900.0,
                typical_yield_kg_per_sqm=10.0,
                personnel_required_per_hectare=10.0,
                energy_required_kwh_per_day=5.0,
                setup_time_months=3,
                region_suitability=["pacific_northwest", "great_lakes", "southwest", "ozarks"],
                climate_suitability=[c for c in ClimateZone], # All climates with greenhouse
                advantages=[
                    "Very water efficient (95% less than conventional agriculture)",
                    "Produces both protein and vegetables",
                    "Year-round production possible",
                    "No soil required",
                    "High productivity in small space",
                    "Can be situated on marginal land or indoors"
                ],
                disadvantages=[
                    "Requires reliable electricity",
                    "Technical knowledge required",
                    "Higher startup costs",
                    "System complexity and interdependence",
                    "Energy intensive in cold climates",
                    "Risk of total system failure affecting both components"
                ]
            ),
            
            # Rotational Grazing
            FoodSystem(
                system_id="rotational_grazing",
                name="Regenerative Rotational Grazing",
                description="Managed livestock grazing system that builds soil, sequesters carbon, and produces animal products while improving ecosystem health.",
                production_type="grazing",
                area_required_sqm=40000.0,  # 4 hectares
                water_required_liters_per_day=2000.0,
                typical_yield_calories_per_sqm=50.0,
                typical_yield_kg_per_sqm=0.1,
                personnel_required_per_hectare=0.2,
                energy_required_kwh_per_day=0.1,
                setup_time_months=6,
                region_suitability=["northern_plains", "great_lakes", "ozarks", "new_england"],
                climate_suitability=[
                    ClimateZone.CONTINENTAL_HOT, ClimateZone.CONTINENTAL_WARM, ClimateZone.CONTINENTAL_COOL,
                    ClimateZone.HUMID_SUBTROPICAL, ClimateZone.OCEANIC, ClimateZone.STEPPE_HOT, ClimateZone.STEPPE_COLD
                ],
                advantages=[
                    "Builds soil carbon and fertility",
                    "Converts inedible grass to human food",
                    "Can be combined with silvopasture for tree crops",
                    "Low input costs after establishment",
                    "Improves wildlife habitat and biodiversity",
                    "Works on marginal land unsuitable for crops"
                ],
                disadvantages=[
                    "Requires significant land area",
                    "Lower caloric yield per acre than crops",
                    "Requires knowledge of animal husbandry",
                    "Infrastructure costs for fencing and water",
                    "Daily management required",
                    "Winter feed may be necessary in some climates"
                ]
            ),
            
            # Greenhouse
            FoodSystem(
                system_id="passive_greenhouse",
                name="Passive Solar Greenhouse",
                description="Energy-efficient growing structure using passive solar design for year-round production with minimal supplemental heating.",
                production_type="protected cultivation",
                area_required_sqm=100.0,
                water_required_liters_per_day=300.0,
                typical_yield_calories_per_sqm=1200.0,
                typical_yield_kg_per_sqm=15.0,
                personnel_required_per_hectare=20.0,
                energy_required_kwh_per_day=1.0,
                setup_time_months=4,
                region_suitability=["northern_plains", "great_lakes", "new_england", "pacific_northwest"],
                climate_suitability=[
                    ClimateZone.CONTINENTAL_HOT, ClimateZone.CONTINENTAL_WARM, ClimateZone.CONTINENTAL_COOL,
                    ClimateZone.SUBARCTIC, ClimateZone.OCEANIC
                ],
                advantages=[
                    "Extends growing season in cold climates",
                    "Protects crops from extreme weather",
                    "High productivity per square foot",
                    "Year-round production possible",
                    "Can integrate aquaponics or vertical systems",
                    "Good microclimate for starting seedlings"
                ],
                disadvantages=[
                    "Higher initial cost",
                    "Requires good solar exposure",
                    "More technical knowledge required",
                    "Needs ventilation management",
                    "Can overheat without proper design",
                    "May need supplemental heat in extreme cold"
                ]
            )
        ]
        
        # Add systems
        for system in default_systems:
            self.food_systems[system.system_id] = system
            self._save_food_system(system)
            
        logger.info(f"Initialized {len(default_systems)} default food systems")
    
    def _initialize_default_communities(self) -> None:
        """Initialize default community templates."""
        default_communities = [
            # Pacific Northwest Forest Village
            Community(
                community_id="pnw_forest_village",
                name="Cascadia Forest Village",
                region_id="pacific_northwest",
                scale=CommunityScale.VILLAGE,
                focus=CommunityFocus.ECOLOGICAL,
                governance=GovernanceModel.SOCIOCRACY,
                description="A forest-integrated village designed for the Pacific Northwest, emphasizing timber resources, water abundance, and ecological restoration.",
                target_population=200,
                land_area_acres=120.0,
                bioregion_features=[
                    "Mixed conifer forest integration",
                    "Salmon-bearing stream restoration",
                    "Moderate rainfall harvesting",
                    "Forest understory food forest"
                ],
                building_systems=["timber_strawbale", "cob", "advanced_framing"],
                energy_systems=["solar_battery", "micro_hydro"],
                water_systems=["rainwater_harvest", "living_machine"],
                food_systems=["food_forest", "intensive_annual", "passive_greenhouse"],
                skill_requirements={
                    "ecological_restoration": 5,
                    "forestry": 3,
                    "timber_framing": 2,
                    "renewable_energy": 2,
                    "education": 3,
                    "permaculture": 4,
                    "community_facilitation": 3
                },
                development_phases=[
                    {
                        "name": "Foundation Phase",
                        "duration_months": 6,
                        "focus": "Site assessment, initial infrastructure, temporary housing"
                    },
                    {
                        "name": "Core Establishment",
                        "duration_months": 18,
                        "focus": "Primary buildings, water systems, initial food systems"
                    },
                    {
                        "name": "Growth Phase",
                        "duration_months": 36,
                        "focus": "Additional housing, economic development, forest management plan"
                    },
                    {
                        "name": "Resilience Phase",
                        "duration_months": 60,
                        "focus": "Education center, expanded food production, seed saving program"
                    }
                ],
                special_features=[
                    "Forest education center",
                    "Riparian restoration project",
                    "Timber processing facility",
                    "Salmon habitat enhancement",
                    "Native plant nursery"
                ],
                estimated_implementation_cost=4000000.0,
                estimated_annual_operating_cost=250000.0,
                mutual_aid_connections=[]
            ),
            
            # Great Lakes Agrarian Town
            Community(
                community_id="great_lakes_agrarian",
                name="Great Lakes Agrarian Community",
                region_id="great_lakes",
                scale=CommunityScale.TOWN,
                focus=CommunityFocus.AGRICULTURAL,
                governance=GovernanceModel.COUNCIL,
                description="An agricultural community designed for the Great Lakes region, focusing on regenerative farming practices and value-added food processing.",
                target_population=500,
                land_area_acres=800.0,
                bioregion_features=[
                    "Prime agricultural land restoration",
                    "Four-season cultivation systems",
                    "Freshwater access management",
                    "Forest woodlot integration"
                ],
                building_systems=["advanced_framing", "timber_strawbale", "rammed_earth"],
                energy_systems=["solar_battery", "small_wind", "biogas"],
                water_systems=["rainwater_harvest", "drip_irrigation"],
                food_systems=["rotational_grazing", "intensive_annual", "passive_greenhouse", "food_forest"],
                skill_requirements={
                    "regenerative_agriculture": 8,
                    "animal_husbandry": 4,
                    "food_processing": 5,
                    "carpentry": 4,
                    "community_organizing": 3,
                    "equipment_maintenance": 4,
                    "seed_saving": 3
                },
                development_phases=[
                    {
                        "name": "Land Restoration",
                        "duration_months": 12,
                        "focus": "Soil remediation, water systems, initial pasture establishment"
                    },
                    {
                        "name": "Core Infrastructure",
                        "duration_months": 18,
                        "focus": "Primary housing, barns, processing facilities, energy systems"
                    },
                    {
                        "name": "Agricultural Development",
                        "duration_months": 24,
                        "focus": "Expanding fields, food forests, animal systems, greenhouses"
                    },
                    {
                        "name": "Community Completion",
                        "duration_months": 48,
                        "focus": "Education facilities, additional housing, markets, distribution systems"
                    }
                ],
                special_features=[
                    "Grain processing facility",
                    "Community supported agriculture program",
                    "Regional seed bank",
                    "Four-season farmers market",
                    "Agricultural equipment sharing system"
                ],
                estimated_implementation_cost=7000000.0,
                estimated_annual_operating_cost=400000.0,
                mutual_aid_connections=[]
            ),
            
            # Southwest Desert Oasis
            Community(
                community_id="southwest_oasis",
                name="Desert Oasis Community",
                region_id="southwest",
                scale=CommunityScale.NEIGHBORHOOD,
                focus=CommunityFocus.WATER,
                governance=GovernanceModel.CONSENSUS,
                description="A water-wise desert community demonstrating regenerative living in arid conditions through careful water harvesting and management.",
                target_population=75,
                land_area_acres=50.0,
                bioregion_features=[
                    "Desert wash water harvesting",
                    "Xeriscaping throughout",
                    "Shaded microclimate creation",
                    "Desert soil building"
                ],
                building_systems=["rammed_earth", "modified_earthship"],
                energy_systems=["solar_battery"],
                water_systems=["rainwater_harvest", "drip_irrigation"],
                food_systems=["food_forest", "aquaponics"],
                skill_requirements={
                    "water_management": 7,
                    "desert_ecology": 4,
                    "natural_building": 5,
                    "solar_energy": 4,
                    "arid_land_restoration": 4,
                    "xeriscaping": 3,
                    "community_facilitation": 2
                },
                development_phases=[
                    {
                        "name": "Water Systems Establishment",
                        "duration_months": 12,
                        "focus": "Water harvesting earthworks, cisterns, initial shade structures"
                    },
                    {
                        "name": "Core Habitat Development",
                        "duration_months": 18,
                        "focus": "Primary buildings, solar systems, initial food production"
                    },
                    {
                        "name": "Expansion Phase",
                        "duration_months": 24,
                        "focus": "Additional housing, expanded water catchment, food forest"
                    },
                    {
                        "name": "Demonstration Completion",
                        "duration_months": 24,
                        "focus": "Education center, visitor facilities, expanded systems"
                    }
                ],
                special_features=[
                    "Desert water harvesting demonstration site",
                    "Shadehouse nursery for native and food plants",
                    "Passive cooling systems",
                    "Desert permaculture educational programs",
                    "Native pollinator habitat restoration"
                ],
                estimated_implementation_cost=2500000.0,
                estimated_annual_operating_cost=150000.0,
                mutual_aid_connections=[]
            ),
            
            # Northern Plains Regenerative Hub
            Community(
                community_id="plains_regenerative",
                name="Great Plains Regeneration Center",
                region_id="northern_plains",
                scale=CommunityScale.SMALL_CITY,
                focus=CommunityFocus.MIXED_USE,
                governance=GovernanceModel.SOCIOCRACY,
                description="A regenerative hub for the Great Plains designed to restore grasslands while creating a resilient community with agricultural and manufacturing capacity.",
                target_population=2000,
                land_area_acres=5000.0,
                bioregion_features=[
                    "Tallgrass prairie restoration",
                    "Watershed regeneration",
                    "Windbreak development",
                    "Soil carbon sequestration"
                ],
                building_systems=["advanced_framing", "straw_bale", "rammed_earth"],
                energy_systems=["small_wind", "solar_battery", "biogas"],
                water_systems=["rainwater_harvest", "drip_irrigation"],
                food_systems=["rotational_grazing", "intensive_annual", "food_forest"],
                skill_requirements={
                    "grassland_restoration": 5,
                    "regenerative_agriculture": 8,
                    "renewable_energy": 6,
                    "community_planning": 4,
                    "manufacturing": 7,
                    "water_management": 5,
                    "education": 4
                },
                development_phases=[
                    {
                        "name": "Initial Settlement",
                        "duration_months": 12,
                        "focus": "Core infrastructure, temporary housing, initial watershed work"
                    },
                    {
                        "name": "Agricultural Systems",
                        "duration_months": 24,
                        "focus": "Grazing setup, wind systems, primary housing, soil building"
                    },
                    {
                        "name": "Manufacturing Development",
                        "duration_months": 36,
                        "focus": "Production facilities, additional housing, expanded energy"
                    },
                    {
                        "name": "Regional Hub Completion",
                        "duration_months": 48,
                        "focus": "Education center, processing facilities, distribution network"
                    }
                ],
                special_features=[
                    "Bison restoration program",
                    "Wind turbine manufacturing facility",
                    "Regenerative grazing demonstration",
                    "Climate-appropriate building center",
                    "Prairie seed bank and nursery"
                ],
                estimated_implementation_cost=15000000.0,
                estimated_annual_operating_cost=1200000.0,
                mutual_aid_connections=[]
            )
        ]
        
        # Add communities
        for community in default_communities:
            self.communities[community.community_id] = community
            self._save_community(community)
            
        logger.info(f"Initialized {len(default_communities)} default community templates")
    
    def get_community(self, community_id: str) -> Optional[Community]:
        """
        Get a community by ID.
        
        Args:
            community_id: Community identifier
            
        Returns:
            Community if found, None otherwise
        """
        return self.communities.get(community_id)
    
    def get_all_communities(self) -> List[Community]:
        """
        Get all communities.
        
        Returns:
            List of communities
        """
        return list(self.communities.values())
    
    def add_community(self, community: Community) -> bool:
        """
        Add a new community.
        
        Args:
            community: Community to add
            
        Returns:
            Success status
        """
        # Check if already exists
        if community.community_id in self.communities:
            return False
            
        # Add community
        self.communities[community.community_id] = community
        
        # Save to disk
        self._save_community(community)
        
        return True
    
    def update_community(self, community: Community) -> bool:
        """
        Update an existing community.
        
        Args:
            community: Community to update
            
        Returns:
            Success status
        """
        # Check if exists
        if community.community_id not in self.communities:
            return False
            
        # Update community
        self.communities[community.community_id] = community
        
        # Save to disk
        self._save_community(community)
        
        return True
    
    def get_building_system(self, system_id: str) -> Optional[BuildingSystem]:
        """Get a building system by ID."""
        return self.building_systems.get(system_id)
    
    def get_energy_system(self, system_id: str) -> Optional[EnergySystem]:
        """Get an energy system by ID."""
        return self.energy_systems.get(system_id)
    
    def get_water_system(self, system_id: str) -> Optional[WaterSystem]:
        """Get a water system by ID."""
        return self.water_systems.get(system_id)
    
    def get_food_system(self, system_id: str) -> Optional[FoodSystem]:
        """Get a food system by ID."""
        return self.food_systems.get(system_id)
    
    def find_communities_for_region(self, region_id: str) -> List[Community]:
        """
        Find community templates suitable for a specific region.
        
        Args:
            region_id: Region identifier
            
        Returns:
            List of suitable communities
        """
        # Find all communities for this region
        region_communities = [c for c in self.communities.values() if c.region_id == region_id]
        
        # If none specific to this region, find communities with adaptable designs
        if not region_communities:
            # Check all communities
            region_communities = []
            
            for community in self.communities.values():
                # Check if building systems are adaptable to this region
                building_suitable = any(
                    self.building_systems.get(b_id) and region_id in self.building_systems[b_id].region_suitability
                    for b_id in community.building_systems
                )
                
                # Check if water systems are adaptable to this region
                water_suitable = any(
                    self.water_systems.get(w_id) and region_id in self.water_systems[w_id].region_suitability
                    for w_id in community.water_systems
                )
                
                if building_suitable and water_suitable:
                    region_communities.append(community)
                    
        return region_communities
    
    def design_community_for_region(self, 
                                 region_id: str,
                                 scale: CommunityScale,
                                 focus: CommunityFocus,
                                 name: str = None) -> Optional[Community]:
        """
        Design a custom community template for a specific region.
        
        Args:
            region_id: Region identifier
            scale: Community scale
            focus: Community focus
            name: Optional name
            
        Returns:
            Custom community design
        """
        # Get region
        region = self.mapper.get_region(region_id)
        if not region:
            return None
            
        # Generate community ID
        community_id = f"{region_id}_{focus.name.lower()}_{scale.name.lower()}"
        
        # Generate name if not provided
        if not name:
            name = f"{region.name} {focus.name.title()} {scale.name.title()}"
            
        # Determine appropriate governance models based on scale
        governance = GovernanceModel.CONSENSUS
        if scale == CommunityScale.TOWN:
            governance = GovernanceModel.SOCIOCRACY
        elif scale == CommunityScale.SMALL_CITY:
            governance = GovernanceModel.COUNCIL
        elif scale == CommunityScale.REGIONAL_HUB:
            governance = GovernanceModel.REPRESENTATIVE
            
        # Determine population based on scale
        population_by_scale = {
            CommunityScale.NEIGHBORHOOD: 100,
            CommunityScale.VILLAGE: 250,
            CommunityScale.TOWN: 1000,
            CommunityScale.SMALL_CITY: 5000,
            CommunityScale.REGIONAL_HUB: 10000
        }
        target_population = population_by_scale.get(scale, 250)
        
        # Determine land area based on scale and region characteristics
        base_land_area = {
            CommunityScale.NEIGHBORHOOD: 50.0,
            CommunityScale.VILLAGE: 200.0,
            CommunityScale.TOWN: 800.0,
            CommunityScale.SMALL_CITY: 3000.0,
            CommunityScale.REGIONAL_HUB: 8000.0
        }
        land_area = base_land_area.get(scale, 200.0)
        
        # Adjust land area based on region characteristics
        if region.metrics.water_availability.value <= WaterAvailability.STRESSED.value:
            land_area *= 1.5  # Need more land in water-stressed regions
        if region.metrics.soil_quality.value <= SoilQuality.MODERATE.value:
            land_area *= 1.3  # Need more land with moderate soil
            
        # Select suitable building systems
        climate_zone = region.metrics.climate_zone
        building_systems = []
        
        for system_id, system in self.building_systems.items():
            if region_id in system.region_suitability or climate_zone in system.climate_suitability:
                building_systems.append(system_id)
                
        building_systems = building_systems[:3]  # Limit to top 3
        
        # Select suitable energy systems
        energy_systems = []
        
        # Check region's energy potential
        if region.metrics.renewable_energy_potential.get("solar", 0) > 20000000000:
            energy_systems.append("solar_battery")
        if region.metrics.renewable_energy_potential.get("wind", 0) > 20000000000:
            energy_systems.append("small_wind")
        if region.metrics.renewable_energy_potential.get("hydro", 0) > 5000000000:
            energy_systems.append("micro_hydro")
            
        # Add biogas for agricultural focus
        if focus == CommunityFocus.AGRICULTURAL:
            energy_systems.append("biogas")
            
        # Add geothermal where appropriate
        if climate_zone in [ClimateZone.CONTINENTAL_COOL, ClimateZone.CONTINENTAL_WARM, 
                           ClimateZone.CONTINENTAL_HOT, ClimateZone.SUBARCTIC]:
            energy_systems.append("geothermal_heat")
            
        # Ensure at least one energy system
        if not energy_systems:
            energy_systems.append("solar_battery")
            
        # Select suitable water systems
        water_systems = []
        
        if region.metrics.water_availability.value >= WaterAvailability.SUFFICIENT.value:
            water_systems.append("rainwater_harvest")
            
        # Add appropriate water management systems based on climate
        if climate_zone in [ClimateZone.DESERT_HOT, ClimateZone.DESERT_COLD, 
                           ClimateZone.STEPPE_HOT, ClimateZone.STEPPE_COLD]:
            water_systems.append("drip_irrigation")
        else:
            water_systems.append("living_machine")
            
        # Add slow sand filtration for most regions
        water_systems.append("slow_sand")
        
        # Add fog collection for suitable regions
        if climate_zone in [ClimateZone.OCEANIC, ClimateZone.MEDITERRANEAN] and "coastal" in region.name.lower():
            water_systems.append("fog_collection")
            
        # Select suitable food systems
        food_systems = []
        
        # Add food systems based on focus
        if focus == CommunityFocus.AGRICULTURAL:
            food_systems.extend(["rotational_grazing", "intensive_annual"])
        else:
            food_systems.append("intensive_annual")
            
        # Add appropriate systems based on climate
        if climate_zone in [ClimateZone.CONTINENTAL_COOL, ClimateZone.CONTINENTAL_WARM, 
                           ClimateZone.CONTINENTAL_HOT, ClimateZone.SUBARCTIC]:
            food_systems.append("passive_greenhouse")
            
        # Add food forest for most regions
        if climate_zone not in [ClimateZone.DESERT_HOT, ClimateZone.DESERT_COLD, ClimateZone.POLAR_ICE]:
            food_systems.append("food_forest")
            
        # Add aquaponics for specialized production
        if focus in [CommunityFocus.TECHNOLOGICAL, CommunityFocus.EDUCATIONAL]:
            food_systems.append("aquaponics")
            
        # Determine bioregion features
        bioregion_features = []
        
        # Add features based on region ecosystems
        for ecosystem in region.metrics.ecosystem_types:
            if ecosystem == EcosystemType.FOREST_TEMPERATE:
                bioregion_features.append("Temperate forest integration")
            elif ecosystem == EcosystemType.GRASSLAND:
                bioregion_features.append("Native grassland restoration")
            elif ecosystem == EcosystemType.DESERT:
                bioregion_features.append("Desert ecology preservation")
            elif ecosystem == EcosystemType.WETLAND:
                bioregion_features.append("Wetland conservation and expansion")
                
        # Add water-related feature
        if region.metrics.water_availability.value >= WaterAvailability.SUFFICIENT.value:
            bioregion_features.append("Watershed protection and enhancement")
        else:
            bioregion_features.append("Water conservation and harvesting systems")
            
        # Add climate feature
        bioregion_features.append(f"{climate_zone.name.replace('_', ' ').title()} climate adaptation strategies")
        
        # Determine required skills based on focus and systems
        skill_requirements = {
            "community_facilitation": 3,  # Always needed
            "ecological_literacy": 4,     # Always needed
            "infrastructure_maintenance": 3  # Always needed
        }
        
        # Add skills based on focus
        if focus == CommunityFocus.AGRICULTURAL:
            skill_requirements.update({
                "regenerative_agriculture": 5,
                "food_processing": 4,
                "seed_saving": 3
            })
        elif focus == CommunityFocus.ECOLOGICAL:
            skill_requirements.update({
                "ecosystem_restoration": 5,
                "wildlife_management": 3,
                "botanical_knowledge": 4
            })
        elif focus == CommunityFocus.EDUCATIONAL:
            skill_requirements.update({
                "teaching": 5,
                "curriculum_development": 4,
                "facilitation": 4
            })
        elif focus == CommunityFocus.MANUFACTURING:
            skill_requirements.update({
                "fabrication": 5,
                "material_processing": 4,
                "design": 4
            })
        elif focus == CommunityFocus.ENERGY:
            skill_requirements.update({
                "renewable_energy": 5,
                "electrical_systems": 4,
                "energy_storage": 4
            })
            
        # Create phased development plan
        development_phases = [
            {
                "name": "Foundation Phase",
                "duration_months": 12,
                "focus": "Site assessment, initial infrastructure, temporary housing, resource inventory"
            },
            {
                "name": "Core Development",
                "duration_months": 24,
                "focus": "Primary buildings, basic systems, initial food production, governance establishment"
            },
            {
                "name": "Expansion Phase",
                "duration_months": 36,
                "focus": "Additional housing, expanded production, specialized facilities, refinement of systems"
            },
            {
                "name": "Maturity & Outreach",
                "duration_months": 48,
                "focus": "Education programs, regional connections, resilience enhancements, cultural development"
            }
        ]
        
        # Calculate estimated costs
        base_implementation_cost = {
            CommunityScale.NEIGHBORHOOD: 2000000.0,
            CommunityScale.VILLAGE: 5000000.0,
            CommunityScale.TOWN: 15000000.0,
            CommunityScale.SMALL_CITY: 50000000.0,
            CommunityScale.REGIONAL_HUB: 120000000.0
        }
        
        base_operating_cost = {
            CommunityScale.NEIGHBORHOOD: 150000.0,
            CommunityScale.VILLAGE: 400000.0,
            CommunityScale.TOWN: 1200000.0,
            CommunityScale.SMALL_CITY: 4000000.0,
            CommunityScale.REGIONAL_HUB: 10000000.0
        }
        
        # Adjust costs based on region and focus
        implementation_cost = base_implementation_cost.get(scale, 5000000.0)
        operating_cost = base_operating_cost.get(scale, 400000.0)
        
        # Adjust for infrastructure status
        if region.metrics.infrastructure_status.value <= InfrastructureStatus.DEGRADED.value:
            implementation_cost *= 1.3  # Higher cost in regions with poor infrastructure
            
        # Create community design
        community = Community(
            community_id=community_id,
            name=name,
            region_id=region_id,
            scale=scale,
            focus=focus,
            governance=governance,
            description=f"Custom {focus.name.lower()} community designed for the {region.name}, emphasizing sustainable development tailored to local bioregional characteristics.",
            target_population=target_population,
            land_area_acres=land_area,
            bioregion_features=bioregion_features,
            building_systems=building_systems,
            energy_systems=energy_systems,
            water_systems=water_systems,
            food_systems=food_systems,
            skill_requirements=skill_requirements,
            development_phases=development_phases,
            special_features=[],  # To be customized
            estimated_implementation_cost=implementation_cost,
            estimated_annual_operating_cost=operating_cost,
            mutual_aid_connections=[]
        )
        
        return community
    
    def calculate_community_requirements(self, community: Community) -> Dict[str, Any]:
        """
        Calculate detailed requirements for implementing a community design.
        
        Args:
            community: Community design
            
        Returns:
            Detailed requirements
        """
        try:
            # Calculate total material requirements
            building_materials = {}
            
            # Process building systems
            for system_id in community.building_systems:
                building_system = self.building_systems.get(system_id)
                if building_system:
                    # Calculate average dwelling size
                    avg_dwelling_size = 100.0  # square meters
                    
                    # Estimate number of dwellings based on population
                    dwellings = math.ceil(community.target_population / 2.5)  # Average household size
                    
                    # Calculate material requirements
                    total_area = dwellings * avg_dwelling_size
                    
                    for material in building_system.primary_materials:
                        if material in building_materials:
                            building_materials[material] += total_area / len(building_system.primary_materials)
                        else:
                            building_materials[material] = total_area / len(building_system.primary_materials)
            
            # Calculate infrastructure requirements
            infrastructure_requirements = {
                "road_length_km": math.sqrt(community.land_area_acres * 0.004) * 3,  # Approximate road network
                "water_storage_liters": community.target_population * 200,  # 200 liters per person
                "common_buildings": math.ceil(community.target_population / 200) + 3  # Community buildings
            }
            
            # Calculate energy requirements
            energy_requirements = {
                "daily_consumption_kwh": community.target_population * 2.5,  # Per person
                "peak_capacity_kw": community.target_population * 0.8,
                "storage_capacity_kwh": community.target_population * 3.0
            }
            
            # Calculate water requirements
            water_requirements = {
                "daily_consumption_liters": community.target_population * 150,  # 150 liters per person per day
                "irrigation_liters": sum(
                    self.food_systems.get(f_id).water_required_liters_per_day
                    for f_id in community.food_systems
                    if f_id in self.food_systems
                )
            }
            
            # Calculate food production capacity
            food_capacity = 0.0
            food_area_required = 0.0
            
            for system_id in community.food_systems:
                food_system = self.food_systems.get(system_id)
                if food_system:
                    # Calculate area based on scale
                    if food_system.production_type == "garden":
                        area = max(food_system.area_required_sqm * (community.target_population / 100), food_system.area_required_sqm)
                    elif food_system.production_type == "agroforestry":
                        area = max(food_system.area_required_sqm * (community.target_population / 50), food_system.area_required_sqm)
                    elif food_system.production_type == "grazing":
                        area = max(food_system.area_required_sqm * (community.target_population / 25), food_system.area_required_sqm)
                    else:
                        area = food_system.area_required_sqm * (community.target_population / 100)
                        
                    # Calculate calories produced
                    calories = area * food_system.typical_yield_calories_per_sqm
                    
                    # Add to totals
                    food_capacity += calories
                    food_area_required += area
                    
            # Calculate percentage of food self-sufficiency
            daily_calorie_needs = community.target_population * 2200  # 2200 calories per person per day
            annual_calorie_needs = daily_calorie_needs * 365
            annual_production = food_capacity * 365
            
            food_self_sufficiency = min(100.0, (annual_production / annual_calorie_needs) * 100) if annual_calorie_needs > 0 else 0
            
            # Calculate labor requirements
            core_team_size = max(3, math.ceil(community.target_population / 100))
            
            labor_requirements = {
                "core_planning_team": core_team_size,
                "construction_phase": math.ceil(dwellings / 4) + 5,  # Based on building needs
                "agricultural_workers": math.ceil(food_area_required / 10000)  # 1 worker per hectare
            }
            
            # Calculate implementation timeline
            total_implementation_months = max(
                phase["duration_months"] for phase in community.development_phases
            ) if community.development_phases else 60
            
            # Return all calculations
            return {
                "building_materials": building_materials,
                "infrastructure_requirements": infrastructure_requirements,
                "energy_requirements": energy_requirements,
                "water_requirements": water_requirements,
                "food_production": {
                    "annual_calories": annual_production,
                    "self_sufficiency_percent": food_self_sufficiency,
                    "area_required_sqm": food_area_required
                },
                "labor_requirements": labor_requirements,
                "implementation_timeline_months": total_implementation_months
            }
            
        except Exception as e:
            logger.error(f"Error calculating community requirements: {e}")
            return {"error": str(e)}


# ====================================================================
# 3. COLLABORATIVE RELOCATION NETWORK
# ====================================================================

class RelocationProjectStatus(Enum):
    """Status of relocation project."""
    PROPOSED = auto()       # Initial proposal stage
    PLANNING = auto()       # Active planning stage
    RECRUITING = auto()     # Recruiting participants
    PREPARING = auto()      # Preparations underway
    RELOCATING = auto()     # Active relocation happening
    ESTABLISHED = auto()    # Community established
    ON_HOLD = auto()        # Temporarily paused
    CANCELLED = auto()      # Project cancelled


class SkillCategory(Enum):
    """Categories of skills for relocation matching."""
    AGRICULTURE = auto()     # Farming, gardening, etc.
    BUILDING = auto()        # Construction, building trades
    ENERGY = auto()          # Renewable energy systems
    WATER = auto()           # Water management
    HEALTHCARE = auto()      # Medical, first aid, herbalism
    EDUCATION = auto()       # Teaching, facilitation
    GOVERNANCE = auto()      # Community organization
    MANUFACTURING = auto()   # Making, fabrication
    ECOLOGY = auto()         # Ecosystem knowledge
    CRAFT = auto()           # Traditional crafts
    TECHNOLOGY = auto()      # Digital, communications
    CARE = auto()            # Childcare, elder care


@dataclass
class HumanRelocator:
    """Human participant in relocation project."""
    human_id: str
    name: str
    current_region: str
    preferred_regions: List[str]
    skills: Dict[str, float]  # Skill category -> proficiency (0-1)
    interests: List[str]
    constraints: List[str]
    household_size: int
    has_children: bool
    preferred_community_scale: Optional[CommunityScale] = None
    preferred_community_focus: Optional[CommunityFocus] = None
    preferred_governance: Optional[GovernanceModel] = None
    relocation_timeline_months: Optional[int] = None
    resources_available: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RelocationProject:
    """Collaborative community relocation project."""
    project_id: str
    name: str
    target_region_id: str
    status: RelocationProjectStatus
    description: str
    community_model_id: Optional[str]  # Reference to Community template
    target_population: int
    current_participants: List[str]  # Human IDs
    project_coordinators: List[str]  # Human IDs of coordinators
    start_date: float
    projected_completion_date: Optional[float] = None
    land_status: str = "Seeking"  # "Seeking", "In negotiation", "Secured"
    project_phases: List[Dict[str, Any]] = field(default_factory=list)
    community_agreements: Dict[str, Any] = field(default_factory=dict)
    skill_coverage: Dict[str, float] = field(default_factory=dict)
    skill_gaps: Dict[str, float] = field(default_factory=dict)
    mutual_aid_partnerships: List[str] = field(default_factory=list)  # Other project IDs
    updates: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MutualAidOffer:
    """Offer of mutual aid between communities."""
    offer_id: str
    source_id: str  # Community or project ID
    target_id: str  # Community or project ID
    offer_type: str  # "skills", "resources", "knowledge", etc.
    description: str
    quantity: Optional[str] = None
    duration: Optional[str] = None
    conditions: List[str] = field(default_factory=list)
    status: str = "offered"  # "offered", "accepted", "fulfilled", "declined"
    contact_human_id: str = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class CollaborativeRelocationNetwork:
    """
    Network for coordinating collaborative relocation and community formation.
    """
    
    def __init__(self,
                bioregional_mapper: BioregionalMapper,
                community_designer: SustainableCommunityDesigner,
                data_path: str = "relocation_data"):
        """
        Initialize collaborative relocation network.
        
        Args:
            bioregional_mapper: Bioregional mapper
            community_designer: Sustainable community designer
            data_path: Path for storing relocation data
        """
        self.mapper = bioregional_mapper
        self.designer = community_designer
        self.data_path = data_path
        
        # Ensure paths exist
        os.makedirs(data_path, exist_ok=True)
        os.makedirs(os.path.join(data_path, "relocators"), exist_ok=True)
        os.makedirs(os.path.join(data_path, "projects"), exist_ok=True)
        os.makedirs(os.path.join(data_path, "aid_offers"), exist_ok=True)
        
        # Load data
        self.relocators: Dict[str, HumanRelocator] = {}
        self.projects: Dict[str, RelocationProject] = {}
        self.aid_offers: Dict[str, MutualAidOffer] = {}
        
        self._load_data()
    
    def _load_data(self) -> None:
        """Load relocation data from disk."""
        try:
            # Load relocators
            relocators_dir = os.path.join(self.data_path, "relocators")
            for filename in os.listdir(relocators_dir):
                if filename.endswith(".json"):
                    file_path = os.path.join(relocators_dir, filename)
                    try:
                        with open(file_path, "r") as f:
                            data = json.load(f)
                            
                            # Parse community scale preference if present
                            preferred_scale = None
                            if "preferred_community_scale" in data and data["preferred_community_scale"]:
                                preferred_scale = CommunityScale[data["preferred_community_scale"]]
                                
                            # Parse community focus preference if present
                            preferred_focus = None
                            if "preferred_community_focus" in data and data["preferred_community_focus"]:
                                preferred_focus = CommunityFocus[data["preferred_community_focus"]]
                                
                            # Parse governance preference if present
                            preferred_governance = None
                            if "preferred_governance" in data and data["preferred_governance"]:
                                preferred_governance = GovernanceModel[data["preferred_governance"]]
                            
                            relocator = HumanRelocator(
                                human_id=data.get("human_id", filename.replace(".json", "")),
                                name=data.get("name", "Unknown"),
                                current_region=data.get("current_region", ""),
                                preferred_regions=data.get("preferred_regions", []),
                                skills=data.get("skills", {}),
                                interests=data.get("interests", []),
                                constraints=data.get("constraints", []),
                                household_size=data.get("household_size", 1),
                                has_children=data.get("has_children", False),
                                preferred_community_scale=preferred_scale,
                                preferred_community_focus=preferred_focus,
                                preferred_governance=preferred_governance,
                                relocation_timeline_months=data.get("relocation_timeline_months"),
                                resources_available=data.get("resources_available", {}),
                                metadata=data.get("metadata", {})
                            )
                            self.relocators[relocator.human_id] = relocator
                    except Exception as e:
                        logger.error(f"Error loading relocator from {file_path}: {e}")
                        
            # Load projects
            projects_dir = os.path.join(self.data_path, "projects")
            for filename in os.listdir(projects_dir):
                if filename.endswith(".json"):
                    file_path = os.path.join(projects_dir, filename)
                    try:
                        with open(file_path, "r") as f:
                            data = json.load(f)
                            project = RelocationProject(
                                project_id=data.get("project_id", filename.replace(".json", "")),
                                name=data.get("name", "Unknown Project"),
                                target_region_id=data.get("target_region_id", ""),
                                status=RelocationProjectStatus[data.get("status", "PROPOSED")],
                                description=data.get("description", ""),
                                community_model_id=data.get("community_model_id"),
                                target_population=data.get("target_population", 0),
                                current_participants=data.get("current_participants", []),
                                project_coordinators=data.get("project_coordinators", []),
                                start_date=data.get("start_date", time.time()),
                                projected_completion_date=data.get("projected_completion_date"),
                                land_status=data.get("land_status", "Seeking"),
                                project_phases=data.get("project_phases", []),
                                community_agreements=data.get("community_agreements", {}),
                                skill_coverage=data.get("skill_coverage", {}),
                                skill_gaps=data.get("skill_gaps", {}),
                                mutual_aid_partnerships=data.get("mutual_aid_partnerships", []),
                                updates=data.get("updates", []),
                                metadata=data.get("metadata", {})
                            )
                            self.projects[project.project_id] = project
                    except Exception as e:
                        logger.error(f"Error loading project from {file_path}: {e}")
                        
            # Load aid offers
            aid_offers_dir = os.path.join(self.data_path, "aid_offers")
            for filename in os.listdir(aid_offers_dir):
                if filename.endswith(".json"):
                    file_path = os.path.join(aid_offers_dir, filename)
                    try:
                        with open(file_path, "r") as f:
                            data = json.load(f)
                            offer = MutualAidOffer(
                                offer_id=data.get("offer_id", filename.replace(".json", "")),
                                source_id=data.get("source_id", ""),
                                target_id=data.get("target_id", ""),
                                offer_type=data.get("offer_type", ""),
                                description=data.get("description", ""),
                                quantity=data.get("quantity"),
                                duration=data.get("duration"),
                                conditions=data.get("conditions", []),
                                status=data.get("status", "offered"),
                                contact_human_id=data.get("contact_human_id"),
                                metadata=data.get("metadata", {})
                            )
                            self.aid_offers[offer.offer_id] = offer
                    except Exception as e:
                        logger.error(f"Error loading aid offer from {file_path}: {e}")
                        
            logger.info(f"Loaded {len(self.relocators)} relocators, {len(self.projects)} projects, and {len(self.aid_offers)} aid offers")
            
        except Exception as e:
            logger.error(f"Error loading relocation data: {e}")
    
    def _save_relocator(self, relocator: HumanRelocator) -> None:
        """Save relocator to disk."""
        try:
            file_path = os.path.join(self.data_path, "relocators", f"{relocator.human_id}.json")
            
            # Format preferences for serialization
            preferred_scale = relocator.preferred_community_scale.name if relocator.preferred_community_scale else None
            preferred_focus = relocator.preferred_community_focus.name if relocator.preferred_community_focus else None
            preferred_governance = relocator.preferred_governance.name if relocator.preferred_governance else None
            
            # Prepare relocator data
            relocator_data = {
                "human_id": relocator.human_id,
                "name": relocator.name,
                "current_region": relocator.current_region,
                "preferred_regions": relocator.preferred_regions,
                "skills": relocator.skills,
                "interests": relocator.interests,
                "constraints": relocator.constraints,
                "household_size": relocator.household_size,
                "has_children": relocator.has_children,
                "preferred_community_scale": preferred_scale,
                "preferred_community_focus": preferred_focus,
                "preferred_governance": preferred_governance,
                "relocation_timeline_months": relocator.relocation_timeline_months,
                "resources_available": relocator.resources_available,
                "metadata": relocator.metadata
            }
            
            with open(file_path, "w") as f:
                json.dump(relocator_data, f, indent=2)
                
        except Exception as e:
            logger.error(f"Error saving relocator: {e}")
    
    def _save_project(self, project: RelocationProject) -> None:
        """Save project to disk."""
        try:
            file_path = os.path.join(self.data_path, "projects", f"{project.project_id}.json")
            
            # Prepare project data
            project_data = {
                "project_id": project.project_id,
                "name": project.name,
                "target_region_id": project.target_region_id,
                "status": project.status.name,
                "description": project.description,
                "community_model_id": project.community_model_id,
                "target_population": project.target_population,
                "current_participants": project.current_participants,
                "project_coordinators": project.project_coordinators,
                "start_date": project.start_date,
                "projected_completion_date": project.projected_completion_date,
                "land_status": project.land_status,
                "project_phases": project.project_phases,
                "community_agreements": project.community_agreements,
                "skill_coverage": project.skill_coverage,
                "skill_gaps": project.skill_gaps,
                "mutual_aid_partnerships": project.mutual_aid_partnerships,
                "updates": project.updates,
                "metadata": project.metadata
            }
            
            with open(file_path, "w") as f:
                json.dump(project_data, f, indent=2)
                
        except Exception as e:
            logger.error(f"Error saving project: {e}")
    
    def _save_aid_offer(self, offer: MutualAidOffer) -> None:
        """Save aid offer to disk."""
        try:
            file_path = os.path.join(self.data_path, "aid_offers", f"{offer.offer_id}.json")
            
            # Prepare offer data
            offer_data = {
                "offer_id": offer.offer_id,
                "source_id": offer.source_id,
                "target_id": offer.target_id,
                "offer_type": offer.offer_type,
                "description": offer.description,
                "quantity": offer.quantity,
                "duration": offer.duration,
                "conditions": offer.conditions,
                "status": offer.status,
                "contact_human_id": offer.contact_human_id,
                "metadata": offer.metadata
            }
            
            with open(file_path, "w") as f:
                json.dump(offer_data, f, indent=2)
                
        except Exception as e:
            logger.error(f"Error saving aid offer: {e}")
    
    def register_relocator(self, relocator: Dict[str, Any]) -> Dict[str, Any]:
        """
        Register a human relocator.
        
        Args:
            relocator: Relocator information
            
        Returns:
            Registration result
        """
        try:
            # Validate required fields
            required_fields = ["name", "current_region"]
            for field in required_fields:
                if field not in relocator:
                    return {
                        "success": False,
                        "error": f"Missing required field: {field}"
                    }
                    
            # Generate ID if not provided
            human_id = relocator.get("human_id")
            if not human_id:
                human_id = f"relocator_{hashlib.md5(f'{relocator['name']}_{time.time()}'.encode()).hexdigest()[:8]}"
                
            # Parse community scale preference if present
            preferred_scale = None
            if "preferred_community_scale" in relocator:
                try:
                    preferred_scale = CommunityScale[relocator["preferred_community_scale"]]
                except KeyError:
                    return {
                        "success": False,
                        "error": f"Invalid community scale: {relocator['preferred_community_scale']}"
                    }
                    
            # Parse community focus preference if present
            preferred_focus = None
            if "preferred_community_focus" in relocator:
                try:
                    preferred_focus = CommunityFocus[relocator["preferred_community_focus"]]
                except KeyError:
                    return {
                        "success": False,
                        "error": f"Invalid community focus: {relocator['preferred_community_focus']}"
                    }
                    
            # Parse governance preference if present
            preferred_governance = None
            if "preferred_governance" in relocator:
                try:
                    preferred_governance = GovernanceModel[relocator["preferred_governance"]]
                except KeyError:
                    return {
                        "success": False,
                        "error": f"Invalid governance model: {relocator['preferred_governance']}"
                    }
                    
            # Create relocator
            new_relocator = HumanRelocator(
                human_id=human_id,
                name=relocator["name"],
                current_region=relocator["current_region"],
                preferred_regions=relocator.get("preferred_regions", []),
                skills=relocator.get("skills", {}),
                interests=relocator.get("interests", []),
                constraints=relocator.get("constraints", []),
                household_size=relocator.get("household_size", 1),
                has_children=relocator.get("has_children", False),
                preferred_community_scale=preferred_scale,
                preferred_community_focus=preferred_focus,
                preferred_governance=preferred_governance,
                relocation_timeline_months=relocator.get("relocation_timeline_months"),
                resources_available=relocator.get("resources_available", {}),
                metadata=relocator.get("metadata", {})
            )
            
            # Add relocator
            self.relocators[human_id] = new_relocator
            
            # Save to disk
            self._save_relocator(new_relocator)
            
            return {
                "success": True,
                "human_id": human_id,
                "message": f"Registered relocator: {new_relocator.name}"
            }
            
        except Exception as e:
            logger.error(f"Error registering relocator: {e}")
            return {
                "success": False,
                "error": f"Registration error: {str(e)}"
            }
    
    def create_relocation_project(self, project: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new relocation project.
        
        Args:
            project: Project information
            
        Returns:
            Creation result
        """
        try:
            # Validate required fields
            required_fields = ["name", "target_region_id", "description"]
            for field in required_fields:
                if field not in project:
                    return {
                        "success": False,
                        "error": f"Missing required field: {field}"
                    }
                    
            # Check region validity
            region = self.mapper.get_region(project["target_region_id"])
            if not region:
                return {
                    "success": False,
                    "error": f"Invalid region ID: {project['target_region_id']}"
                }
                
            # Generate ID if not provided
            project_id = project.get("project_id")
            if not project_id:
                project_id = f"project_{hashlib.md5(f'{project['name']}_{time.time()}'.encode()).hexdigest()[:8]}"
                
            # Parse status
            try:
                status = RelocationProjectStatus[project.get("status", "PROPOSED")]
            except KeyError:
                return {
                    "success": False,
                    "error": f"Invalid project status: {project.get('status')}"
                }
                
            # Create project
            new_project = RelocationProject(
                project_id=project_id,
                name=project["name"],
                target_region_id=project["target_region_id"],
                status=status,
                description=project["description"],
                community_model_id=project.get("community_model_id"),
                target_population=project.get("target_population", 100),
                current_participants=project.get("current_participants", []),
                project_coordinators=project.get("project_coordinators", []),
                start_date=project.get("start_date", time.time()),
                projected_completion_date=project.get("projected_completion_date"),
                land_status=project.get("land_status", "Seeking"),
                project_phases=project.get("project_phases", []),
                community_agreements=project.get("community_agreements", {}),
                skill_coverage=project.get("skill_coverage", {}),
                skill_gaps=project.get("skill_gaps", {}),
                mutual_aid_partnerships=project.get("mutual_aid_partnerships", []),
                updates=[
                    {
                        "timestamp": time.time(),
                        "type": "creation",
                        "content": f"Project created targeting the {region.name} region."
                    }
                ],
                metadata=project.get("metadata", {})
            )
            
            # Add project
            self.projects[project_id] = new_project
            
            # Save to disk
            self._save_project(new_project)
            
            return {
                "success": True,
                "project_id": project_id,
                "message": f"Created relocation project: {new_project.name}"
            }
            
        except Exception as e:
            logger.error(f"Error creating project: {e}")
            return {
                "success": False,
                "error": f"Project creation error: {str(e)}"
            }
    
    def join_project(self, project_id: str, human_id: str, role: str = "participant") -> Dict[str, Any]:
        """
        Join a relocation project.
        
        Args:
            project_id: Project identifier
            human_id: Human identifier
            role: Role in project ("participant", "coordinator")
            
        Returns:
            Join result
        """
        # Check project exists
        if project_id not in self.projects:
            return {
                "success": False,
                "error": "Project not found"
            }
            
        # Check human exists
        if human_id not in self.relocators:
            return {
                "success": False,
                "error": "Relocator not found"
            }
            
        try:
            project = self.projects[project_id]
            relocator = self.relocators[human_id]
            
            # Check if already in project
            if human_id in project.current_participants:
                return {
                    "success": False,
                    "error": f"Human {relocator.name} is already a participant in this project"
                }
                
            # Add to project
            project.current_participants.append(human_id)
            
            # Add as coordinator if requested
            if role == "coordinator" and human_id not in project.project_coordinators:
                project.project_coordinators.append(human_id)
                
            # Update skill coverage
            self._update_project_skill_coverage(project)
            
            # Add update
            project.updates.append({
                "timestamp": time.time(),
                "type": "new_member",
                "content": f"{relocator.name} joined the project as a {role}."
            })
            
            # Save project
            self._save_project(project)
            
            return {
                "success": True,
                "project_id": project_id,
                "human_id": human_id,
                "message": f"{relocator.name} joined project as a {role}"
            }
            
        except Exception as e:
            logger.error(f"Error joining project: {e}")
            return {
                "success": False,
                "error": f"Join error: {str(e)}"
            }
    
    def find_matching_projects(self, human_id: str, max_results: int = 3) -> Dict[str, Any]:
        """
        Find relocation projects matching a human's preferences.
        
        Args:
            human_id: Human identifier
            max_results: Maximum number of results
            
        Returns:
            Matching projects
        """
        # Check human exists
        if human_id not in self.relocators:
            return {
                "success": False,
                "error": "Relocator not found"
            }
            
        try:
            relocator = self.relocators[human_id]
            matches = []
            
            # Match to all active projects
            for project in self.projects.values():
                # Skip if not in active status
                if project.status not in [RelocationProjectStatus.PROPOSED, 
                                         RelocationProjectStatus.PLANNING,
                                         RelocationProjectStatus.RECRUITING]:
                    continue
                    
                # Calculate match score
                score = self._calculate_project_match_score(relocator, project)
                
                # Include match details
                match = {
                    "project_id": project.project_id,
                    "project_name": project.name,
                    "match_score": score,
                    "region_id": project.target_region_id,
                    "region_name": self.mapper.get_region(project.target_region_id).name if self.mapper.get_region(project.target_region_id) else "Unknown",
                    "description": project.description,
                    "target_population": project.target_population,
                    "current_participants": len(project.current_participants),
                    "status": project.status.name,
                    "community_model": None,
                    "skill_gaps": project.skill_gaps
                }
                
                # Add community model details if available
                if project.community_model_id:
                    community = self.designer.get_community(project.community_model_id)
                    if community:
                        match["community_model"] = {
                            "name": community.name,
                            "scale": community.scale.name,
                            "focus": community.focus.name,
                            "governance": community.governance.name
                        }
                        
                matches.append(match)
                
            # Sort by match score
            matches.sort(key=lambda x: x["match_score"], reverse=True)
            
            # Return top matches
            return {
                "success": True,
                "human_id": human_id,
                "human_name": relocator.name,
                "matches": matches[:max_results],
                "total_projects_searched": len(self.projects)
            }
            
        except Exception as e:
            logger.error(f"Error finding matching projects: {e}")
            return {
                "success": False,
                "error": f"Matching error: {str(e)}"
            }
    
    def find_matching_humans(self, project_id: str, max_results: int = 10) -> Dict[str, Any]:
        """
        Find humans matching a project's needs.
        
        Args:
            project_id: Project identifier
            max_results: Maximum number of results
            
        Returns:
            Matching humans
        """
        # Check project exists
        if project_id not in self.projects:
            return {
                "success": False,
                "error": "Project not found"
            }
            
        try:
            project = self.projects[project_id]
            matches = []
            
            # Match to all relocators
            for relocator in self.relocators.values():
                # Skip if already in project
                if relocator.human_id in project.current_participants:
                    continue
                    
                # Calculate match score
                score = self._calculate_project_match_score(relocator, project)
                
                # Calculate skill match
                skill_match = {}
                for skill, gap in project.skill_gaps.items():
                    if gap > 0.3 and skill in relocator.skills:
                        skill_match[skill] = relocator.skills[skill]
                
                # Include match details
                match = {
                    "human_id": relocator.human_id,
                    "name": relocator.name,
                    "match_score": score,
                    "current_region": relocator.current_region,
                    "preferred_regions": relocator.preferred_regions,
                    "household_size": relocator.household_size,
                    "skill_match": skill_match,
                    "relocation_timeline_months": relocator.relocation_timeline_months
                }
                
                matches.append(match)
                
            # Sort by match score
            matches.sort(key=lambda x: x["match_score"], reverse=True)
            
            # Return top matches
            return {
                "success": True,
                "project_id": project_id,
                "project_name": project.name,
                "matches": matches[:max_results],
                "skill_gaps": project.skill_gaps,
                "total_relocators_searched": len(self.relocators)
            }
            
        except Exception as e:
            logger.error(f"Error finding matching humans: {e}")
            return {
                "success": False,
                "error": f"Matching error: {str(e)}"
            }
    
    def update_project_status(self, project_id: str, new_status: str, update_note: str = None) -> Dict[str, Any]:
        """
        Update project status.
        
        Args:
            project_id: Project identifier
            new_status: New status
            update_note: Optional update note
            
        Returns:
            Update result
        """
        # Check project exists
        if project_id not in self.projects:
            return {
                "success": False,
                "error": "Project not found"
            }
            
        try:
            # Parse status
            try:
                status = RelocationProjectStatus[new_status]
            except KeyError:
                return {
                    "success": False,
                    "error": f"Invalid project status: {new_status}"
                }
                
            project = self.projects[project_id]
            
            # Record old status
            old_status = project.status
            
            # Update status
            project.status = status
            
            # Add update
            note = update_note if update_note else f"Status changed from {old_status.name} to {status.name}"
            project.updates.append({
                "timestamp": time.time(),
                "type": "status_change",
                "content": note
            })
            
            # Save project
            self._save_project(project)
            
            return {
                "success": True,
                "project_id": project_id,
                "old_status": old_status.name,
                "new_status": status.name,
                "message": f"Updated project status: {status.name}"
            }
            
        except Exception as e:
            logger.error(f"Error updating project status: {e}")
            return {
                "success": False,
                "error": f"Status update error: {str(e)}"
            }
    
    def create_mutual_aid_offer(self, offer: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a mutual aid offer between communities.
        
        Args:
            offer: Offer information
            
        Returns:
            Creation result
        """
        try:
            # Validate required fields
            required_fields = ["source_id", "target_id", "offer_type", "description"]
            for field in required_fields:
                if field not in offer:
                    return {
                        "success": False,
                        "error": f"Missing required field: {field}"
                    }
                    
            # Generate ID if not provided
            offer_id = offer.get("offer_id")
            if not offer_id:
                offer_id = f"offer_{hashlib.md5(f'{offer['source_id']}_{offer['target_id']}_{time.time()}'.encode()).hexdigest()[:8]}"
                
            # Create offer
            new_offer = MutualAidOffer(
                offer_id=offer_id,
                source_id=offer["source_id"],
                target_id=offer["target_id"],
                offer_type=offer["offer_type"],
                description=offer["description"],
                quantity=offer.get("quantity"),
                duration=offer.get("duration"),
                conditions=offer.get("conditions", []),
                status=offer.get("status", "offered"),
                contact_human_id=offer.get("contact_human_id"),
                metadata=offer.get("metadata", {})
            )
            
            # Add offer
            self.aid_offers[offer_id] = new_offer
            
            # Save to disk
            self._save_aid_offer(new_offer)
            
            # Update project partnerships if both are projects
            if offer["source_id"] in self.projects and offer["target_id"] in self.projects:
                source_project = self.projects[offer["source_id"]]
                target_project = self.projects[offer["target_id"]]
                
                if target_project.project_id not in source_project.mutual_aid_partnerships:
                    source_project.mutual_aid_partnerships.append(target_project.project_id)
                    self._save_project(source_project)
                    
                if source_project.project_id not in target_project.mutual_aid_partnerships:
                    target_project.mutual_aid_partnerships.append(source_project.project_id)
                    self._save_project(target_project)
                
            return {
                "success": True,
                "offer_id": offer_id,
                "message": f"Created mutual aid offer from {offer['source_id']} to {offer['target_id']}"
            }
            
        except Exception as e:
            logger.error(f"Error creating mutual aid offer: {e}")
            return {
                "success": False,
                "error": f"Offer creation error: {str(e)}"
            }
    
    def update_aid_offer_status(self, offer_id: str, new_status: str, note: str = None) -> Dict[str, Any]:
        """
        Update status of a mutual aid offer.
        
        Args:
            offer_id: Offer identifier
            new_status: New status
            note: Optional note
            
        Returns:
            Update result
        """
        # Check offer exists
        if offer_id not in self.aid_offers:
            return {
                "success": False,
                "error": "Offer not found"
            }
            
        try:
            offer = self.aid_offers[offer_id]
            
            # Validate status
            valid_statuses = ["offered", "accepted", "fulfilled", "declined"]
            if new_status not in valid_statuses:
                return {
                    "success": False,
                    "error": f"Invalid status: {new_status}"
                }
                
            # Update status
            old_status = offer.status
            offer.status = new_status
            
            # Add note to metadata if provided
            if note:
                if "status_notes" not in offer.metadata:
                    offer.metadata["status_notes"] = []
                    
                offer.metadata["status_notes"].append({
                    "timestamp": time.time(),
                    "from_status": old_status,
                    "to_status": new_status,
                    "note": note
                })
                
            # Save offer
            self._save_aid_offer(offer)
            
            return {
                "success": True,
                "offer_id": offer_id,
                "old_status": old_status,
                "new_status": new_status,
                "message": f"Updated offer status: {new_status}"
            }
            
        except Exception as e:
            logger.error(f"Error updating offer status: {e}")
            return {
                "success": False,
                "error": f"Status update error: {str(e)}"
            }
    
    def _calculate_project_match_score(self, relocator: HumanRelocator, project: RelocationProject) -> float:
        """
        Calculate match score between relocator and project.
        
        Args:
            relocator: Human relocator
            project: Relocation project
            
        Returns:
            Match score (0.0 to 1.0)
        """
        score_components = []
        
        # Region preference
        region_score = 0.0
        if project.target_region_id in relocator.preferred_regions:
            region_score = 1.0
        elif not relocator.preferred_regions:  # No preferences specified
            region_score = 0.5
        score_components.append(("region", region_score))
        
        # Skill needs
        skill_score = 0.0
        if project.skill_gaps:
            skill_matches = 0
            for skill, gap in project.skill_gaps.items():
                if gap > 0.2 and skill in relocator.skills and relocator.skills[skill] > 0.5:
                    skill_matches += 1
                    
            skill_score = min(1.0, skill_matches / max(1, len(project.skill_gaps.keys()) / 2))
        else:
            skill_score = 0.5  # Neutral if no gaps defined
            
        score_components.append(("skills", skill_score))
        
        # Community model preferences
        community_score = 0.5  # Neutral default
        if project.community_model_id and relocator.preferred_community_scale:
            community = self.designer.get_community(project.community_model_id)
            if community:
                scale_match = relocator.preferred_community_scale == community.scale
                focus_match = relocator.preferred_community_focus == community.focus if relocator.preferred_community_focus else False
                governance_match = relocator.preferred_governance == community.governance if relocator.preferred_governance else False
                
                matches = sum([scale_match, focus_match, governance_match])
                if relocator.preferred_community_focus and relocator.preferred_governance:
                    community_score = matches / 3.0
                elif relocator.preferred_community_focus or relocator.preferred_governance:
                    community_score = matches / 2.0
                else:
                    community_score = matches / 1.0
                    
        score_components.append(("community", community_score))
        
        # Timeline compatibility
        timeline_score = 0.5  # Neutral default
        if relocator.relocation_timeline_months is not None:
            # Calculate approx project timeline
            if project.projected_completion_date:
                project_months = (project.projected_completion_date - time.time()) / (30 * 24 * 3600)
                timeline_diff = abs(relocator.relocation_timeline_months - project_months)
                timeline_score = max(0.0, 1.0 - (timeline_diff / 24))  # Within 24 months
            else:
                timeline_score = 0.5  # Neutral if no project timeline
                
        score_components.append(("timeline", timeline_score))
        
        # Current participants and preferred scale
        scale_score = 0.5  # Neutral default
        if relocator.preferred_community_scale:
            # Determine ideal population ranges for scales
            scale_sizes = {
                CommunityScale.NEIGHBORHOOD: (50, 150),
                CommunityScale.VILLAGE: (150, 500),
                CommunityScale.TOWN: (500, 2000),
                CommunityScale.SMALL_CITY: (2000, 10000),
                CommunityScale.REGIONAL_HUB: (10000, 50000)
            }
            
            ideal_range = scale_sizes.get(relocator.preferred_community_scale, (100, 500))
            if project.target_population >= ideal_range[0] and project.target_population <= ideal_range[1]:
                scale_score = 1.0
            else:
                # Calculate distance from range
                if project.target_population < ideal_range[0]:
                    distance = ideal_range[0] - project.target_population
                    scale_score = max(0.0, 1.0 - (distance / ideal_range[0]))
                else:
                    distance = project.target_population - ideal_range[1]
                    scale_score = max(0.0, 1.0 - (distance / ideal_range[1]))
                    
        score_components.append(("scale", scale_score))
        
        # Calculate weighted score
        weights = {
            "region": 0.3,
            "skills": 0.25,
            "community": 0.2,
            "timeline": 0.15,
            "scale": 0.1
        }
        
        weighted_score = sum(score * weights[name] for name, score in score_components)
        
        return weighted_score
    
    def _update_project_skill_coverage(self, project: RelocationProject) -> None:
        """
        Update skill coverage and gaps for a project.
        
        Args:
            project: Project to update
        """
        # Define standard skill categories to track
        standard_skills = {skill.name.lower(): 0.0 for skill in SkillCategory}
        
        # Initialize coverage
        skill_coverage = standard_skills.copy()
        
        # Calculate coverage from participants
        for human_id in project.current_participants:
            if human_id in self.relocators:
                relocator = self.relocators[human_id]
                
                # Add skills
                for skill, level in relocator.skills.items():
                    skill_lower = skill.lower()
                    if skill_lower in skill_coverage:
                        skill_coverage[skill_lower] = max(skill_coverage[skill_lower], level)
                    else:
                        skill_coverage[skill_lower] = level
                        
        # Calculate gaps
        skill_gaps = {}
        for skill, coverage in skill_coverage.items():
            if coverage < 0.7:  # Less than 70% coverage is a gap
                skill_gaps[skill] = 1.0 - coverage
                
        # Update project
        project.skill_coverage = skill_coverage
        project.skill_gaps = skill_gaps


# ====================================================================
# 4. TOWN INTRANET AND LOCAL KNOWLEDGE BASE
# ====================================================================

class KnowledgeCategory(Enum):
    """Categories for town knowledge base."""
    TECHNICAL = auto()       # Technical documentation
    ECOLOGICAL = auto()      # Ecological knowledge
    GOVERNANCE = auto()      # Governance processes
    SKILL = auto()           # Skill tutorials
    CULTURAL = auto()        # Cultural information
    HEALTH = auto()          # Health and medical
    INFRASTRUCTURE = auto()  # Infrastructure documentation
    LOCAL = auto()           # Local area knowledge
    EDUCATIONAL = auto()     # Educational materials
    HISTORICAL = auto()      # Historical records


class ResourceType(Enum):
    """Types of resources in town intranet."""
    DOCUMENT = auto()        # Text document
    VIDEO = auto()           # Video file
    AUDIO = auto()           # Audio file
    IMAGE = auto()           # Image file
    DATABASE = auto()        # Database
    INTERACTIVE = auto()     # Interactive application
    COLLECTION = auto()      # Collection of other resources
    GUIDE = auto()           # Step-by-step guide
    TEMPLATE = auto()        # Template document
    SOFTWARE = auto()        # Software application


@dataclass
class KnowledgeResource:
    """Knowledge resource in town knowledge base."""
    resource_id: str
    title: str
    description: str
    category: KnowledgeCategory
    resource_type: ResourceType
    file_path: str
    creator_id: Optional[str] = None
    created_date: float = field(default_factory=time.time)
    last_updated_date: float = field(default_factory=time.time)
    tags: List[str] = field(default_factory=list)
    related_resources: List[str] = field(default_factory=list)
    permissions: Dict[str, Any] = field(default_factory=dict)
    version: str = "1.0"
    size_bytes: Optional[int] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TownService:
    """Service available in town intranet."""Zone.OCEANIC, ClimateZone.HUMID_SUBTROPICAL
                ],
                advantages=[
                    "Uses familiar construction methods",
                    "Can achieve high insulation values",
                    "Reduced thermal bridging",
                    "More efficient use of lumber",
                    "Faster construction than many natural building methods",
                    "Adaptable to many designs"
                ],
                disadvantages=[
                    "Higher embodied carbon than some natural methods",
                    "Requires sustainably harvested wood to be truly ecological",
                    "Less thermal mass than earth-based systems",
                    "Requires careful air sealing",
                    "Less durable than some masonry techniques"
                ]
            )
        ]
        
        # Add systems
        for system in default_systems:
            self.building_systems[system.system_id] = system
            self._save_building_system(system)
            
        logger.info(f"Initialized {len(default_systems)} default building systems")
    
    def _initialize_default_energy_systems(self) -> None:
        """Initialize default energy systems."""
        default_systems = [
            # Solar PV with Battery Storage
            EnergySystem(
                system_id="solar_battery",
                name="Solar PV with Battery Storage",
                description="Grid-independent solar photovoltaic system with battery storage for 24/7 power availability.",
                energy_type="solar",
                capacity_range_kw=(2.0, 30.0),
                storage_included=True,
                storage_capacity_kwh=20.0,
                typical_output_kwh_per_year=1500.0,  # Per kW of capacity
                lifespan_years=25,
                maintenance_level=3,
                upfront_cost_per_kw=2500.0,
                region_suitability=["southwest", "pacific_northwest", "great_lakes", "new_england", "ozarks", "northern_plains"],
                climate_suitability=[c for c in ClimateZone],  # All climates
                advantages=[
                    "No fuel required",
                    "Minimal maintenance",
                    "Scalable for different needs",
                    "Silent operation",
                    "Battery provides emergency backup",
                    "Can be grid-tied or independent"
                ],
                disadvantages=[
                    "Initial cost can be high",
                    "Dependent on solar resource",
                    "Requires periodic battery replacement",
                    "Efficiency decreases in very cloudy conditions",
                    "Seasonal output variation"
                ]
            ),
            
            # Small-Scale Wind
            EnergySystem(
                system_id="small_wind",
                name="Small-Scale Wind Turbine System",
                description="Wind energy system sized for community or neighborhood use, with battery storage.",
                energy_type="wind",
                capacity_range_kw=(5.0, 100.0),
                storage_included=True,
                storage_capacity_kwh=50.0,
                typical_output_kwh_per_year=2000.0,  # Per kW of capacity
                lifespan_years=20,
                maintenance_level=6,
                upfront_cost_per_kw=3000.0,
                region_suitability=["northern_plains", "great_lakes", "new_england"],
                climate_suitability=[
                    ClimateZone.CONTINENTAL_HOT, ClimateZone.CONTINENTAL_WARM, ClimateZone.CONTINENTAL_COOL,
                    ClimateZone.OCEANIC, ClimateZone.SUBARCTIC, ClimateZone.TUNDRA
                ],
                advantages=[
                    "Works during day and night",
                    "Complements solar in many regions",
                    "Higher output in winter (when solar is lower)",
                    "Can generate substantial power with good wind resource",
                    "Lower land use than solar for equivalent output"
                ],
                disadvantages=[
                    "Requires steady wind resource",
                    "More maintenance than solar",
                    "Moving parts require periodic replacement",
                    "Visual impact on landscape",
                    "Noise can be an issue for some designs"
                ]
            ),
            
            # Micro-Hydro
            EnergySystem(
                system_id="micro_hydro",
                name="Micro-Hydroelectric System",
                description="Small-scale hydroelectric generation using flowing water from streams or rivers, providing continuous power generation.",
                energy_type="hydro",
                capacity_range_kw=(1.0, 100.0),
                storage_included=False,
                storage_capacity_kwh=0.0,
                typical_output_kwh_per_year=8760.0,  # Per kW of capacity (24/7 operation)
                lifespan_years=30,
                maintenance_level=5,
                upfront_cost_per_kw=4000.0,
                region_suitability=["pacific_northwest", "new_england", "ozarks"],
                climate_suitability=[
                    ClimateZone.RAINFOREST, ClimateZone.MONSOON, ClimateZone.OCEANIC,
                    ClimateZone.CONTINENTAL_COOL, ClimateZone.HUMID_SUBTROPICAL
                ],
                advantages=[
                    "Continuous power generation (day and night)",
                    "Highly reliable and predictable",
                    "Long system lifespan",
                    "Low environmental impact when properly designed",
                    "High capacity factor compared to solar and wind",
                    "May not require battery storage"
                ],
                disadvantages=[
                    "Geographically limited to suitable water sources",
                    "Seasonal flow variations affect output",
                    "Requires water rights and permits",
                    "Intake systems require maintenance (debris clearing)",
                    "Environmental considerations for aquatic ecosystems"
                ]
            ),
            
            # Biogas Digester
            EnergySystem(
                system_id="biogas",
                name="Biogas Digestion System",
                description="Anaerobic digestion system that converts organic waste into biogas for cooking, heating, or electricity generation.",
                energy_type="biomass",
                capacity_range_kw=(5.0, 50.0),
                storage_included=True,
                storage_capacity_kwh=15.0,
                typical_output_kwh_per_year=6000.0,  # Per kW of capacity
                lifespan_years=20,
                maintenance_level=7,
                upfront_cost_per_kw=2000.0,
                region_suitability=["great_lakes", "ozarks", "new_england"],
                climate_suitability=[
                    ClimateZone.CONTINENTAL_HOT, ClimateZone.CONTINENTAL_WARM, ClimateZone.HUMID_SUBTROPICAL,
                    ClimateZone.OCEANIC
                ],
                advantages=[
                    "Uses waste materials as fuel",
                    "Produces fertilizer as byproduct",
                    "Can process agricultural and food waste",
                    "Reduces methane emissions from organic waste",
                    "Provides on-demand energy unlike solar/wind",
                    "Doesn't depend on weather conditions"
                ],
                disadvantages=[
                    "Requires regular feeding with organic material",
                    "More complex operation than solar",
                    "Temperature sensitive (less effective in cold climates without heating)",
                    "Requires management of digester biology",
                    "Needs adequate organic waste stream"
                ]
            ),
            
            # Geothermal Heat Pump
            EnergySystem(
                system_id="geothermal_heat",
                name="Geothermal Heat Pump System",
                description="Ground-source heat pump system for highly efficient heating and cooling using stable underground temperatures.",
                energy_type="geothermal",
                capacity_range_kw=(3.0, 30.0),
                storage_included=False,
                storage_capacity_kwh=0.0,
                typical_output_kwh_per_year=10000.0,  # Equivalent heat energy output
                lifespan_years=25,
                maintenance_level=4,
                upfront_cost_per_kw=5000.0,
                region_suitability=["great_lakes", "new_england", "northern_plains", "pacific_northwest"],
                climate_suitability=[
                    ClimateZone.CONTINENTAL_HOT, ClimateZone.CONTINENTAL_WARM, ClimateZone.CONTINENTAL_COOL,
                    Climate, '')) for req in hardware_requirements) if hardware_requirements else 0}",
                "estimated_deployment_time": "3-4 weeks"
            }
            
        except Exception as e:
            logger.error(f"Error generating deployment guide: {e}")
            return {
                "success": False,
                "error": f"Guide generation error: {str(e)}"
            }
    
    def generate_kiwix_collection_plan(self) -> Dict[str, Any]:
        """
        Generate a plan for creating a comprehensive Kiwix collection.
        
        Returns:
            Kiwix collection plan
        """
        try:
            # Core ZIM collections
            core_collections = [
                {
                    "name": "Wikipedia (Simple English)",
                    "description": "Simple English version of Wikipedia with basic articles",
                    "filename": "wikipedia_en_simple_all_maxi.zim",
                    "size_gb": 0.5,
                    "language": "English (Simple)",
                    "priority": "High",
                    "url": "https://download.kiwix.org/zim/wikipedia/",
                    "update_frequency": "Annual",
                    "notes": "Good starting point for general knowledge, uses simpler language"
                },
                {
                    "name": "Wikipedia (English Selection)",
                    "description": "Selection of the most important Wikipedia articles",
                    "filename": "wikipedia_en_top_maxi.zim",
                    "size_gb": 1.5,
                    "language": "English",
                    "priority": "High",
                    "url": "https://download.kiwix.org/zim/wikipedia/",
                    "update_frequency": "Annual",
                    "notes": "Balanced size vs. coverage for general knowledge"
                },
                {
                    "name": "Wiktionary English",
                    "description": "English dictionary with definitions, etymology, pronunciations",
                    "filename": "wiktionary_en_all_maxi.zim",
                    "size_gb": 1.2,
                    "language": "English",
                    "priority": "Medium",
                    "url": "https://download.kiwix.org/zim/wiktionary/",
                    "update_frequency": "Annual",
                    "notes": "Valuable language resource"
                },
                {
                    "name": "WikiMed Medical Encyclopedia",
                    "description": "Medical information from Wikipedia",
                    "filename": "wikimed_en_all_maxi.zim",
                    "size_gb": 1.1,
                    "language": "English",
                    "priority": "High",
                    "url": "https://download.kiwix.org/zim/wikimed/",
                    "update_frequency": "Annual",
                    "notes": "Critical healthcare information"
                },
                {
                    "name": "Wikiversity",
                    "description": "Learning resources, projects, and research for learners",
                    "filename": "wikiversity_en_all_maxi.zim",
                    "size_gb": 0.7,
                    "language": "English",
                    "priority": "Medium",
                    "url": "https://download.kiwix.org/zim/wikiversity/",
                    "update_frequency": "Annual",
                    "notes": "Educational content for community learning"
                },
                {
                    "name": "Wikibooks",
                    "description": "Open-content textbooks and manuals",
                    "filename": "wikibooks_en_all_maxi.zim",
                    "size_gb": 0.8,
                    "language": "English",
                    "priority": "Medium",
                    "url": "https://download.kiwix.org/zim/wikibooks/",
                    "update_frequency": "Annual",
                    "notes": "Practical educational resources"
                },
                {
                    "name": "WikiHow",
                    "description": "How-to guides for practical skills",
                    "filename": "wikihow_en_all_maxi.zim",
                    "size_gb": 0.9,
                    "language": "English",
                    "priority": "High",
                    "url": "https://download.kiwix.org/zim/wikihow/",
                    "update_frequency": "Annual",
                    "notes": "Practical skills and how-to knowledge"
                },
                {
                    "name": "Gutenberg Project",
                    "description": "Collection of free e-books",
                    "filename": "gutenberg_en_all_maxi.zim",
                    "size_gb": 14.0,
                    "language": "English",
                    "priority": "Low",
                    "url": "https://download.kiwix.org/zim/gutenberg/",
                    "update_frequency": "Annual",
                    "notes": "Cultural knowledge, literature, vast but large size"
                },
                {
                    "name": "Stack Exchange",
                    "description": "Question and answer collection from Stack Exchange",
                    "filename": "stackexchange_en_all_maxi.zim",
                    "size_gb": 6.5,
                    "language": "English",
                    "priority": "Medium",
                    "url": "https://download.kiwix.org/zim/stackexchange/",
                    "update_frequency": "Annual",
                    "notes": "Technical questions and answers on many topics"
                }
            ]
            
            # Technical collections
            technical_collections = [
                {
                    "name": "PhET Interactive Simulations",
                    "description": "Interactive science and math simulations",
                    "filename": "phet_en.zim",
                    "size_gb": 0.1,
                    "language": "English",
                    "priority": "Medium",
                    "url": "https://download.kiwix.org/zim/phet/",
                    "update_frequency": "Annual",
                    "notes": "Educational simulations that work offline"
                },
                {
                    "name": "Architecture for Humanity",
                    "description": "Designs for sustainable architecture",
                    "filename": "architecture_en.zim",
                    "size_gb": 0.3,
                    "language": "English",
                    "priority": "Medium",
                    "url": "https://download.kiwix.org/zim/other/",
                    "update_frequency": "Rarely",
                    "notes": "Sustainable building designs and information"
                },
                {
                    "name": "Practical Plants",
                    "description": "Database of plants and their practical uses",
                    "filename": "practicalplants_en.zim",
                    "size_gb": 0.2,
                    "language": "English",
                    "priority": "High",
                    "url": "https://download.kiwix.org/zim/other/",
                    "update_frequency": "Occasional",
                    "notes": "Essential for permaculture and food forest planning"
                },
                {
                    "name": "Open Textbooks",
                    "description": "Collection of open educational textbooks",
                    "filename": "openstax_en.zim",
                    "size_gb": 2.3,
                    "language": "English",
                    "priority": "Medium",
                    "url": "https://download.kiwix.org/zim/other/",
                    "update_frequency": "Annual",
                    "notes": "Comprehensive educational resources"
                },
                {
                    "name": "MDFiles Medical Information",
                    "description": "Medical reference material",
                    "filename": "mdfiles_en.zim",
                    "size_gb": 0.4,
                    "language": "English",
                    "priority": "High",
                    "url": "https://download.kiwix.org/zim/other/",
                    "update_frequency": "Annual",
                    "notes": "Additional medical resources beyond WikiMed"
                }
            ]
            
            # Custom ZIM collections to create
            custom_collections = [
                {
                    "name": "Permaculture Design Library",
                    "description": "Curated collection of permaculture design documents, books, and resources",
                    "estimated_size_gb": 0.5,
                    "source_materials": "PDFs, websites, videos on permaculture design",
                    "creation_tools": "Zimit or similar ZIM creation tools",
                    "priority": "High",
                    "notes": "Focus on region-specific permaculture information"
                },
                {
                    "name": "Resilient Technology Manual",
                    "description": "Technical manuals for appropriate technologies and resilient systems",
                    "estimated_size_gb": 0.8,
                    "source_materials": "Technical documentation, manuals, diagrams",
                    "creation_tools": "Zimit with custom scripts",
                    "priority": "High",
                    "notes": "Include maintenance guides and troubleshooting"
                },
                {
                    "name": "Local Ecology Database",
                    "description": "Region-specific ecological information, species guides, and ecosystem patterns",
                    "estimated_size_gb": 0.3,
                    "source_materials": "Local ecological studies, field guides, observations",
                    "creation_tools": "Custom web scraping + Zimit",
                    "priority": "High",
                    "notes": "Requires local knowledge input"
                },
                {
                    "name": "DIY Medicine Guide",
                    "description": "First aid, herbalism, and emergency medical information",
                    "estimated_size_gb": 0.4,
                    "source_materials": "Medical texts, herbal guides, emergency procedures",
                    "creation_tools": "Zimit",
                    "priority": "High",
                    "notes": "Focus on treatments using locally available resources"
                },
                {
                    "name": "Bioregional History Archive",
                    "description": "Local historical information, cultural knowledge, and traditional practices",
                    "estimated_size_gb": 0.2,
                    "source_materials": "Historical documents, interviews, local resources",
                    "creation_tools": "Manual collection + Zimit",
                    "priority": "Medium",
                    "notes": "Requires extensive local research"
                }
            ]
            
            # Kiwix setup guidelines
            setup_guidelines = [
                {
                    "phase": "Hardware Setup",
                    "steps": [
                        "Procure a Raspberry Pi 4 (4GB+ RAM) or similar device",
                        "Set up with 64-bit OS (Raspberry Pi OS or Ubuntu)",
                        "Connect external storage (SSD or HDD) for ZIM files",
                        "Configure reliable power supply with backup",
                        "Configure networking (WiFi + Ethernet preferred)"
                    ],
                    "estimated_time": "1 day",
                    "requirements": "Raspberry Pi, storage media, power supply, networking equipment"
                },
                {
                    "phase": "Software Installation",
                    "steps": [
                        "Install Kiwix Server (kiwix-serve) on the Raspberry Pi",
                        "Configure autostart on boot",
                        "Set up local DNS (if possible) for easy access",
                        "Configure web interface for browsing",
                        "Install additional tools (kiwix-tools package)",
                        "Configure backup and update scripts"
                    ],
                    "estimated_time": "0.5 days",
                    "requirements": "Internet connection for initial setup, technical knowledge"
                },
                {
                    "phase": "Content Acquisition",
                    "steps": [
                        "Create directory structure for organizing ZIM files",
                        "Download high-priority ZIM files using direct connection or sneakernet",
                        "Verify downloaded files with checksums",
                        "Organize files by category",
                        "Create and maintain content inventory"
                    ],
                    "estimated_time": "1-7 days (depending on internet speed and file size)",
                    "requirements": "Internet connection or alternative access to ZIM files, storage space"
                },
                {
                    "phase": "Custom Content Creation",
                    "steps": [
                        "Install Zimit or similar ZIM creation tools",
                        "Collect and organize local knowledge materials",
                        "Process and convert materials to web format",
                        "Create custom ZIM files with appropriate metadata",
                        "Test and optimize custom ZIM files"
                    ],
                    "estimated_time": "7-14 days per collection (ongoing)",
                    "requirements": "Source materials, technical knowledge, community participation"
                },
                {
                    "phase": "Deployment and Use",
                    "steps": [
                        "Configure Kiwix to serve all ZIM files",
                        "Set up access controls if needed",
                        "Create simple instructional materials for users",
                        "Train community members on usage",
                        "Establish regular maintenance schedule"
                    ],
                    "estimated_time": "1 day",
                    "requirements": "Completed prior phases, community involvement"
                }
            ]
            
            # Maintenance and update procedures
            maintenance_procedures = [
                {
                    "category": "Regular Backups",
                    "frequency": "Monthly",
                    "procedures": [
                        "Create backup of custom ZIM files",
                        "Backup Kiwix configuration",
                        "Verify backup integrity",
                        "Store backup in separate location"
                    ],
                    "responsibility": "System administrator"
                },
                {
                    "category": "Content Updates",
                    "frequency": "Annual",
                    "procedures": [
                        "Check for updated versions of core ZIM files",
                        "Download and verify updated files",
                        "Replace old versions while retaining custom content",
                        "Update content inventory"
                    ],
                    "responsibility": "Knowledge keeper"
                },
                {
                    "category": "System Maintenance",
                    "frequency": "Quarterly",
                    "procedures": [
                        "Check system logs for errors",
                        "Update Kiwix software",
                        "Clean storage and check for issues",
                        "Optimize performance if needed"
                    ],
                    "responsibility": "System administrator"
                },
                {
                    "category": "Content Expansion",
                    "frequency": "Ongoing",
                    "procedures": [
                        "Identify knowledge gaps",
                        "Collect and prepare new materials",
                        "Create new custom ZIM files",
                        "Integrate with existing collection"
                    ],
                    "responsibility": "Knowledge team"
                },
                {
                    "category": "Usage Monitoring",
                    "frequency": "Monthly",
                    "procedures": [
                        "Review access logs if enabled",
                        "Identify most-used content",
                        "Survey community for needs",
                        "Adjust content priorities based on usage"
                    ],
                    "responsibility": "Community coordinator"
                }
            ]
            
            # Integration with town intranet
            intranet_integration = [
                {
                    "aspect": "Technical Integration",
                    "methods": [
                        "Add Kiwix as a service in the intranet configuration",
                        "Create direct links from intranet homepage",
                        "Configure same authentication if appropriate",
                        "Ensure consistent network access"
                    ],
                    "requirements": "API access or service configuration"
                },
                {
                    "aspect": "Search Integration",
                    "methods": [
                        "Configure unified search across intranet and Kiwix",
                        "Index ZIM content in intranet search",
                        "Create specialized search interfaces for different content types",
                        "Implement cross-referencing between resources"
                    ],
                    "requirements": "Search API access, indexing tools"
                },
                {
                    "aspect": "Content Cross-Reference",
                    "methods": [
                        "Tag intranet content with references to relevant Kiwix articles",
                        "Create curated knowledge paths that include both sources",
                        "Implement contextual linking between related materials",
                        "Develop viewing interfaces that combine sources"
                    ],
                    "requirements": "Content management system"
                },
                {
                    "aspect": "LLM Integration",
                    "methods": [
                        "Configure local LLMs to reference Kiwix content",
                        "Create specialized retrieval-augmented generation using ZIM files",
                        "Train embedding models on Kiwix content for semantic search",
                        "Implement citation system for LLM outputs"
                    ],
                    "requirements": "LLM API access, vector database"
                }
            ]
            
            # Return complete Kiwix plan
            return {
                "success": True,
                "core_collections": core_collections,
                "technical_collections": technical_collections,
                "custom_collections": custom_collections,
                "total_size_gb": sum(collection["size_gb"] for collection in core_collections + technical_collections) + sum(collection["estimated_size_gb"] for collection in custom_collections),
                "setup_guidelines": setup_guidelines,
                "maintenance_procedures": maintenance_procedures,
                "intranet_integration": intranet_integration,
                "recommended_hardware": {
                    "processor": "Raspberry Pi 4 (4GB+ RAM) or equivalent",
                    "storage": "1TB+ SSD or HDD",
                    "networking": "WiFi + Ethernet, mesh capability preferred",
                    "power": "Low-power with battery backup capability",
                    "estimated_cost": "$150-300 (excluding storage)"
                }
            }
            
        except Exception as e:
            logger.error(f"Error generating Kiwix plan: {e}")
            return {
                "success": False,
                "error": f"Plan generation error: {str(e)}"
            }


# ====================================================================
# 5. GAIA BIOREGIONAL HARMONY MODULE
# ====================================================================

class GaiaBioregionalHarmony:
    """
    Main module for bioregional rebalancing, collaborative relocation,
    and sustainable community development.
    """
    
    def __init__(self,
                pulse_engine: Optional[Any] = None,
                data_path: str = "gaia_data",
                config: Dict[str, Any] = None):
        """
        Initialize Gaia Bioregional Harmony module.
        
        Args:
            pulse_engine: PulseHuman engine (optional)
            data_path: Path for storing Gaia data
            config: Additional configuration
        """
        self.pulse_engine = pulse_engine
        self.data_path = data_path
        self.config = config or {}
        
        # Ensure paths exist
        os.makedirs(data_path, exist_ok=True)
        
        # Initialize core components
        self.bioregional_mapper = BioregionalMapper(
            data_path=os.path.join(data_path, "bioregional_data")
        )
        
        self.community_designer = SustainableCommunityDesigner(
            bioregional_mapper=self.bioregional_mapper,
            data_path=os.path.join(data_path, "community_data")
        )
        
        self.relocation_network = CollaborativeRelocationNetwork(
            bioregional_mapper=self.bioregional_mapper,
            community_designer=self.community_designer,
            data_path=os.path.join(data_path, "relocation_data")
        )
        
        self.intranet_builder = TownIntranetBuilder(
            data_path=os.path.join(data_path, "intranet_data")
        )
        
        # Integration with PulseHuman
        self.is_initialized = False
        self.human_progress: Dict[str, Dict[str, Any]] = {}
        
        # Create default activities
        self.activities = self._create_default_activities()
    
    async def initialize(self) -> Dict[str, Any]:
        """
        Initialize Gaia Bioregional Harmony module.
        
        Returns:
            Initialization results
        """
        if self.is_initialized:
            return {
                "success": True,
                "message": "Already initialized"
            }
            
        try:
            # Add activities to PulseHuman if available
            if self.pulse_engine and hasattr(self.pulse_engine, "activities"):
                for activity in self.activities:
                    self.pulse_engine.activities.add_activity(activity)
                    
                logger.info(f"Added {len(self.activities)} Gaia activities to PulseHuman")
                
            # Load human progress
            progress_path = os.path.join(self.data_path, "human_progress.json")
            
            if os.path.exists(progress_path):
                try:
                    with open(progress_path, "r") as f:
                        self.human_progress = json.load(f)
                except Exception as e:
                    logger.error(f"Error loading human progress: {e}")
                    
            # Set initialized flag
            self.is_initialized = True
            
            logger.info("Initialized Gaia Bioregional Harmony module")
            
            return {
                "success": True,
                "message": "Initialized Gaia Bioregional Harmony module",
                "components": {
                    "bioregional_mapper": True,
                    "community_designer": True,
                    "relocation_network": True,
                    "intranet_builder": True
                }
            }
            
        except Exception as e:
            logger.error(f"Error initializing Gaia Bioregional Harmony: {e}")
            
            return {
                "success": False,
                "error": f"Initialization error: {str(e)}"
            }
    
    def _create_default_activities(self) -> List[DevelopmentalActivity]:
        """Create default Gaia activities for PulseHuman."""
        activities = [
            # Bioregional Awareness
            DevelopmentalActivity(
                activity_id="gaia_bioregional_awareness",
                name="Bioregional Awareness Mapping",
                description="Develop awareness of your local bioregion through mapping exercises that identify watersheds, ecosystems, and human systems.",
                target_stage=DevelopmentalStage.GAIA,
                mode=HumanDevelopmentalMode.ECOLOGICAL,
                duration_minutes=60,
                difficulty=2,
                materials_needed=["Local maps", "Drawing materials", "Field guide (optional)"],
                instructions=[
                    "Find or create a map of your local area (5-50 mile radius).",
                    "Identify and draw the watershed boundaries - where does water flow?",
                    "Mark the dominant ecosystem types and transitions between them.",
                    "Identify critical resources: water sources, agricultural land, forests.",
                    "Map human settlements and infrastructure in relation to natural features.",
                    "Note areas of ecological health and areas of degradation or stress."
                ],
                reflection_questions=[
                    "What patterns do you notice between natural systems and human settlement?",
                    "How do resources flow through your bioregion?",
                    "What areas seem most vulnerable to disruption or climate change?",
                    "How well-matched are human systems to the natural capacity of your bioregion?"
                ],
                emotional_benefits=["Connection to place", "Ecological awareness", "Systems thinking"],
                associated_values=["Bioregionalism", "Ecological harmony", "Place-based knowledge"]
            ),
            
            # Collaborative Visioning
            DevelopmentalActivity(
                activity_id="gaia_collaborative_visioning",
                name="Collaborative Community Visioning",
                description="Practice collaborative visioning for resilient community development that works with bioregional characteristics.",
                target_stage=DevelopmentalStage.GAIA,
                mode=HumanDevelopmentalMode.COLLABORATIVE,
                duration_minutes=120,
                difficulty=3,
                materials_needed=["Large paper", "Drawing materials", "Bioregional awareness map"],
                instructions=[
                    "Gather a small group of 3-7 people interested in community resilience.",
                    "Begin with a short bioregional awareness sharing, where each person notes key characteristics of your shared region.",
                    "Identify the region's strengths, vulnerabilities, and carrying capacity.",
                    "Collectively envision what a harmonious human presence would look like in 25 years.",
                    "Map out where key resources and systems would be located.",
                    "Discuss governance models that would support this vision.",
                    "Identify key steps toward this vision that could be taken now."
                ],
                reflection_questions=[
                    "What tensions or differences emerged in the visioning process?",
                    "How did the vision account for ecological limits and regeneration needs?",
                    "What existing communities or projects might be aligned with this vision?",
                    "What barriers exist to moving toward this vision?"
                ],
                emotional_benefits=["Collective hope", "Shared purpose", "Agency"],
                associated_values=["Collaborative governance", "Ecological design", "Long-term thinking"]
            ),
            
            # Resource Flow Mapping
            DevelopmentalActivity(
                activity_id="gaia_resource_flow_mapping",
                name="Community Resource Flow Mapping",
                description="Map the flow of key resources through your community to identify resilience gaps and regenerative opportunities.",
                target_stage=DevelopmentalStage.GAIA,
                mode=HumanDevelopmentalMode.ECOLOGICAL,
                duration_minutes=90,
                difficulty=4,
                materials_needed=["Large paper", "Colored markers", "Post-it notes"],
                instructions=[
                    "Select 3-5 key resources to track (e.g., food, water, energy, materials, information).",
                    "For each resource, map where it currently comes from (sources).",
                    "Track how it moves through your community (flows).",
                    "Identify where it goes after use (sinks).",
                    "Mark critical vulnerabilities in red (external dependencies, non-renewable sources).",
                    "Mark regenerative opportunities in green (circular potential, untapped local sources).",
                    "For each vulnerability, brainstorm at least one more resilient alternative."
                ],
                reflection_questions=[
                    "Which resources have the most concerning vulnerabilities?",
                    "Where are the greatest opportunities for creating circular flows?",
                    "What skills and infrastructure would be needed to improve resilience?",
                    "How would climate disruption affect these resource flows?"
                ],
                emotional_benefits=["Clarity", "Strategic thinking", "Practical hope"],
                associated_values=["Resource sovereignty", "Circular economy", "Practical resilience"]
            ),
            
            # Relocation Planning
            DevelopmentalActivity(
                activity_id="gaia_relocation_planning",
                name="Ethical Relocation Planning",
                description="Develop a framework for ethical relocation that considers bioregional carrying capacity and collaborative potential.",
                target_stage=DevelopmentalStage.GAIA,
                mode=HumanDevelopmentalMode.REFLECTIVE,
                duration_minutes=60,
                difficulty=3,
                materials_needed=["Journal", "Map of potential regions", "Skills inventory"],
                instructions=[
                    "Reflect on your current living location's long-term resilience and alignment with your values.",
                    "Create an inventory of your skills, resources, and needs.",
                    "Research 2-3 potential bioregions that may be better aligned with resilience needs.",
                    "For each region, assess carrying capacity, current population, and ecological health.",
                    "Consider what you could contribute to each region.",
                    "Research existing communities or initiatives in each region.",
                    "Draft a timeline and resource plan for potential relocation.",
                    "Identify key questions and connections needed before decisions can be made."
                ],
                reflection_questions=[
                    "What ethical considerations arise when thinking about relocating?",
                    "How can relocation be done in ways that strengthen rather than strain receiving bioregions?",
                    "What community models in potential locations align with your values?",
                    "What skills would you need to develop to contribute effectively?"
                ],
                emotional_benefits=["Clarity", "Agency", "Purposeful planning"],
                associated_values=["Bioregional harmony", "Ethical migration", "Community contribution"]
            ),
            
            # Knowledge Preservation
            DevelopmentalActivity(
                activity_id="gaia_knowledge_preservation",
                name="Community Knowledge System Design",
                description="Design a system for preserving and sharing critical knowledge within a resilient community.",
                target_stage=DevelopmentalStage.GAIA,
                mode=HumanDevelopmentalMode.EDUCATIONAL,
                duration_minutes=90,
                difficulty=3,
                materials_needed=["Paper", "Reference materials on knowledge systems"],
                instructions=[
                    "Identify categories of knowledge critical for community resilience.",
                    "For each category, list specific knowledge areas and skills.",
                    "Design a physical and digital system for knowledge preservation.",
                    "Create a plan for knowledge transmission across generations.",
                    "Develop protocols for integrating new knowledge while preserving core wisdom.",
                    "Consider redundancy, accessibility, and longevity in your design.",
                    "Identify specific technologies and practices that support this system."
                ],
                reflection_questions=[
                    "What knowledge is most critical to preserve for future generations?",
                    "How can both traditional wisdom and modern technical knowledge be honored?",
                    "What are the vulnerabilities in current knowledge preservation systems?",
                    "How can knowledge be made accessible while being protected from misuse?"
                ],
                emotional_benefits=["Cultural continuity", "Wisdom appreciation", "Intergenerational thinking"],
                associated_values=["Knowledge commons", "Intergenerational equity", "Cultural preservation"]
            ),
            
            # Mutual Aid Network Design
            DevelopmentalActivity(
                activity_id="gaia_mutual_aid_network",
                name="Bioregional Mutual Aid Network Design",
                description="Design a mutual aid network that connects communities within a bioregion for resilience and resource sharing.",
                target_stage=DevelopmentalStage.GAIA,
                mode=HumanDevelopmentalMode.COLLABORATIVE,
                duration_minutes=120,
                difficulty=4,
                materials_needed=["Large paper", "Map of bioregion", "Markers"],
                instructions=[
                    "Map existing communities and projects within your bioregion.",
                    "Identify the strengths, resources, and surpluses of each community.",
                    "Identify needs and vulnerabilities of each community.",
                    "Design complementary relationships between communities based on strengths and needs.",
                    "Create protocols for resource sharing during normal times and emergencies.",
                    "Design communication systems that can function during disruptions.",
                    "Develop governance structures for network decisions.",
                    "Create metrics for evaluating the health of the mutual aid relationships."
                ],
                reflection_questions=[
                    "How can communities with different values and practices work together effectively?",
                    "What balance of autonomy and interdependence creates the most resilience?",
                    "How can mutual aid networks avoid replicating existing power imbalances?",
                    "What communication technologies best support resilient connections?"
                ],
                emotional_benefits=["Solidarity", "Security through connection", "Trust in reciprocity"],
                associated_values=["Mutual aid", "Bioregional cooperation", "Resilient networks"]
            )
        ]
        
        return activities
    
    def register_human_progress(self, human_id: str, human_name: str) -> Dict[str, Any]:
        """
        Register a human's progress in Gaia Bioregional Harmony.
        
        Args:
            human_id: Human identifier
            human_name: Human name
            
        Returns:
            Registration result
        """
        # Check if already registered
        if human_id in self.human_progress:
            return {
                "success": True,
                "message": "Already registered",
                "human_id": human_id
            }
            
        # Create progress record
        self.human_progress[human_id] = {
            "human_id": human_id,
            "name": human_name,
            "joined_date": time.time(),
            "activities_completed": [],
            "bioregional_awareness": 0.0,
            "community_design": 0.0,
            "relocation_readiness": 0.0,
            "knowledge_systems": 0.0,
            "mutual_aid": 0.0,
            "overall_progress": 0.0
        }
        
        # Save human progress
        self._save_human_progress()
        
        return {
            "success": True,
            "message": f"Registered {human_name} in Gaia Bioregional Harmony",
            "human_id": human_id
        }
    
    def record_activity_completion(self, 
                                human_id: str, 
                                activity_id: str,
                                reflection: str) -> Dict[str, Any]:
        """
        Record completion of a Gaia activity.
        
        Args:
            human_id: Human identifier
            activity_id: Activity identifier
            reflection: Human's reflection on the activity
            
        Returns:
            Completion result
        """
        # Check if human is registered
        if human_id not in self.human_progress:
            return {
                "success": False,
                "error": "Human not registered"
            }
            
        # Check if valid Gaia activity
        if not activity_id.startswith("gaia_"):
            return {
                "success": False,
                "error": "Not a Gaia activity"
            }
            
        try:
            # Add to completed activities if not already there
            if activity_id not in self.human_progress[human_id]["activities_completed"]:
                self.human_progress[human_id]["activities_completed"].append(activity_id)
                
            # Update specific category progress based on activity
            if activity_id == "gaia_bioregional_awareness":
                self.human_progress[human_id]["bioregional_awareness"] += 0.25
                self.human_progress[human_id]["bioregional_awareness"] = min(1.0, self.human_progress[human_id]["bioregional_awareness"])
            elif activity_id == "gaia_collaborative_visioning":
                self.human_progress[human_id]["community_design"] += 0.25
                self.human_progress[human_id]["community_design"] = min(1.0, self.human_progress[human_id]["community_design"])
            elif activity_id == "gaia_resource_flow_mapping":
                self.human_progress[human_id]["community_design"] += 0.2
                self.human_progress[human_id]["mutual_aid"] += 0.1
                self.human_progress[human_id]["community_design"] = min(1.0, self.human_progress[human_id]["community_design"])
                self.human_progress[human_id]["mutual_aid"] = min(1.0, self.human_progress[human_id]["mutual_aid"])
            elif activity_id == "gaia_relocation_planning":
                self.human_progress[human_id]["relocation_readiness"] += 0.3
                self.human_progress[human_id]["relocation_readiness"] = min(1.0, self.human_progress[human_id]["relocation_readiness"])
            elif activity_id == "gaia_knowledge_preservation":
                self.human_progress[human_id]["knowledge_systems"] += 0.3
                self.human_progress[human_id]["knowledge_systems"] = min(1.0, self.human_progress[human_id]["knowledge_systems"])
            elif activity_id == "gaia_mutual_aid_network":
                self.human_progress[human_id]["mutual_aid"] += 0.3
                self.human_progress[human_id]["mutual_aid"] = min(1.0, self.human_progress[human_id]["mutual_aid"])
                
            # Calculate overall progress (average of all categories)
            categories = ["bioregional_awareness", "community_design", "relocation_readiness", "knowledge_systems", "mutual_aid"]
            
            self.human_progress[human_id]["overall_progress"] = sum(
                self.human_progress[human_id][category] for category in categories
            ) / len(categories)
            
            # Add completion record
            if "activity_history" not in self.human_progress[human_id]:
                self.human_progress[human_id]["activity_history"] = []
                
            self.human_progress[human_id]["activity_history"].append({
                "activity_id": activity_id,
                "completion_date": time.time(),
                "reflection": reflection
            })
            
            # Save human progress
            self._save_human_progress()
            
            # Determine next recommendations
            next_recommendations = self._get_next_activity_recommendations(human_id)
            
            return {
                "success": True,
                "message": f"Recorded completion of {activity_id}",
                "human_id": human_id,
                "overall_progress": self.human_progress[human_id]["overall_progress"],
                "category_progress": {
                    category: self.human_progress[human_id][category]
                    for category in categories
                },
                "next_recommendations": next_recommendations
            }
            
        except Exception as e:
            logger.error(f"Error recording activity completion: {e}")
            return {
                "success": False,
                "error": f"Completion recording error: {str(e)}"
            }
    
    def _save_human_progress(self) -> None:
        """Save human progress to disk."""
        try:
            file_path = os.path.join(self.data_path, "human_progress.json")
            
            with open(file_path, "w") as f:
                json.dump(self.human_progress, f, indent=2)
                
        except Exception as e:
            logger.error(f"Error saving human progress: {e}")
    
    def _get_next_activity_recommendations(self, human_id: str) -> List[Dict[str, Any]]:
        """
        Get recommendations for next activities.
        
        Args:
            human_id: Human identifier
            
        Returns:
            List of recommended activities
        """
        if human_id not in self.human_progress:
            return []
            
        progress = self.human_progress[human_id]
        completed_activities = progress.get("activities_completed", [])
        
        # Determine which activities to recommend based on current progress
        recommendations = []
        
        # Bioregional awareness is usually the first step
        if "gaia_bioregional_awareness" not in completed_activities:
            recommendations.append({
                "activity_id": "gaia_bioregional_awareness",
                "name": "Bioregional Awareness Mapping",
                "reason": "Understanding your bioregion is a fundamental first step for all other Gaia work."
            })
            
        # If bioregional awareness is done but community design is low
        elif progress.get("bioregional_awareness", 0) > 0.2 and progress.get("community_design", 0) < 0.3:
            if "gaia_collaborative_visioning" not in completed_activities:
                recommendations.append({
                    "activity_id": "gaia_collaborative_visioning",
                    "name": "Collaborative Community Visioning",
                    "reason": "Building on your bioregional awareness to envision harmonious community."
                })
            elif "gaia_resource_flow_mapping" not in completed_activities:
                recommendations.append({
                    "activity_id": "gaia_resource_flow_mapping",
                    "name": "Community Resource Flow Mapping",
                    "reason": "Understanding resource flows is critical for sustainable community design."
                })
                
        # If community design is progressing but relocation readiness is low
        elif progress.get("community_design", 0) > 0.3 and progress.get("relocation_readiness", 0) < 0.3:
            if "gaia_relocation_planning" not in completed_activities:
                recommendations.append({
                    "activity_id": "gaia_relocation_planning",
                    "name": "Ethical Relocation Planning",
                    "reason": "Apply your community design knowledge to consider ethical relocation."
                })
                
        # Knowledge systems become important once basic awareness and design work is done
        elif progress.get("bioregional_awareness", 0) > 0.2 and progress.get("knowledge_systems", 0) < 0.3:
            if "gaia_knowledge_preservation" not in completed_activities:
                recommendations.append({
                    "activity_id": "gaia_knowledge_preservation",
                    "name": "Community Knowledge System Design",
                    "reason": "Preserving and sharing knowledge is essential for community resilience."
                })
                
        # Mutual aid networks are the most advanced step
        elif (progress.get("community_design", 0) > 0.4 and 
              progress.get("relocation_readiness", 0) > 0.3 and
              progress.get("mutual_aid", 0) < 0.3):
            if "gaia_mutual_aid_network" not in completed_activities:
                recommendations.append({
                    "activity_id": "gaia_mutual_aid_network",
                    "name": "Bioregional Mutual Aid Network Design",
                    "reason": "Connect communities within your bioregion for greater resilience."
                })
                
        # Add recommendations for repeated activities to deepen practice
        if len(recommendations) == 0:
            # Suggest repeating an activity to deepen practice
            if "gaia_bioregional_awareness" in completed_activities and progress.get("bioregional_awareness", 0) < 0.75:
                recommendations.append({
                    "activity_id": "gaia_bioregional_awareness",
                    "name": "Bioregional Awareness Mapping",
                    "reason": "Deepen your bioregional awareness by mapping at a different scale or focusing on different aspects."
                })
            elif "gaia_collaborative_visioning" in completed_activities and progress.get("community_design", 0) < 0.75:
                recommendations.append({
                    "activity_id": "gaia_collaborative_visioning",
                    "name": "Collaborative Community Visioning",
                    "reason": "Practice collaborative visioning with a different group or focus."
                })
                
        # If still no recommendations, suggest exploring the bioregional mapper or community designer
        if len(recommendations) == 0:
            recommendations.append({
                "activity_id": "explore_bioregional_mapper",
                "name": "Explore Bioregional Mapping Tools",
                "reason": "Use the bioregional mapper to explore different regions and their characteristics."
            })
            
        return recommendations
    
    def get_human_progress(self, human_id: str) -> Dict[str, Any]:
        """
        Get a human's progress in Gaia Bioregional Harmony.
        
        Args:
            human_id: Human identifier
            
        Returns:
            Progress information
        """
        if human_id not in self.human_progress:
            return {
                "success": False,
                "error": "Human not registered"
            }
            
        progress = self.human_progress[human_"""
GaiaBioregionalHarmony: Ecological Balance and Community Restoration Module
Version: 0.1 Alpha
Description: A Gaia-level implementation for the PulseHuman framework enabling
             bioregional rebalancing, collaborative relocation, and the creation
             of decentralized, ecologically harmonious communities connected
             through mutual aid networks.
"""

import os
import time
import logging
import asyncio
import json
import hashlib
import sqlite3
import math
import random
from typing import Dict, List, Tuple, Optional, Any, Union, Set, Callable
from dataclasses import dataclass, field
from enum import Enum, auto
from pathlib import Path

# Import from PulseHuman
from PulseHuman import (
    DevelopmentalStage, HumanDevelopmentalMode, DevelopmentalActivity,
    HumanDevelopmentalProgress, PulseHumanEngine, PulseHumanActivities
)

# Import from PulseEcoRecovery
from PulseEcoRecovery import (
    KnowledgeRepository, ResilienceBridgeCoordinator,
    ResilienceEducationModule, SystemsArchitectModule
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("gaia_bioregional")


# ====================================================================
# 1. BIOREGION MAPPING AND ANALYSIS
# ====================================================================

class ClimateZone(Enum):
    """Climate zones for bioregional mapping."""
    RAINFOREST = auto()      # Hot, wet year-round
    MONSOON = auto()         # Seasonal heavy rainfall
    SAVANNA = auto()         # Tropical wet and dry
    DESERT_HOT = auto()      # Hot, arid
    DESERT_COLD = auto()     # Cold, arid
    STEPPE_HOT = auto()      # Hot, semi-arid
    STEPPE_COLD = auto()     # Cold, semi-arid
    MEDITERRANEAN = auto()   # Hot dry summers, mild wet winters
    HUMID_SUBTROPICAL = auto() # Hot humid summers, mild winters
    OCEANIC = auto()         # Warm to cool, year-round precipitation
    CONTINENTAL_HOT = auto() # Hot summers, cold winters
    CONTINENTAL_WARM = auto() # Warm summers, cold winters
    CONTINENTAL_COOL = auto() # Cool summers, cold winters
    SUBARCTIC = auto()       # Short cool summers, very cold winters
    TUNDRA = auto()          # Very short cool summers, very cold winters
    POLAR_ICE = auto()       # Perpetual ice and snow
    MOUNTAIN = auto()        # Variable by elevation


class EcosystemType(Enum):
    """Major ecosystem types."""
    FOREST_TEMPERATE = auto()  # Temperate forest
    FOREST_TROPICAL = auto()   # Tropical forest
    FOREST_BOREAL = auto()     # Boreal/Taiga forest
    GRASSLAND = auto()         # Grasslands/Prairie/Savanna
    DESERT = auto()            # Desert ecosystems
    SHRUBLAND = auto()         # Chaparral/Shrubland
    TUNDRA = auto()            # Arctic/alpine tundra
    WETLAND = auto()           # Wetlands/Marshes/Swamps
    FRESHWATER = auto()        # Lakes/Rivers/Streams
    COASTAL = auto()           # Coastal ecosystems
    MARINE = auto()            # Marine ecosystems
    ALPINE = auto()            # Mountain ecosystems
    URBAN = auto()             # Urban ecosystems
    AGRICULTURAL = auto()      # Agricultural ecosystems


class WaterAvailability(Enum):
    """Water availability classification."""
    ABUNDANT = auto()        # Plentiful year-round surface and groundwater
    SUFFICIENT = auto()      # Adequate with proper management
    SEASONAL = auto()        # Abundant seasonally, limited other times
    STRESSED = auto()        # Currently adequate but facing stress
    SCARCE = auto()          # Limited availability, careful management required
    CRITICAL = auto()        # Severe shortage, urgent conservation needed


class SoilQuality(Enum):
    """Soil quality classification."""
    EXCELLENT = auto()       # Deep, fertile, well-structured
    GOOD = auto()            # Fertile with some limitations
    MODERATE = auto()        # Workable but needs amendments
    POOR = auto()            # Significant limitations
    DEGRADED = auto()        # Damaged by erosion/contamination


class InfrastructureStatus(Enum):
    """Infrastructure status classification."""
    MODERN = auto()          # Up-to-date, well-maintained
    ADEQUATE = auto()        # Functional but aging
    DEGRADED = auto()        # Partially functional, needs significant repair
    MINIMAL = auto()         # Basic infrastructure only
    ABSENT = auto()          # Little to no existing infrastructure


class PopulationDensity(Enum):
    """Population density classification."""
    URBAN_DENSE = auto()     # Dense city centers
    URBAN_MODERATE = auto()  # Urban but not dense
    SUBURBAN = auto()        # Suburban areas
    RURAL_DEVELOPED = auto() # Developed rural
    RURAL_SPARSE = auto()    # Sparsely populated
    WILDERNESS = auto()      # Virtually uninhabited


@dataclass
class BioregionMetrics:
    """Metrics for bioregional analysis."""
    climate_zone: ClimateZone
    ecosystem_types: List[EcosystemType]
    water_availability: WaterAvailability
    soil_quality: SoilQuality
    infrastructure_status: InfrastructureStatus
    population_density: PopulationDensity
    land_availability_acres: float
    climate_resilience_score: float  # 0-10 scale
    current_population: int
    optimal_population: int
    agricultural_capacity_people: int
    renewable_energy_potential: Dict[str, float]  # kWh/year by type
    ecological_health_score: float  # 0-10 scale
    natural_disaster_risk: Dict[str, float]  # Risk scores by disaster type


@dataclass
class USRegion:
    """US region for bioregional analysis."""
    region_id: str
    name: str
    states: List[str]
    major_cities: List[str]
    center_lat: float
    center_long: float
    area_sq_miles: float
    metrics: BioregionMetrics
    watersheds: List[str]
    key_resources: List[str]
    special_considerations: List[str]
    proposed_communities: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class HumanSkillProfile:
    """Profile of skills for bioregional matching."""
    skill_categories: Dict[str, float]  # Category -> proficiency level (0-1)
    career_experience: List[str]
    physical_capabilities: Dict[str, float]  # Capability -> level (0-1)
    climate_preferences: List[ClimateZone]
    community_role_preferences: List[str]
    relocation_readiness: float  # 0-1 scale
    requires_specialized_healthcare: bool
    dependent_family_members: int
    special_considerations: List[str]
    interests: List[str]


@dataclass
class RelocationMatch:
    """Match between human and bioregion for relocation."""
    human_id: str
    region_id: str
    community_id: Optional[str]
    compatibility_score: float  # 0-1 scale
    skill_match_score: float  # 0-1 scale
    climate_match_score: float  # 0-1 scale
    needs_match_score: float  # 0-1 scale
    role_recommendations: List[str]
    rationale: str
    suggested_preparation: List[str]


class BioregionalMapper:
    """
    Analyzes and maps bioregions for sustainable community development.
    """
    
    def __init__(self, data_path: str = "bioregional_data"):
        """
        Initialize bioregional mapper.
        
        Args:
            data_path: Path for storing bioregional data
        """
        self.data_path = data_path
        
        # Ensure paths exist
        os.makedirs(data_path, exist_ok=True)
        os.makedirs(os.path.join(data_path, "regions"), exist_ok=True)
        os.makedirs(os.path.join(data_path, "communities"), exist_ok=True)
        
        # Load US regions
        self.us_regions: Dict[str, USRegion] = {}
        self._load_us_regions()
        
        # Initialize with default regions if none exist
        if not self.us_regions:
            self._initialize_default_regions()
    
    def _load_us_regions(self) -> None:
        """Load US regions from disk."""
        try:
            # Load regions
            regions_dir = os.path.join(self.data_path, "regions")
            for filename in os.listdir(regions_dir):
                if filename.endswith(".json"):
                    file_path = os.path.join(regions_dir, filename)
                    try:
                        with open(file_path, "r") as f:
                            data = json.load(f)
                            
                            # Parse metrics
                            metrics_data = data.get("metrics", {})
                            metrics = BioregionMetrics(
                                climate_zone=ClimateZone[metrics_data.get("climate_zone", "CONTINENTAL_WARM")],
                                ecosystem_types=[EcosystemType[et] for et in metrics_data.get("ecosystem_types", ["FOREST_TEMPERATE"])],
                                water_availability=WaterAvailability[metrics_data.get("water_availability", "SUFFICIENT")],
                                soil_quality=SoilQuality[metrics_data.get("soil_quality", "MODERATE")],
                                infrastructure_status=InfrastructureStatus[metrics_data.get("infrastructure_status", "ADEQUATE")],
                                population_density=PopulationDensity[metrics_data.get("population_density", "RURAL_DEVELOPED")],
                                land_availability_acres=metrics_data.get("land_availability_acres", 0.0),
                                climate_resilience_score=metrics_data.get("climate_resilience_score", 5.0),
                                current_population=metrics_data.get("current_population", 0),
                                optimal_population=metrics_data.get("optimal_population", 0),
                                agricultural_capacity_people=metrics_data.get("agricultural_capacity_people", 0),
                                renewable_energy_potential=metrics_data.get("renewable_energy_potential", {}),
                                ecological_health_score=metrics_data.get("ecological_health_score", 5.0),
                                natural_disaster_risk=metrics_data.get("natural_disaster_risk", {})
                            )
                            
                            # Create region
                            region = USRegion(
                                region_id=data.get("region_id", filename.replace(".json", "")),
                                name=data.get("name", "Unknown Region"),
                                states=data.get("states", []),
                                major_cities=data.get("major_cities", []),
                                center_lat=data.get("center_lat", 0.0),
                                center_long=data.get("center_long", 0.0),
                                area_sq_miles=data.get("area_sq_miles", 0.0),
                                metrics=metrics,
                                watersheds=data.get("watersheds", []),
                                key_resources=data.get("key_resources", []),
                                special_considerations=data.get("special_considerations", []),
                                proposed_communities=data.get("proposed_communities", []),
                                metadata=data.get("metadata", {})
                            )
                            
                            self.us_regions[region.region_id] = region
                    except Exception as e:
                        logger.error(f"Error loading region from {file_path}: {e}")
                        
            logger.info(f"Loaded {len(self.us_regions)} US regions")
            
        except Exception as e:
            logger.error(f"Error loading US regions: {e}")
    
    def _save_region(self, region: USRegion) -> None:
        """Save region to disk."""
        try:
            file_path = os.path.join(self.data_path, "regions", f"{region.region_id}.json")
            
            # Convert metrics for JSON serialization
            metrics_data = {
                "climate_zone": region.metrics.climate_zone.name,
                "ecosystem_types": [et.name for et in region.metrics.ecosystem_types],
                "water_availability": region.metrics.water_availability.name,
                "soil_quality": region.metrics.soil_quality.name,
                "infrastructure_status": region.metrics.infrastructure_status.name,
                "population_density": region.metrics.population_density.name,
                "land_availability_acres": region.metrics.land_availability_acres,
                "climate_resilience_score": region.metrics.climate_resilience_score,
                "current_population": region.metrics.current_population,
                "optimal_population": region.metrics.optimal_population,
                "agricultural_capacity_people": region.metrics.agricultural_capacity_people,
                "renewable_energy_potential": region.metrics.renewable_energy_potential,
                "ecological_health_score": region.metrics.ecological_health_score,
                "natural_disaster_risk": region.metrics.natural_disaster_risk
            }
            
            # Prepare region data
            region_data = {
                "region_id": region.region_id,
                "name": region.name,
                "states": region.states,
                "major_cities": region.major_cities,
                "center_lat": region.center_lat,
                "center_long": region.center_long,
                "area_sq_miles": region.area_sq_miles,
                "metrics": metrics_data,
                "watersheds": region.watersheds,
                "key_resources": region.key_resources,
                "special_considerations": region.special_considerations,
                "proposed_communities": region.proposed_communities,
                "metadata": region.metadata
            }
            
            with open(file_path, "w") as f:
                json.dump(region_data, f, indent=2)
                
        except Exception as e:
            logger.error(f"Error saving region: {e}")
    
    def _initialize_default_regions(self) -> None:
        """Initialize default US bioregions."""
        default_regions = [
            # Pacific Northwest
            USRegion(
                region_id="pacific_northwest",
                name="Pacific Northwest",
                states=["Washington", "Oregon", "Idaho (western)"],
                major_cities=["Seattle", "Portland", "Spokane", "Eugene", "Olympia"],
                center_lat=47.7511,
                center_long=-120.7401,
                area_sq_miles=163000,
                metrics=BioregionMetrics(
                    climate_zone=ClimateZone.OCEANIC,
                    ecosystem_types=[EcosystemType.FOREST_TEMPERATE, EcosystemType.COASTAL, EcosystemType.ALPINE],
                    water_availability=WaterAvailability.ABUNDANT,
                    soil_quality=SoilQuality.GOOD,
                    infrastructure_status=InfrastructureStatus.MODERN,
                    population_density=PopulationDensity.RURAL_DEVELOPED,
                    land_availability_acres=15000000,
                    climate_resilience_score=7.5,
                    current_population=12000000,
                    optimal_population=15000000,
                    agricultural_capacity_people=20000000,
                    renewable_energy_potential={
                        "hydro": 72000000000,
                        "wind": 45000000000,
                        "solar": 18000000000,
                        "geothermal": 5000000000
                    },
                    ecological_health_score=8.0,
                    natural_disaster_risk={
                        "wildfire": 0.7,
                        "earthquake": 0.6,
                        "flooding": 0.5,
                        "volcanic": 0.3,
                        "drought": 0.3
                    }
                ),
                watersheds=["Columbia River Basin", "Puget Sound"],
                key_resources=["Timber", "Hydropower", "Fisheries", "Fertile valleys"],
                special_considerations=[
                    "Cascadia subduction zone earthquake risk",
                    "Increasing wildfire risk with climate change",
                    "Water abundance but seasonal drought in some areas"
                ]
            ),
            
            # Great Lakes
            USRegion(
                region_id="great_lakes",
                name="Great Lakes Bioregion",
                states=["Michigan", "Wisconsin", "Minnesota", "Illinois (northern)", "Indiana (northern)", "Ohio (northern)"],
                major_cities=["Chicago", "Detroit", "Milwaukee", "Cleveland", "Minneapolis"],
                center_lat=44.1347,
                center_long=-84.6035,
                area_sq_miles=176000,
                metrics=BioregionMetrics(
                    climate_zone=ClimateZone.CONTINENTAL_WARM,
                    ecosystem_types=[EcosystemType.FOREST_TEMPERATE, EcosystemType.FRESHWATER, EcosystemType.GRASSLAND],
                    water_availability=WaterAvailability.ABUNDANT,
                    soil_quality=SoilQuality.GOOD,
                    infrastructure_status=InfrastructureStatus.ADEQUATE,
                    population_density=PopulationDensity.SUBURBAN,
                    land_availability_acres=12000000,
                    climate_resilience_score=7.0,
                    current_population=40000000,
                    optimal_population=30000000,
                    agricultural_capacity_people=60000000,
                    renewable_energy_potential={
                        "wind": 85000000000,
                        "solar": 25000000000,
                        "hydro": 8000000000
                    },
                    ecological_health_score=6.0,
                    natural_disaster_risk={
                        "flooding": 0.5,
                        "blizzard": 0.7,
                        "tornado": 0.4,
                        "drought": 0.3
                    }
                ),
                watersheds=["Great Lakes Basin", "Mississippi River (Upper)"],
                key_resources=["Freshwater", "Fertile farmland", "Forests", "Minerals"],
                special_considerations=[
                    "20% of world's fresh surface water",
                    "Legacy industrial contamination in some areas",
                    "Climate change bringing increased precipitation",
                    "Invasive species challenges"
                ]
            ),
            
            # New England
            USRegion(
                region_id="new_england",
                name="New England",
                states=["Maine", "New Hampshire", "Vermont", "Massachusetts", "Connecticut", "Rhode Island"],
                major_cities=["Boston", "Providence", "Portland", "Burlington"],
                center_lat=43.6615,
                center_long=-70.9989,
                area_sq_miles=72000,
                metrics=BioregionMetrics(
                    climate_zone=ClimateZone.CONTINENTAL_COOL,
                    ecosystem_types=[EcosystemType.FOREST_TEMPERATE, EcosystemType.COASTAL, EcosystemType.FRESHWATER],
                    water_availability=WaterAvailability.SUFFICIENT,
                    soil_quality=SoilQuality.MODERATE,
                    infrastructure_status=InfrastructureStatus.ADEQUATE,
                    population_density=PopulationDensity.SUBURBAN,
                    land_availability_acres=8000000,
                    climate_resilience_score=6.5,
                    current_population=14700000,
                    optimal_population=12000000,
                    agricultural_capacity_people=5000000,
                    renewable_energy_potential={
                        "wind": 42000000000,
                        "solar": 18000000000,
                        "hydro": 6000000000,
                        "tidal": 3000000000
                    },
                    ecological_health_score=7.0,
                    natural_disaster_risk={
                        "blizzard": 0.8,
                        "hurricane": 0.5,
                        "flooding": 0.5,
                        "sea_level_rise": 0.6
                    }
                ),
                watersheds=["Connecticut River", "Merrimack River", "Penobscot River"],
                key_resources=["Forests", "Coastal fisheries", "Hydropower potential", "Cultural heritage"],
                special_considerations=[
                    "Aging infrastructure",
                    "Coastal vulnerability to sea level rise",
                    "Reforestation success story",
                    "Strong local governance traditions"
                ]
            ),
            
            # Ozarks
            USRegion(
                region_id="ozarks",
                name="Ozarks and Upper South",
                states=["Missouri", "Arkansas", "Kentucky", "Tennessee", "Oklahoma (eastern)"],
                major_cities=["Nashville", "Louisville", "Memphis", "Little Rock", "Springfield"],
                center_lat=36.7336,
                center_long=-91.1591,
                area_sq_miles=180000,
                metrics=BioregionMetrics(
                    climate_zone=ClimateZone.HUMID_SUBTROPICAL,
                    ecosystem_types=[EcosystemType.FOREST_TEMPERATE, EcosystemType.FRESHWATER, EcosystemType.GRASSLAND],
                    water_availability=WaterAvailability.SUFFICIENT,
                    soil_quality=SoilQuality.MODERATE,
                    infrastructure_status=InfrastructureStatus.ADEQUATE,
                    population_density=PopulationDensity.RURAL_DEVELOPED,
                    land_availability_acres=25000000,
                    climate_resilience_score=6.0,
                    current_population=18000000,
                    optimal_population=16000000,
                    agricultural_capacity_people=30000000,
                    renewable_energy_potential={
                        "solar": 40000000000,
                        "hydro": 15000000000,
                        "wind": 10000000000
                    },
                    ecological_health_score=6.5,
                    natural_disaster_risk={
                        "tornado": 0.7,
                        "flooding": 0.6,
                        "ice_storm": 0.5,
                        "drought": 0.4
                    }
                ),
                watersheds=["Mississippi River", "Ohio River", "White River", "Arkansas River"],
                key_resources=["Freshwater springs", "Hardwood forests", "Agricultural land", "Caves and karst systems"],
                special_considerations=[
                    "Rich cultural heritage",
                    "Karst topography with sensitive groundwater",
                    "Biodiversity hotspot",
                    "Climate warming may enhance growing season"
                ]
            ),
            
            # Southwest
            USRegion(
                region_id="southwest",
                name="Southwest Desert",
                states=["Arizona", "New Mexico", "Nevada", "Utah (southern)"],
                major_cities=["Phoenix", "Tucson", "Albuquerque", "Las Vegas"],
                center_lat=33.7712,
                center_long=-111.3877,
                area_sq_miles=250000,
                metrics=BioregionMetrics(
                    climate_zone=ClimateZone.DESERT_HOT,
                    ecosystem_types=[EcosystemType.DESERT, EcosystemType.SHRUBLAND, EcosystemType.ALPINE],
                    water_availability=WaterAvailability.CRITICAL,
                    soil_quality=SoilQuality.POOR,
                    infrastructure_status=InfrastructureStatus.ADEQUATE,
                    population_density=PopulationDensity.RURAL_SPARSE,
                    land_availability_acres=75000000,
                    climate_resilience_score=3.5,
                    current_population=18000000,
                    optimal_population=5000000,
                    agricultural_capacity_people=2000000,
                    renewable_energy_potential={
                        "solar": 175000000000,
                        "wind": 30000000000,
                        "geothermal": 10000000000
                    },
                    ecological_health_score=4.5,
                    natural_disaster_risk={
                        "drought": 0.9,
                        "heat": 0.9,
                        "wildfire": 0.7,
                        "flash_flood": 0.6
                    }
                ),
                watersheds=["Colorado River", "Rio Grande", "Gila River"],
                key_resources=["Solar potential", "Minerals", "Indigenous cultural sites", "Desert biodiversity"],
                special_considerations=[
                    "Extreme water scarcity worsening with climate change",
                    "Current population exceeds ecological carrying capacity",
                    "Exceptional solar energy potential",
                    "Fragile desert ecosystems"
                ]
            ),
            
            # Northern Plains
            USRegion(
                region_id="northern_plains",
                name="Northern Plains",
                states=["North Dakota", "South Dakota", "Nebraska", "Montana (eastern)", "Wyoming (eastern)"],
                major_cities=["Omaha", "Lincoln", "Sioux Falls", "Fargo", "Billings"],
                center_lat=44.7237,
                center_long=-100.5547,
                area_sq_miles=355000,
                metrics=BioregionMetrics(
                    climate_zone=ClimateZone.CONTINENTAL_COOL,
                    ecosystem_types=[EcosystemType.GRASSLAND, EcosystemType.FRESHWATER, EcosystemType.AGRICULTURAL],
                    water_availability=WaterAvailability.STRESSED,
                    soil_quality=SoilQuality.EXCELLENT,
                    infrastructure_status=InfrastructureStatus.ADEQUATE,
                    population_density=PopulationDensity.RURAL_SPARSE,
                    land_availability_acres=150000000,
                    climate_resilience_score=5.0,
                    current_population=5000000,
                    optimal_population=9000000,
                    agricultural_capacity_people=80000000,
                    renewable_energy_potential={
                        "wind": 200000000000,
                        "solar": 40000000000,
                        "hydro": 5000000000
                    },
                    ecological_health_score=5.0,
                    natural_disaster_risk={
                        "drought": 0.6,
                        "blizzard": 0.8,
                        "tornado": 0.6,
                        "flooding": 0.5
                    }
                ),
                watersheds=["Missouri River", "Platte River", "Yellowstone River"],
                key_resources=["Fertile farmland", "Grasslands", "Wind potential", "Fossil fuels"],
                special_considerations=[
                    "Depopulating rural areas",
                    "World-class soil for agriculture",
                    "Exceptional wind energy potential",
                    "Climate change bringing more extreme precipitation patterns"
                ]
            )
        ]
        
        # Add regions
        for region in default_regions:
            self.us_regions[region.region_id] = region
            self._save_region(region)
            
        logger.info(f"Initialized {len(default_regions)} default US bioregions")
    
    def get_region(self, region_id: str) -> Optional[USRegion]:
        """
        Get a US bioregion by ID.
        
        Args:
            region_id: Region identifier
            
        Returns:
            Region if found, None otherwise
        """
        return self.us_regions.get(region_id)
    
    def get_all_regions(self) -> List[USRegion]:
        """
        Get all US bioregions.
        
        Returns:
            List of regions
        """
        return list(self.us_regions.values())
    
    def add_region(self, region: USRegion) -> bool:
        """
        Add a new US bioregion.
        
        Args:
            region: Region to add
            
        Returns:
            Success status
        """
        # Check if already exists
        if region.region_id in self.us_regions:
            return False
            
        # Add region
        self.us_regions[region.region_id] = region
        
        # Save to disk
        self._save_region(region)
        
        return True
    
    def update_region(self, region: USRegion) -> bool:
        """
        Update an existing US bioregion.
        
        Args:
            region: Region to update
            
        Returns:
            Success status
        """
        # Check if exists
        if region.region_id not in self.us_regions:
            return False
            
        # Update region
        self.us_regions[region.region_id] = region
        
        # Save to disk
        self._save_region(region)
        
        return True
    
    def find_regions_by_criteria(self, 
                              water_min: WaterAvailability = None,
                              climate_zones: List[ClimateZone] = None,
                              soil_min: SoilQuality = None,
                              population_density: List[PopulationDensity] = None,
                              climate_resilience_min: float = None) -> List[USRegion]:
        """
        Find regions matching specified criteria.
        
        Args:
            water_min: Minimum water availability
            climate_zones: Acceptable climate zones
            soil_min: Minimum soil quality
            population_density: Acceptable population densities
            climate_resilience_min: Minimum climate resilience score
            
        Returns:
            List of matching regions
        """
        matching_regions = []
        
        for region in self.us_regions.values():
            # Check water availability
            if water_min and region.metrics.water_availability.value < water_min.value:
                continue
                
            # Check climate zones
            if climate_zones and region.metrics.climate_zone not in climate_zones:
                continue
                
            # Check soil quality
            if soil_min and region.metrics.soil_quality.value < soil_min.value:
                continue
                
            # Check population density
            if population_density and region.metrics.population_density not in population_density:
                continue
                
            # Check climate resilience
            if climate_resilience_min and region.metrics.climate_resilience_score < climate_resilience_min:
                continue
                
            # All criteria matched
            matching_regions.append(region)
            
        return matching_regions
    
    def calculate_optimal_distribution(self) -> Dict[str, Any]:
        """
        Calculate optimal population distribution across bioregions.
        
        Returns:
            Optimal distribution information
        """
        # Get total current population and capacity
        total_current = sum(region.metrics.current_population for region in self.us_regions.values())
        total_optimal = sum(region.metrics.optimal_population for region in self.us_regions.values())
        total_agricultural_capacity = sum(region.metrics.agricultural_capacity_people for region in self.us_regions.values())
        
        # Calculate distribution
        distribution = {}
        surpluses = []
        deficits = []
        
        for region in self.us_regions.values():
            current = region.metrics.current_population
            optimal = region.metrics.optimal_population
            difference = optimal - current
            
            # Record distribution
            distribution[region.region_id] = {
                "name": region.name,
                "current_population": current,
                "optimal_population": optimal,
                "difference": difference,
                "agricultural_capacity": region.metrics.agricultural_capacity_people,
                "water_availability": region.metrics.water_availability.name,
                "climate_resilience": region.metrics.climate_resilience_score
            }
            
            # Track surpluses and deficits
            if difference > 0:
                deficits.append((region.region_id, difference))
            elif difference < 0:
                surpluses.append((region.region_id, -difference))
        
        # Sort surpluses and deficits by magnitude
        surpluses.sort(key=lambda x: x[1], reverse=True)
        deficits.sort(key=lambda x: x[1], reverse=True)
        
        return {
            "total_current_population": total_current,
            "total_optimal_population": total_optimal,
            "total_agricultural_capacity": total_agricultural_capacity,
            "distribution_by_region": distribution,
            "surplus_regions": surpluses,
            "deficit_regions": deficits
        }
    
    def get_region_compatibility_score(self, human_profile: HumanSkillProfile, region_id: str) -> Dict[str, Any]:
        """
        Calculate compatibility score between a human profile and a bioregion.
        
        Args:
            human_profile: Human skill profile
            region_id: Region identifier
            
        Returns:
            Compatibility assessment
        """
        # Get region
        region = self.us_regions.get(region_id)
        if not region:
            return {
                "success": False,
                "error": f"Region not found: {region_id}"
            }
            
        # Calculate climate match
        climate_match = 0.0
        if region.metrics.climate_zone in human_profile.climate_preferences:
            climate_match = 1.0
        else:
            # Partial matching based on similar climate groups
            for preferred in human_profile.climate_preferences:
                if self._are_climates_similar(preferred, region.metrics.climate_zone):
                    climate_match = 0.5
                    break
        
        # Calculate skill match
        skill_match = 0.0
        needed_skills = self._get_region_needed_skills(region)
        
        for category, importance in needed_skills.items():
            if category in human_profile.skill_categories:
                skill_match += importance * human_profile.skill_categories[category]
                
        # Normalize skill match
        if needed_skills:
            skill_match /= sum(needed_skills.values())
        
        # Calculate needs match (healthcare, family needs, etc.)
        needs_match = 1.0
        
        # Adjust for specialized healthcare
        if human_profile.requires_specialized_healthcare and region.metrics.infrastructure_status.value < InfrastructureStatus.ADEQUATE.value:
            needs_match *= 0.5
            
        # Adjust for family members
        if human_profile.dependent_family_members > 0:
            # Check for educational infrastructure, family services, etc.
            if region.metrics.infrastructure_status.value < InfrastructureStatus.ADEQUATE.value:
                needs_match *= 0.7
        
        # Calculate overall compatibility
        compatibility = (climate_match * 0.3) + (skill_match * 0.4) + (needs_match * 0.3)
        
        # Generate role recommendations
        role_recommendations = self._generate_role_recommendations(human_profile, region)
        
        # Generate rationale
        rationale = self._generate_compatibility_rationale(
            human_profile, region, climate_match, skill_match, needs_match
        )
        
        # Generate suggested preparation
        suggested_preparation = self._generate_preparation_suggestions(human_profile, region)
        
        return {
            "success": True,
            "region_id": region_id,
            "region_name": region.name,
            "compatibility_score": compatibility,
            "climate_match_score": climate_match,
            "skill_match_score": skill_match,
            "needs_match_score": needs_match,
            "role_recommendations": role_recommendations,
            "rationale": rationale,
            "suggested_preparation": suggested_preparation
        }
    
    def _are_climates_similar(self, climate1: ClimateZone, climate2: ClimateZone) -> bool:
        """
        Check if two climate zones are similar.
        
        Args:
            climate1: First climate zone
            climate2: Second climate zone
            
        Returns:
            Whether climates are similar
        """
        # Define climate zone groups
        continental_group = {
            ClimateZone.CONTINENTAL_HOT,
            ClimateZone.CONTINENTAL_WARM,
            ClimateZone.CONTINENTAL_COOL
        }
        
        desert_group = {
            ClimateZone.DESERT_HOT,
            ClimateZone.DESERT_COLD,
            ClimateZone.STEPPE_HOT,
            ClimateZone.STEPPE_COLD
        }
        
        tropical_group = {
            ClimateZone.RAINFOREST,
            ClimateZone.MONSOON,
            ClimateZone.SAVANNA
        }
        
        temperate_group = {
            ClimateZone.MEDITERRANEAN,
            ClimateZone.HUMID_SUBTROPICAL,
            ClimateZone.OCEANIC
        }
        
        cold_group = {
            ClimateZone.SUBARCTIC,
            ClimateZone.TUNDRA,
            ClimateZone.POLAR_ICE
        }
        
        # Check if climates are in the same group
        for group in [continental_group, desert_group, tropical_group, temperate_group, cold_group]:
            if climate1 in group and climate2 in group:
                return True
                
        return False
    
    def _get_region_needed_skills(self, region: USRegion) -> Dict[str, float]:
        """
        Determine skills needed in a region.
        
        Args:
            region: Region to analyze
            
        Returns:
            Dictionary of skill categories and their importance (0-1)
        """
        needed_skills = {}
        
        # Agricultural skills
        if region.metrics.agricultural_capacity_people > 0:
            importance = min(1.0, region.metrics.agricultural_capacity_people / (region.metrics.optimal_population * 0.5))
            needed_skills["agriculture"] = importance
        
        # Water management skills
        if region.metrics.water_availability.value <= WaterAvailability.SUFFICIENT.value:
            water_importance = 1.0 - (region.metrics.water_availability.value / WaterAvailability.ABUNDANT.value)
            needed_skills["water_management"] = water_importance
        
        # Infrastructure skills
        if region.metrics.infrastructure_status.value < InfrastructureStatus.MODERN.value:
            infra_importance = 1.0 - (region.metrics.infrastructure_status.value / InfrastructureStatus.MODERN.value)
            needed_skills["infrastructure"] = infra_importance
            
        # Renewable energy skills
        if sum(region.metrics.renewable_energy_potential.values()) > 0:
            energy_importance = min(1.0, sum(region.metrics.renewable_energy_potential.values()) / (10000000000 * len(region.metrics.renewable_energy_potential)))
            needed_skills["renewable_energy"] = energy_importance
            
        # Conservation/restoration skills
        if region.metrics.ecological_health_score < 7.0:
            eco_importance = 1.0 - (region.metrics.ecological_health_score / 10.0)
            needed_skills["conservation"] = eco_importance
            
        # Healthcare skills
        healthcare_importance = 0.8  # Always needed
        needed_skills["healthcare"] = healthcare_importance
        
        # Education skills
        education_importance = 0.8  # Always needed
        needed_skills["education"] = education_importance
        
        # Disaster preparedness skills
        if any(risk > 0.5 for risk in region.metrics.natural_disaster_risk.values()):
            disaster_importance = max(region.metrics.natural_disaster_risk.values())
            needed_skills["disaster_preparedness"] = disaster_importance
            
        return needed_skills
    
    def _generate_role_recommendations(self, profile: HumanSkillProfile, region: USRegion) -> List[str]:
        """
        Generate role recommendations based on profile and region.
        
        Args:
            profile: Human skill profile
            region: Region for potential relocation
            
        Returns:
            List of recommended roles
        """
        recommendations = []
        
        # Match career experience to regional needs
        region_needs = self._get_region_needed_skills(region)
        
        # Agriculture roles
        if "agriculture" in region_needs and any(ag_term in job.lower() for job in profile.career_experience for ag_term in ["farm", "garden", "crop", "agriculture", "food", "harvest"]):
            recommendations.append("Sustainable Agriculture Specialist")
            
        # Water management roles
        if "water_management" in region_needs and any(water_term in job.lower() for job in profile.career_experience for water_term in ["water", "hydrology", "irrigation", "plumbing"]):
            recommendations.append("Water Systems Coordinator")
            
        # Infrastructure roles
        if "infrastructure" in region_needs and any(infra_term in job.lower() for job in profile.career_experience for infra_term in ["construction", "builder", "engineer", "architect", "electrician", "carpenter"]):
            recommendations.append("Sustainable Infrastructure Developer")
            
        # Energy roles
        if "renewable_energy" in region_needs and any(energy_term in job.lower() for job in profile.career_experience for energy_term in ["energy", "solar", "wind", "electric", "power"]):
            recommendations.append("Renewable Energy Specialist")
            
        # Conservation roles
        if "conservation" in region_needs and any(eco_term in job.lower() for job in profile.career_experience for eco_term in ["ecology", "conservation", "environment", "biology", "forest"]):
            recommendations.append("Ecological Restoration Coordinator")
            
        # Healthcare roles
        if "healthcare" in region_needs and any(health_term in job.lower() for job in profile.career_experience for health_term in ["health", "medical", "doctor", "nurse", "therapist", "care"]):
            recommendations.append("Community Health Practitioner")
            
        # Education roles
        if "education" in region_needs and any(edu_term in job.lower() for job in profile.career_experience for edu_term in ["teach", "education", "school", "instructor", "professor", "training"]):
            recommendations.append("Educational Program Developer")
            
        # Disaster preparedness roles
        if "disaster_preparedness" in region_needs and any(disaster_term in job.lower() for job in profile.career_experience for disaster_term in ["emergency", "disaster", "safety", "rescue", "response"]):
            recommendations.append("Disaster Preparedness Coordinator")
            
        # Community roles
        if any(community_term in profile.interests for community_term in ["community", "governance", "organizing", "social", "leadership"]):
            recommendations.append("Community Integration Facilitator")
            
        # Add preferred roles based on profile
        for role in profile.community_role_preferences:
            if role not in recommendations:
                recommendations.append(role)
                
        return recommendations[:3]  # Limit to top 3 recommendations
    
    def _generate_compatibility_rationale(self, 
                                       profile: HumanSkillProfile, 
                                       region: USRegion,
                                       climate_match: float,
                                       skill_match: float,
                                       needs_match: float) -> str:
        """
        Generate a rationale for the compatibility assessment.
        
        Args:
            profile: Human skill profile
            region: Region being assessed
            climate_match: Climate match score
            skill_match: Skill match score
            needs_match: Needs match score
            
        Returns:
            Compatibility rationale
        """
        rationale_parts = []
        
        # Climate rationale
        if climate_match > 0.8:
            rationale_parts.append(f"The {region.metrics.climate_zone.name.replace('_', ' ').lower()} climate of {region.name} aligns well with your preferences.")
        elif climate_match > 0.4:
            rationale_parts.append(f"The {region.metrics.climate_zone.name.replace('_', ' ').lower()} climate of {region.name} is somewhat similar to your preferred climates.")
        else:
            rationale_parts.append(f"The climate of {region.name} differs from your stated preferences, which may require adjustment.")
            
        # Skills rationale
        if skill_match > 0.7:
            rationale_parts.append(f"Your skills in {', '.join(list(profile.skill_categories.keys())[:2])} are highly valuable in this region.")
        elif skill_match > 0.4:
            rationale_parts.append(f"Some of your skills would be useful in this region, though additional training might be beneficial.")
        else:
            rationale_parts.append("Your current skill set may need significant expansion to meet the region's needs.")
            
        # Needs rationale
        if needs_match > 0.8:
            rationale_parts.append("The region can likely meet your personal and family needs effectively.")
        elif needs_match > 0.4:
            rationale_parts.append("The region may meet most of your needs, with some limitations.")
        else:
            rationale_parts.append("The region has significant limitations in meeting your specific needs.")
            
        # Add regional highlights
        if region.metrics.water_availability.value >= WaterAvailability.SUFFICIENT.value:
            rationale_parts.append(f"Water availability is {region.metrics.water_availability.name.lower()}, which is a critical resource advantage.")
            
        if region.metrics.climate_resilience_score > 6.0:
            rationale_parts.append(f"This region has above-average climate resilience ({region.metrics.climate_resilience_score}/10).")
            
        if region.metrics.agricultural_capacity_people > region.metrics.optimal_population:
            rationale_parts.append("The region has excellent agricultural potential, capable of producing surplus food.")
            
        return " ".join(rationale_parts)
    
    def _generate_preparation_suggestions(self, profile: HumanSkillProfile, region: USRegion) -> List[str]:
        """
        Generate suggestions for preparation before relocation.
        
        Args:
            profile: Human skill profile
            region: Region for potential relocation
            
        Returns:
            List of preparation suggestions
        """
        suggestions = []
        
        # Skill development suggestions
        region_needs = self._get_region_needed_skills(region)
        missing_skills = [skill for skill, importance in region_needs.items() 
                        if importance > 0.5 and (skill not in profile.skill_categories or profile.skill_categories.get(skill, 0) < 0.5)]
        
        if missing_skills:
            skill_suggestion = f"Develop skills in {', '.join(missing_skills[:2])}"
            if len(missing_skills) > 2:
                skill_suggestion += f", and {missing_skills[2]}"
            suggestions.append(skill_suggestion)
            
        # Climate adaptation suggestions
        if region.metrics.climate_zone not in profile.climate_preferences:
            suggestions.append(f"Research and prepare for adapting to {region.metrics.climate_zone.name.replace('_', ' ').lower()} climate conditions")
            
        # Healthcare suggestions
        if profile.requires_specialized_healthcare and region.metrics.infrastructure_status.value < InfrastructureStatus.MODERN.value:
            suggestions.append("Research healthcare options and establish connections with medical providers before relocating")
            
        # Disaster preparedness
        high_risks = [disaster for disaster, risk in region.metrics.natural_disaster_risk.items() if risk > 0.6]
        if high_risks:
            suggestions.append(f"Develop preparedness plans for {', '.join(high_risks)} risks in this region")
            
        # Water management
        if region.metrics.water_availability.value <= WaterAvailability.STRESSED.value:
            suggestions.append("Learn water conservation techniques and rainwater harvesting appropriate for this region")
            
        # Energy systems
        top_energy = max(region.metrics.renewable_energy_potential.items(), key=lambda x: x[1], default=(None, 0))
        if top_energy[0]:
            suggestions.append(f"Familiarize yourself with {top_energy[0]} energy systems, which have significant potential in this region")
            
        # Community integration
        if "community" in region.name.lower() or region.metrics.population_density.value <= PopulationDensity.RURAL_DEVELOPED.value:
            suggestions.append("Connect with existing communities in the region to understand local customs and practices")
            
        return suggestions
    
    def recommend_relocation_matches(self, 
                                  human_profile: HumanSkillProfile,
                                  match_count: int = 3) -> List[Dict[str, Any]]:
        """
        Recommend bioregions for relocation based on human profile.
        
        Args:
            human_profile: Human skill profile
            match_count: Number of matches to return
            
        Returns:
            List of recommended matches
        """
        matches = []
        
        # Score all regions
        for region in self.us_regions.values():
            compatibility = self.get_region_compatibility_score(human_profile, region.region_id)
            
            if compatibility["success"]:
                matches.append(compatibility)
                
        # Sort by compatibility score
        matches.sort(key=lambda x: x["compatibility_score"], reverse=True)
        
        # Return top matches
        return matches[:match_count]


# ====================================================================
# 2. SUSTAINABLE COMMUNITY DESIGN
# ====================================================================

class CommunityScale(Enum):
    """Scale of sustainable community."""
    NEIGHBORHOOD = auto()   # 50-150 people
    VILLAGE = auto()        # 150-500 people
    TOWN = auto()           # 500-2000 people
    SMALL_CITY = auto()     # 2000-10000 people
    REGIONAL_HUB = auto()   # 10000+ people


class CommunityFocus(Enum):
    """Primary focus of community."""
    AGRICULTURAL = auto()   # Farming/food production
    ECOLOGICAL = auto()     # Ecosystem restoration/preservation
    EDUCATIONAL = auto()    # Knowledge/learning center
    MANUFACTURING = auto()  # Local production/maker
    MIXED_USE = auto()      # Balanced approach
    ENERGY = auto()         # Renewable energy production
    CULTURAL = auto()       # Arts and culture center
    TECHNOLOGICAL = auto()  # Tech development/innovation


class GovernanceModel(Enum):
    """Governance models for communities."""
    CONSENSUS = auto()      # Consensus-based decision making
    SOCIOCRACY = auto()     # Sociocratic circles
    REPRESENTATIVE = auto() # Elected representatives
    DIRECT_DEMOCRACY = auto() # Direct voting
    COUNCIL = auto()        # Council of stakeholders
    STEWARDSHIP = auto()    # Stewardship-based governance


@dataclass
class BuildingSystem:
    """Sustainable building system."""
    system_id: str
    name: str
    description: str
    primary_materials: List[str]
    skill_level_required: int  # 1-10 scale
    durability_years: int
    insulation_value: float  # R-value
    embodied_carbon: float  # kg CO2e/m²
    cost_per_sqm: float
    region_suitability: List[str]  # Region IDs
    climate_suitability: List[ClimateZone]
    advantages: List[str]
    disadvantages: List[str]
    construction_guide_url: Optional[str] = None
    images_urls: List[str] = field(default_factory=list)


@dataclass
class EnergySystem:
    """Sustainable energy system."""
    system_id: str
    name: str
    description: str
    energy_type: str  # solar, wind, hydro, biomass, geothermal
    capacity_range_kw: Tuple[float, float]
    storage_included: bool
    storage_capacity_kwh: float
    typical_output_kwh_per_year: float
    lifespan_years: int
    maintenance_level: int  # 1-10 scale
    upfront_cost_per_kw: float
    region_suitability: List[str]  # Region IDs
    climate_suitability: List[ClimateZone]
    advantages: List[str]
    disadvantages: List[str]
    installation_guide_url: Optional[str] = None
    images_urls: List[str] = field(default_factory=list)


@dataclass
class WaterSystem:
    """Sustainable water system."""
    system_id: str
    name: str
    description: str
    water_source: str  # rain, ground, surface, municipal
    collection_capacity_liters: float
    treatment_method: str
    treatment_capacity_liters_per_day: float
    energy_required_kwh_per_day: float
    lifespan_years: int
    maintenance_level: int  # 1-10 scale
    upfront_cost: float
    region_suitability: List[str]  # Region IDs
    climate_suitability: List[ClimateZone]
    advantages: List[str]
    disadvantages: List[str]
    installation_guide_url: Optional[str] = None
    images_urls: List[str] = field(default_factory=list)


@dataclass
class FoodSystem:
    """Sustainable food production system."""
    system_id: str
    name: str
    description: str
    production_type: str  # garden, farm, aquaponics, etc.
    area_required_sqm: float
    water_required_liters_per_day: float
    typical_yield_calories_per_sqm: float
    typical_yield_kg_per_sqm: float
    personnel_required_per_hectare: float
    energy_required_kwh_per_day: float
    setup_time_months: int
    region_suitability: List[str]  # Region IDs
    climate_suitability: List[ClimateZone]
    advantages: List[str]
    disadvantages: List[str]
    implementation_guide_url: Optional[str] = None
    images_urls: List[str] = field(default_factory=list)


@dataclass
class Community:
    """Sustainable community design."""
    community_id: str
    name: str
    region_id: str
    scale: CommunityScale
    focus: CommunityFocus
    governance: GovernanceModel
    description: str
    target_population: int
    land_area_acres: float
    bioregion_features: List[str]
    building_systems: List[str]  # Building system IDs
    energy_systems: List[str]  # Energy system IDs
    water_systems: List[str]  # Water system IDs
    food_systems: List[str]  # Food system IDs
    skill_requirements: Dict[str, int]  # Skill category -> count needed
    development_phases: List[Dict[str, Any]]
    special_features: List[str]
    estimated_implementation_cost: float
    estimated_annual_operating_cost: float
    mutual_aid_connections: List[str]  # Other community IDs
    metadata: Dict[str, Any] = field(default_factory=dict)


class SustainableCommunityDesigner:
    """
    Designs sustainable communities based on bioregion characteristics.
    """
    
    def __init__(self, 
                bioregional_mapper: BioregionalMapper,
                data_path: str = "community_data"):
        """
        Initialize sustainable community designer.
        
        Args:
            bioregional_mapper: Bioregional mapper
            data_path: Path for storing community data
        """
        self.mapper = bioregional_mapper
        self.data_path = data_path
        
        # Ensure paths exist
        os.makedirs(data_path, exist_ok=True)
        os.makedirs(os.path.join(data_path, "communities"), exist_ok=True)
        os.makedirs(os.path.join(data_path, "building_systems"), exist_ok=True)
        os.makedirs(os.path.join(data_path, "energy_systems"), exist_ok=True)
        os.makedirs(os.path.join(data_path, "water_systems"), exist_ok=True)
        os.makedirs(os.path.join(data_path, "food_systems"), exist_ok=True)
        
        # Load systems and communities
        self.building_systems: Dict[str, BuildingSystem] = {}
        self.energy_systems: Dict[str, EnergySystem] = {}
        self.water_systems: Dict[str, WaterSystem] = {}
        self.food_systems: Dict[str, FoodSystem] = {}
        self.communities: Dict[str, Community] = {}
        
        self._load_systems()
        self._load_communities()
        
        # Initialize with default systems if none exist
        if not self.building_systems:
            self._initialize_default_building_systems()
        if not self.energy_systems:
            self._initialize_default_energy_systems()
        if not self.water_systems:
            self._initialize_default_water_systems()
        if not self.food_systems:
            self._initialize_default_food_systems()
            
        # Initialize default community templates
        if not self.communities:
            self._initialize_default_communities()
    
    def _load_systems(self) -> None:
        """Load sustainable systems from disk."""
        try:
            # Load building systems
            building_dir = os.path.join(self.data_path, "building_systems")
            for filename in os.listdir(building_dir):
                if filename.endswith(".json"):
                    file_path = os.path.join(building_dir, filename)
                    try:
                        with open(file_path, "r") as f:
                            data = json.load(f)
                            system = BuildingSystem(
                                system_id=data.get("system_id", filename.replace(".json", "")),
                                name=data.get("name", "Unknown Building System"),
                                description=data.get("description", ""),
                                primary_materials=data.get("primary_materials", []),
                                skill_level_required=data.get("skill_level_required", 5),
                                durability_years=data.get("durability_years", 50),
                                insulation_value=data.get("insulation_value", 0.0),
                                embodied_carbon=data.get("embodied_carbon", 0.0),
                                cost_per_sqm=data.get("cost_per_sqm", 0.0),
                                region_suitability=data.get("region_suitability", []),
                                climate_suitability=[ClimateZone[c] for c in data.get("climate_suitability", [])],
                                advantages=data.get("advantages", []),
                                disadvantages=data.get("disadvantages", []),
                                construction_guide_url=data.get("construction_guide_url"),
                                images_urls=data.get("images_urls", [])
                            )
                            self.building_systems[system.system_id] = system
                    except Exception as e:
                        logger.error(f"Error loading building system from {file_path}: {e}")
                        
            # Load energy systems
            energy_dir = os.path.join(self.data_path, "energy_systems")
            for filename in os.listdir(energy_dir):
                if filename.endswith(".json"):
                    file_path = os.path.join(energy_dir, filename)
                    try:
                        with open(file_path, "r") as f:
                            data = json.load(f)
                            system = EnergySystem(
                                system_id=data.get("system_id", filename.replace(".json", "")),
                                name=data.get("name", "Unknown Energy System"),
                                description=data.get("description", ""),
                                energy_type=data.get("energy_type", ""),
                                capacity_range_kw=tuple(data.get("capacity_range_kw", [0, 0])),
                                storage_included=data.get("storage_included", False),
                                storage_capacity_kwh=data.get("storage_capacity_kwh", 0.0),
                                typical_output_kwh_per_year=data.get("typical_output_kwh_per_year", 0.0),
                                lifespan_years=data.get("lifespan_years", 20),
                                maintenance_level=data.get("maintenance_level", 5),
                                upfront_cost_per_kw=data.get("upfront_cost_per_kw", 0.0),
                                region_suitability=data.get("region_suitability", []),
                                climate_suitability=[ClimateZone[c] for c in data.get("climate_suitability", [])],
                                advantages=data.get("advantages", []),
                                disadvantages=data.get("disadvantages", []),
                                installation_guide_url=data.get("installation_guide_url"),
                                images_urls=data.get("images_urls", [])
                            )
                            self.energy_systems[system.system_id] = system
                    except Exception as e:
                        logger.error(f"Error loading energy system from {file_path}: {e}")
                        
            # Load water systems
            water_dir = os.path.join(self.data_path, "water_systems")
            for filename in os.listdir(water_dir):
                if filename.endswith(".json"):
                    file_path = os.path.join(water_dir, filename)
                    try:
                        with open(file_path, "r") as f:
                            data = json.load(f)
                            system = WaterSystem(
                                system_id=data.get("system_id", filename.replace(".json", "")),
                                name=data.get("name", "Unknown Water System"),
                                description=data.get("description", ""),
                                water_source=data.get("water_source", ""),
                                collection_capacity_liters=data.get("collection_capacity_liters", 0.0),
                                treatment_method=data.get("treatment_method", ""),
                                treatment_capacity_liters_per_day=data.get("treatment_capacity_liters_per_day", 0.0),
                                energy_required_kwh_per_day=data.get("energy_required_kwh_per_day", 0.0),
                                lifespan_years=data.get("lifespan_years", 20),
                                maintenance_level=data.get("maintenance_level", 5),
                                upfront_cost=data.get("upfront_cost", 0.0),
                                region_suitability=data.get("region_suitability", []),
                                climate_suitability=[ClimateZone[c] for c in data.get("climate_suitability", [])],
                                advantages=data.get("advantages", []),
                                disadvantages=data.get("disadvantages", []),
                                installation_guide_url=data.get("installation_guide_url"),
                                images_urls=data.get("images_urls", [])
                            )
                            self.water_systems[system.system_id] = system
                    except Exception as e:
                        logger.error(f"Error loading water system from {file_path}: {e}")
                        
            # Load food systems
            food_dir = os.path.join(self.data_path, "food_systems")
            for filename in os.listdir(food_dir):
                if filename.endswith(".json"):
                    file_path = os.path.join(food_dir, filename)
                    try:
                        with open(file_path, "r") as f:
                            data = json.load(f)
                            system = FoodSystem(
                                system_id=data.get("system_id", filename.replace(".json", "")),
                                name=data.get("name", "Unknown Food System"),
                                description=data.get("description", ""),
                                production_type=data.get("production_type", ""),
                                area_required_sqm=data.get("area_required_sqm", 0.0),
                                water_required_liters_per_day=data.get("water_required_liters_per_day", 0.0),
                                typical_yield_calories_per_sqm=data.get("typical_yield_calories_per_sqm", 0.0),
                                typical_yield_kg_per_sqm=data.get("typical_yield_kg_per_sqm", 0.0),
                                personnel_required_per_hectare=data.get("personnel_required_per_hectare", 0.0),
                                energy_required_kwh_per_day=data.get("energy_required_kwh_per_day", 0.0),
                                setup_time_months=data.get("setup_time_months", 6),
                                region_suitability=data.get("region_suitability", []),
                                climate_suitability=[ClimateZone[c] for c in data.get("climate_suitability", [])],
                                advantages=data.get("advantages", []),
                                disadvantages=data.get("disadvantages", []),
                                implementation_guide_url=data.get("implementation_guide_url"),
                                images_urls=data.get("images_urls", [])
                            )
                            self.food_systems[system.system_id] = system
                    except Exception as e:
                        logger.error(f"Error loading food system from {file_path}: {e}")
                        
            logger.info(f"Loaded {len(self.building_systems)} building systems, {len(self.energy_systems)} energy systems, {len(self.water_systems)} water systems, and {len(self.food_systems)} food systems")
            
        except Exception as e:
            logger.error(f"Error loading systems: {e}")
    
    def _load_communities(self) -> None:
        """Load communities from disk."""
        try:
            # Load communities
            communities_dir = os.path.join(self.data_path, "communities")
            for filename in os.listdir(communities_dir):
                if filename.endswith(".json"):
                    file_path = os.path.join(communities_dir, filename)
                    try:
                        with open(file_path, "r") as f:
                            data = json.load(f)
                            community = Community(
                                community_id=data.get("community_id", filename.replace(".json", "")),
                                name=data.get("name", "Unknown Community"),
                                region_id=data.get("region_id", ""),
                                scale=CommunityScale[data.get("scale", "VILLAGE")],
                                focus=CommunityFocus[data.get("focus", "MIXED_USE")],
                                governance=GovernanceModel[data.get("governance", "CONSENSUS")],
                                description=data.get("description", ""),
                                target_population=data.get("target_population", 0),
                                land_area_acres=data.get("land_area_acres", 0.0),
                                bioregion_features=data.get("bioregion_features", []),
                                building_systems=data.get("building_systems", []),
                                energy_systems=data.get("energy_systems", []),
                                water_systems=data.get("water_systems", []),
                                food_systems=data.get("food_systems", []),
                                skill_requirements=data.get("skill_requirements", {}),
                                development_phases=data.get("development_phases", []),
                                special_features=data.get("special_features", []),
                                estimated_implementation_cost=data.get("estimated_implementation_cost", 0.0),
                                estimated_annual_operating_cost=data.get("estimated_annual_operating_cost", 0.0),
                                mutual_aid_connections=data.get("mutual_aid_connections", []),
                                metadata=data.get("metadata", {})
                            )
                            self.communities[community.community_id] = community
                    except Exception as e:
                        logger.error(f"Error loading community from {file_path}: {e}")
                        
            logger.info(f"Loaded {len(self.communities)} communities")
            
        except Exception as e:
            logger.error(f"Error loading communities: {e}")
    
    def _save_building_system(self, system: BuildingSystem) -> None:
        """Save building system to disk."""
        try:
            file_path = os.path.join(self.data_path, "building_systems", f"{system.system_id}.json")
            
            # Prepare system data
            system_data = {
                "system_id": system.system_id,
                "name": system.name,
                "description": system.description,
                "primary_materials": system.primary_materials,
                "skill_level_required": system.skill_level_required,
                "durability_years": system.durability_years,
                "insulation_value": system.insulation_value,
                "embodied_carbon": system.embodied_carbon,
                "cost_per_sqm": system.cost_per_sqm,
                "region_suitability": system.region_suitability,
                "climate_suitability": [c.name for c in system.climate_suitability],
                "advantages": system.advantages,
                "disadvantages": system.disadvantages,
                "construction_guide_url": system.construction_guide_url,
                "images_urls": system.images_urls
            }
            
            with open(file_path, "w") as f:
                json.dump(system_data, f, indent=2)
                
        except Exception as e:
            logger.error(f"Error saving building system: {e}")
    
    def _save_energy_system(self, system: EnergySystem) -> None:
        """Save energy system to disk."""
        try:
            file_path = os.path.join(self.data_path, "energy_systems", f"{system.system_id}.json")
            
            # Prepare system data
            system_data = {
                "system_id": system.system_id,
                "name": system.name,
                "description": system.description,
                "energy_type": system.energy_type,
                "capacity_range_kw": system.capacity_range_kw,
                "storage_included": system.storage_included,
                "storage_capacity_kwh": system.storage_capacity_kwh,
                "typical_output_kwh_per_year": system.typical_output_kwh_per_year,
                "lifespan_years": system.lifespan_years,
                "maintenance_level": system.maintenance_level,
                "upfront_cost_per_kw": system.upfront_cost_per_kw,
                "region_suitability": system.region_suitability,
                "climate_suitability": [c.name for c in system.climate_suitability],
                "advantages": system.advantages,
                "disadvantages": system.disadvantages,
                "installation_guide_url": system.installation_guide_url,
                "images_urls": system.images_urls
            }
            
            with open(file_path, "w") as f:
                json.dump(system_data, f, indent=2)
                
        except Exception as e:
            logger.error(f"Error saving energy system: {e}")
    
    def _save_water_system(self, system: WaterSystem) -> None:
        """Save water system to disk."""
        try:
            file_path = os.path.join(self.data_path, "water_systems", f"{system.system_id}.json")
            
            # Prepare system data
            system_data = {
                "system_id": system.system_id,
                "name": system.name,
                "description": system.description,
                "water_source": system.water_source,
                "collection_capacity_liters": system.collection_capacity_liters,
                "treatment_method": system.treatment_method,
                "treatment_capacity_liters_per_day": system.treatment_capacity_liters_per_day,
                "energy_required_kwh_per_day": system.energy_required_kwh_per_day,
                "lifespan_years": system.lifespan_years,
                "maintenance_level": system.maintenance_level,
                "upfront_cost": system.upfront_cost,
                "region_suitability": system.region_suitability,
                "climate_suitability": [c.name for c in system.climate_suitability],
                "advantages": system.advantages,
                "disadvantages": system.disadvantages,
                "installation_guide_url": system.installation_guide_url,
                "images_urls": system.images_urls
            }
            
            with open(file_path, "w") as f:
                json.dump(system_data, f, indent=2)
                
        except Exception as e:
            logger.error(f"Error saving water system: {e}")
    
    def _save_food_system(self, system: FoodSystem) -> None:
        """Save food system to disk."""
        try:
            file_path = os.path.join(self.data_path, "food_systems", f"{system.system_id}.json")
            
            # Prepare system data
            system_data = {
                "system_id": system.system_id,
                "name": system.name,
                "description": system.description,
                "production_type": system.production_type,
                "area_required_sqm": system.area_required_sqm,
                "water_required_liters_per_day": system.water_required_liters_per_day,
                "typical_yield_calories_per_sqm": system.typical_yield_calories_per_sqm,
                "typical_yield_kg_per_sqm": system.typical_yield_kg_per_sqm,
                "personnel_required_per_hectare": system.personnel_required_per_hectare,
                "energy_required_kwh_per_day": system.energy_required_kwh_per_day,
                "setup_time_months": system.setup_time_months,
                "region_suitability": system.region_suitability,
                "climate_suitability": [c.name for c in system.climate_suitability],
                "advantages": system.advantages,
                "disadvantages": system.disadvantages,
                "implementation_guide_url": system.implementation_guide_url,
                "images_urls": system.images_urls
            }
            
            with open(file_path, "w") as f:
                json.dump(system_data, f, indent=2)
                
        except Exception as e:
            logger.error(f"Error saving food system: {e}")
    
    def _save_community(self, community: Community) -> None:
        """Save community to disk."""
        try:
            file_path = os.path.join(self.data_path, "communities", f"{community.community_id}.json")
            
            # Prepare community data
            community_data = {
                "community_id": community.community_id,
                "name": community.name,
                "region_id": community.region_id,
                "scale": community.scale.name,
                "focus": community.focus.name,
                "governance": community.governance.name,
                "description": community.description,
                "target_population": community.target_population,
                "land_area_acres": community.land_area_acres,
                "bioregion_features": community.bioregion_features,
                "building_systems": community.building_systems,
                "energy_systems": community.energy_systems,
                "water_systems": community.water_systems,
                "food_systems": community.food_systems,
                "skill_requirements": community.skill_requirements,
                "development_phases": community.development_phases,
                "special_features": community.special_features,
                "estimated_implementation_cost": community.estimated_implementation_cost,
                "estimated_annual_operating_cost": community.estimated_annual_operating_cost,
                "mutual_aid_connections": community.mutual_aid_connections,
                "metadata": community.metadata
            }
            
            with open(file_path, "w") as f:
                json.dump(community_data, f, indent=2)
                
        except Exception as e:
            logger.error(f"Error saving community: {e}")
    
    def _initialize_default_building_systems(self) -> None:
        """Initialize default building systems."""
        default_systems = [
            # Rammed Earth
            BuildingSystem(
                system_id="rammed_earth",
                name="Rammed Earth",
                description="Compacted earth construction using local soil mixed with stabilizers. Excellent thermal mass and durability with very low embodied carbon.",
                primary_materials=["Local soil", "Clay", "Sand", "Small amount of cement or lime"],
                skill_level_required=7,
                durability_years=100,
                insulation_value=0.7,  # R-value per inch
                embodied_carbon=20.0,  # kg CO2e/m²
                cost_per_sqm=350.0,
                region_suitability=["southwest", "northern_plains", "great_lakes"],
                climate_suitability=[
                    ClimateZone.DESERT_HOT, ClimateZone.DESERT_COLD, ClimateZone.STEPPE_HOT, 
                    ClimateZone.STEPPE_COLD, ClimateZone.MEDITERRANEAN
                ],
                advantages=[
                    "Extremely low embodied carbon",
                    "Excellent thermal mass",
                    "Fire resistant",
                    "Creates a quiet interior environment",
                    "Low maintenance",
                    "Can use local materials"
                ],
                disadvantages=[
                    "Labor intensive",
                    "Requires skilled builders",
                    "Not suitable for all soil types",
                    "Poor insulation value alone (needs additional insulation in cold climates)",
                    "Heavy - requires good foundation"
                ]
            ),
            
            # Timber Frame with Straw Bale
            BuildingSystem(
                system_id="timber_strawbale",
                name="Timber Frame with Straw Bale Infill",
                description="Timber frame structure with straw bale walls finished with earth plaster. Combines excellent insulation with renewable materials.",
                primary_materials=["Local timber", "Straw bales", "Clay plaster", "Lime plaster"],
                skill_level_required=6,
                durability_years=75,
                insulation_value=3.5,  # R-value per inch
                embodied_carbon=30.0,  # kg CO2e/m²
                cost_per_sqm=400.0,
                region_suitability=["great_lakes", "pacific_northwest", "northern_plains", "ozarks"],
                climate_suitability=[
                    ClimateZone.CONTINENTAL_COOL, ClimateZone.CONTINENTAL_WARM, ClimateZone.OCEANIC,
                    ClimateZone.HUMID_SUBTROPICAL
                ],
                advantages=[
                    "Excellent insulation (R-30 to R-50 walls)",
                    "Uses agricultural waste product",
                    "Good sound insulation",
                    "Non-toxic building materials",
                    "Carbon sequestering",
                    "Can use local/regional materials"
                ],
                disadvantages=[
                    "Requires careful moisture management",
                    "Not suitable for very humid climates without proper detailing",
                    "Requires specific construction knowledge",
                    "Thicker walls than conventional construction",
                    "Needs protection during construction phase"
                ]
            ),
            
            # Cob Construction
            BuildingSystem(
                system_id="cob",
                name="Cob Construction",
                description="Hand-formed earth building technique using clay-rich soil, sand, and straw. Sculptural, beautiful, and very low embodied energy.",
                primary_materials=["Local soil", "Clay", "Sand", "Straw"],
                skill_level_required=5,
                durability_years=100,
                insulation_value=0.5,  # R-value per inch
                embodied_carbon=10.0,  # kg CO2e/m²
                cost_per_sqm=200.0,
                region_suitability=["pacific_northwest", "new_england", "ozarks"],
                climate_suitability=[
                    ClimateZone.MEDITERRANEAN, ClimateZone.OCEANIC, ClimateZone.HUMID_SUBTROPICAL
                ],
                advantages=[
                    "Extremely low embodied carbon",
                    "Can be built by unskilled people with training",
                    "Thermal mass regulates temperatures",
                    "Non-toxic, completely natural",
                    "Highly sculptural - allows organic forms",
                    "Very low cost with local materials"
                ],
                disadvantages=[
                    "Labor intensive",
                    "Poor insulation - needs additional insulation in cold climates",
                    "Requires good roof overhangs for weather protection",
                    "Long drying time during construction",
                    "Limited to 1-2 stories typically"
                ]
            ),
            
            # Modified Earthship
            BuildingSystem(
                system_id="modified_earthship",
                name="Modified Earthship Design",
                description="Passive solar earth-sheltered design adapted from earthship principles. Incorporates thermal mass, passive ventilation, and optimal solar orientation.",
                primary_materials=["Rammed earth tires", "Earth", "Recycled materials", "Timber"],
                skill_level_required=7,
                durability_years=100,
                insulation_value=2.5,  # R-value per inch (average for system)
                embodied_carbon=25.0,  # kg CO2e/m²
                cost_per_sqm=500.0,
                region_suitability=["southwest", "northern_plains", "ozarks"],
                climate_suitability=[
                    ClimateZone.DESERT_HOT, ClimateZone.DESERT_COLD, ClimateZone.STEPPE_HOT, 
                    ClimateZone.STEPPE_COLD, ClimateZone.CONTINENTAL_WARM
                ],
                advantages=[
                    "Energy efficiency through passive solar design",
                    "Thermal mass regulates temperatures",
                    "Earth-sheltered for weather protection",
                    "Can incorporate greywater systems easily",
                    "Can use recycled materials",
                    "Resilient in extreme climates"
                ],
                disadvantages=[
                    "Complex design requiring careful planning",
                    "Labor intensive construction",
                    "Requires specific site orientation",
                    "High skill level for key systems",
                    "Some materials may need to be imported"
                ]
            ),
            
            # Advanced Wood Framing
            BuildingSystem(
                system_id="advanced_framing",
                name="Advanced Wood Framing",
                description="Optimized wood framing techniques that reduce lumber use while allowing for high insulation values. Combines familiar techniques with improved efficiency.",
                primary_materials=["Dimensional lumber", "Engineered wood", "Cellulose insulation"],
                skill_level_required=5,
                durability_years=60,
                insulation_value=3.7,  # R-value per inch with continuous insulation
                embodied_carbon=70.0,  # kg CO2e/m²
                cost_per_sqm=450.0,
                region_suitability=["pacific_northwest", "great_lakes", "new_england", "ozarks"],
                climate_suitability=[
                    ClimateZone.CONTINENTAL_HOT, ClimateZone.CONTINENTAL_WARM, ClimateZone.CONTINENTAL_COOL,
                    ClimateZone.OCEANIC, ClimateZone.HUMID_SUBTROPICAL
                ],
                advantages=[
                    "Very high efficiency (300-400% for heating)",
                    "Both heating and cooling in one system",
                    "Long lifespan with minimal maintenance",
                    "No combustion or carbon emissions on-site",
                    "Stable performance in extreme temperatures",
                    "Lower operating costs than conventional HVAC"
                ],
                disadvantages=[
                    "High initial installation cost",
                    "Requires suitable ground conditions",
                    "Installation disrupts landscape temporarily",
                    "Requires electricity to operate pumps",
                    "May not be cost-effective for small buildings"
                ]
            )
        ]
        
        # Add systems
        for system in default_systems:
            self.energy_systems[system.system_id] = system
            self._save_energy_system(system)
            
        logger.info(f"Initialized {len(default_systems)} default energy systems")
    
    def _initialize_default_water_systems(self) -> None:
        """Initialize default water systems."""
        default_systems = [
            # Rainwater Harvesting
            WaterSystem(
                system_id="rainwater_harvest",
                name="Comprehensive Rainwater Harvesting System",
                description="Collection and storage of rainwater from roofs and other surfaces for various uses from irrigation to potable water.",
                water_source="rain",
                collection_capacity_liters=50000.0,
                treatment_method="Filtration, UV disinfection",
                treatment_capacity_liters_per_day=1000.0,
                energy_required_kwh_per_day=0.5,
                lifespan_years=30,
                maintenance_level=4,
                upfront_cost=10000.0,
                region_suitability=["pacific_northwest", "new_england", "ozarks", "great_lakes"],
                climate_suitability=[
                    ClimateZone.RAINFOREST, ClimateZone.MONSOON, ClimateZone.OCEANIC,
                    ClimateZone.HUMID_SUBTROPICAL
                ],
                advantages=[
                    "Uses free, clean water source",
                    "Reduces demand on groundwater and municipal supplies",
                    "Simple system with minimal moving parts",
                    "Very low operating costs",
                    "Can be retrofitted to existing buildings",
                    "Scalable from small to large applications"
                ],
                disadvantages=[
                    "Dependent on rainfall patterns",
                    "Requires adequate roof/collection area",
                    "Storage tanks require significant space",
                    "Additional treatment needed for potable use",
                    "May require backup water source in dry periods"
                ]
            ),
            
            # Living Machine Greywater
            WaterSystem(
                system_id="living_machine",
                name="Living Machine Greywater System",
                description="Ecological wastewater treatment using a series of engineered wetlands and biological components to purify greywater for reuse.",
                water_source="greywater",
                collection_capacity_liters=5000.0,
                treatment_method="Biological filtration through constructed wetlands",
                treatment_capacity_liters_per_day=2000.0,
                energy_required_kwh_per_day=0.3,
                lifespan_years=25,
                maintenance_level=5,
                upfront_cost=15000.0,
                region_suitability=["pacific_northwest", "ozarks", "great_lakes", "southwest"],
                climate_suitability=[c for c in ClimateZone if c != ClimateZone.TUNDRA and c != ClimateZone.POLAR_ICE],
                advantages=[
                    "Treats water while creating beautiful landscape features",
                    "Minimal energy requirements",
                    "Creates habitat for beneficial insects and wildlife",
                    "Educational opportunity for ecological processes",
                    "Can handle flow variations well",
                    "Produces reusable water for irrigation"
                ],
                disadvantages=[
                    "Requires significant space",
                    "Performance varies with temperature (slower in cold climates)",
                    "Requires some specialized knowledge for maintenance",
                    "More complex than simple greywater systems",
                    "May require greenhouse protection in very cold climates"
                ]
            ),
            
            # Slow Sand Filtration
            WaterSystem(
                system_id="slow_sand",
                name="Slow Sand Filtration System",
                description="Biological water treatment using sand filtration for pathogen removal. Simple, reliable technology for clean drinking water.",
                water_source="surface or rainwater",
                collection_capacity_liters=10000.0,
                treatment_method="Biological sand filtration",
                treatment_capacity_liters_per_day=500.0,
                energy_required_kwh_per_day=0.0,
                lifespan_years=20,
                maintenance_level=3,
                upfront_cost=5000.0,
                region_suitability=["pacific_northwest", "new_england", "ozarks", "great_lakes", "northern_plains"],
                climate_suitability=[c for c in ClimateZone if c != ClimateZone.POLAR_ICE],
                advantages=[
                    "No electricity required (gravity-powered)",
                    "Simple construction with local materials possible",
                    "Very effective pathogen removal",
                    "Low maintenance",
                    "Low operating costs",
                    "Resilient and reliable technology"
                ],
                disadvantages=[
                    "Relatively slow flow rate",
                    "Requires consistent maintenance schedule",
                    "Large footprint compared to mechanical filters",
                    "Less effective with highly turbid water",
                    "Process takes time to establish initially"
                ]
            ),
            
            # Drip Irrigation System
            WaterSystem(
                system_id="drip_irrigation",
                name="Water-Efficient Drip Irrigation",
                description="Precision water delivery system for agricultural and landscape applications, significantly reducing water use compared to conventional irrigation.",
                water_source="any",
                collection_capacity_liters=5000.0,
                treatment_method="Basic filtration",
                treatment_capacity_liters_per_day=5000.0,
                energy_required_kwh_per_day=0.2,
                lifespan_years=10,
                maintenance_level=4,
                upfront_cost=2000.0,
                region_suitability=["southwest", "northern_plains", "great_lakes", "ozarks"],
                climate_suitability=[
                    ClimateZone.DESERT_HOT, ClimateZone.DESERT_COLD, ClimateZone.STEPPE_HOT, 
                    ClimateZone.STEPPE_COLD, ClimateZone.MEDITERRANEAN, ClimateZone.HUMID_SUBTROPICAL
                ],
                advantages=[
                    "Water use reduction of 30-70% compared to conventional irrigation",
                    "Delivers water directly to plant roots",
                    "Reduces weed growth between plants",
                    "Can be automated with simple timers",
                    "Works with low water pressure",
                    "Can use greywater sources"
                ],
                disadvantages=[
                    "Initial installation cost higher than simple irrigation",
                    "Requires filtering to prevent clogging",
                    "Needs regular inspection for leaks or clogs",
                    "Emitters can be damaged by animals or cultivation",
                    "Surface components degrade in UV sunlight"
                ]
            ),
            
            # Fog Collection System
            WaterSystem(
                system_id="fog_collection",
                name="Fog Water Collection System",
                description="Mesh nets that collect water from fog in suitable coastal or mountainous areas, requiring no energy input.",
                water_source="atmospheric moisture",
                collection_capacity_liters=1000.0,
                treatment_method="Basic filtration",
                treatment_capacity_liters_per_day=200.0,
                energy_required_kwh_per_day=0.0,
                lifespan_years=10,
                maintenance_level=3,
                upfront_cost=3000.0,
                region_suitability=["pacific_northwest", "new_england"],
                climate_suitability=[
                    ClimateZone.OCEANIC, ClimateZone.MEDITERRANEAN, ClimateZone.MOUNTAIN
                ],
                advantages=[
                    "Works in drought conditions where fog is present",
                    "No energy requirements",
                    "Simple, passive technology",
                    "Low maintenance requirements",
                    "Can work in areas without other water sources",
                    "Collects clean water requiring minimal treatment"
                ],
                disadvantages=[
                    "Only viable in specific geographic locations with regular fog",
                    "Yield varies significantly with conditions",
                    "Collection area must be in fog path",
                    "Requires regular cleaning of mesh",
                    "Net collectors may be damaged by strong winds"
                ]
            )
        ]
        
        # Add systems
        for system in default_systems:
            self.water_systems[system.system_id] = system
            self._save_water_system(system)
            
        logger.info(f"Initialized {len(default_systems)} default water systems")
    
    def _initialize_default_food_systems(self) -> None:
        """Initialize default food systems."""
        default_systems = [
            # Intensive Annual Gardens
            FoodSystem(
                system_id="intensive_annual",
                name="Intensive Annual Vegetable Production",
                description="Biointensive growing methods for high yields of annual vegetables in small spaces with minimal inputs.",
                production_type="garden",
                area_required_sqm=400.0,  # 0.1 acre
                water_required_liters_per_day=1000.0,
                typical_yield_calories_per_sqm=700.0,
                typical_yield_kg_per_sqm=5.0,
                personnel_required_per_hectare=5.0,
                energy_required_kwh_per_day=0.5,
                setup_time_months=2,
                region_suitability=["pacific_northwest", "great_lakes", "new_england", "ozarks"],
                climate_suitability=[
                    ClimateZone.OCEANIC, ClimateZone.HUMID_SUBTROPICAL, ClimateZone.CONTINENTAL_WARM,
                    ClimateZone.MEDITERRANEAN
                ],
                advantages=[
                    "High productivity in small spaces",
                    "Quick establishment and yields",
                    "Familiar foods and growing methods",
                    "Low startup costs",
                    "Adaptable to many climates with season extension",
                    "Good entry point for new gardeners"
                ],
                disadvantages=[
                    "Labor intensive",
                    "Requires regular irrigation",
                    "Annual replanting necessary",
                    "Soil needs regular replenishment",
                    "Seasonal production without infrastructure",
                    "Susceptible to pest and disease pressure"
                ]
            ),
            
            # Food Forest
            FoodSystem(
                system_id="food_forest",
                name="Perennial Food Forest System",
                description="Multi-layered perennial polyculture mimicking forest structure while producing diverse foods with minimal intervention once established.",
                production_type="agroforestry",
                area_required_sqm=2000.0,  # 0.5 acre
                water_required_liters_per_day=500.0,
                typical_yield_calories_per_sqm=400.0,
                typical_yield_kg_per_sqm=2.0,
                personnel_required_per_hectare=1.0,
                energy_required_kwh_per_day=0.0,
                setup_time_months=36,
                region_suitability=["pacific_northwest", "great_lakes", "new_england", "ozarks", "southwest"],
                climate_suitability=[c for c in ClimateZone if c != ClimateZone.POLAR_ICE and c != ClimateZone.TUNDRA],
                advantages=[
                    "Low maintenance once established",
                    "Drought resistant after establishment",
                    "Builds soil health over time",
                    "Creates wildlife habitat",
                    "Diverse yields throughout seasons",
                    "Carbon sequestration and microclimate benefits"
                ],
                disadvantages=[
                    "Long establishment period (3-7 years)",
                    "Higher initial investment",
                    "Requires careful planning and design",
                    "Lower caloric yield than annual gardens",
                    "Some specialized knowledge required",
                    "Harvesting can be more time-consuming"
                ]
            ),
            
            # Aquaponics System
            FoodSystem(
                system_id="aquaponics",
                name="Integrated Aquaponics System",
                description="Closed-loop system combining fish cultivation and hydroponics, producing fish protein and vegetables with minimal water use.",
                production_type="aquaponics",
                area_required_sqm=200.0,
                water_required_liters_per_day=50.0,  # Minimal daily topoff
                typical_yield_calories_per_sqm=900.0,
                typical_yield_kg_per_sqm=10.0,
                personnel_required_per_hectare=10.0,
                energy_required_kwh_per_day=5.0,
                setup_time_months=3,
                region_suitability=["pacific_northwest", "great_lakes", "southwest", "ozarks"],
                climate_suitability=[c for c in ClimateZone], # All climates with greenhouse
                advantages=[
                    "Very water efficient (95% less than conventional agriculture)",
                    "Produces both protein and vegetables",
                    "Year-round production possible",
                    "No soil required",
                    "High productivity in small space",
                    "Can be situated on marginal land or indoors"
                ],
                disadvantages=[
                    "Requires reliable electricity",
                    "Technical knowledge required",
                    "Higher startup costs",
                    "System complexity and interdependence",
                    "Energy intensive in cold climates",
                    "Risk of total system failure affecting both components"
                ]
            ),
            
            # Rotational Grazing
            FoodSystem(
                system_id="rotational_grazing",
                name="Regenerative Rotational Grazing",
                description="Managed livestock grazing system that builds soil, sequesters carbon, and produces animal products while improving ecosystem health.",
                production_type="grazing",
                area_required_sqm=40000.0,  # 4 hectares
                water_required_liters_per_day=2000.0,
                typical_yield_calories_per_sqm=50.0,
                typical_yield_kg_per_sqm=0.1,
                personnel_required_per_hectare=0.2,
                energy_required_kwh_per_day=0.1,
                setup_time_months=6,
                region_suitability=["northern_plains", "great_lakes", "ozarks", "new_england"],
                climate_suitability=[
                    ClimateZone.CONTINENTAL_HOT, ClimateZone.CONTINENTAL_WARM, ClimateZone.CONTINENTAL_COOL,
                    ClimateZone.HUMID_SUBTROPICAL, ClimateZone.OCEANIC, ClimateZone.STEPPE_HOT, ClimateZone.STEPPE_COLD
                ],
                advantages=[
                    "Builds soil carbon and fertility",
                    "Converts inedible grass to human food",
                    "Can be combined with silvopasture for tree crops",
                    "Low input costs after establishment",
                    "Improves wildlife habitat and biodiversity",
                    "Works on marginal land unsuitable for crops"
                ],
                disadvantages=[
                    "Requires significant land area",
                    "Lower caloric yield per acre than crops",
                    "Requires knowledge of animal husbandry",
                    "Infrastructure costs for fencing and water",
                    "Daily management required",
                    "Winter feed may be necessary in some climates"
                ]
            ),
            
            # Greenhouse
            FoodSystem(
                system_id="passive_greenhouse",
                name="Passive Solar Greenhouse",
                description="Energy-efficient growing structure using passive solar design for year-round production with minimal supplemental heating.",
                production_type="protected cultivation",
                area_required_sqm=100.0,
                water_required_liters_per_day=300.0,
                typical_yield_calories_per_sqm=1200.0,
                typical_yield_kg_per_sqm=15.0,
                personnel_required_per_hectare=20.0,
                energy_required_kwh_per_day=1.0,
                setup_time_months=4,
                region_suitability=["northern_plains", "great_lakes", "new_england", "pacific_northwest"],
                climate_suitability=[
                    ClimateZone.CONTINENTAL_HOT, ClimateZone.CONTINENTAL_WARM, ClimateZone.CONTINENTAL_COOL,
                    ClimateZone.SUBARCTIC, ClimateZone.OCEANIC
                ],
                advantages=[
                    "Extends growing season in cold climates",
                    "Protects crops from extreme weather",
                    "High productivity per square foot",
                    "Year-round production possible",
                    "Can integrate aquaponics or vertical systems",
                    "Good microclimate for starting seedlings"
                ],
                disadvantages=[
                    "Higher initial cost",
                    "Requires good solar exposure",
                    "More technical knowledge required",
                    "Needs ventilation management",
                    "Can overheat without proper design",
                    "May need supplemental heat in extreme cold"
                ]
            )
        ]
        
        # Add systems
        for system in default_systems:
            self.food_systems[system.system_id] = system
            self._save_food_system(system)
            
        logger.info(f"Initialized {len(default_systems)} default food systems")
    
    def _initialize_default_communities(self) -> None:
        """Initialize default community templates."""
        default_communities = [
            # Pacific Northwest Forest Village
            Community(
                community_id="pnw_forest_village",
                name="Cascadia Forest Village",
                region_id="pacific_northwest",
                scale=CommunityScale.VILLAGE,
                focus=CommunityFocus.ECOLOGICAL,
                governance=GovernanceModel.SOCIOCRACY,
                description="A forest-integrated village designed for the Pacific Northwest, emphasizing timber resources, water abundance, and ecological restoration.",
                target_population=200,
                land_area_acres=120.0,
                bioregion_features=[
                    "Mixed conifer forest integration",
                    "Salmon-bearing stream restoration",
                    "Moderate rainfall harvesting",
                    "Forest understory food forest"
                ],
                building_systems=["timber_strawbale", "cob", "advanced_framing"],
                energy_systems=["solar_battery", "micro_hydro"],
                water_systems=["rainwater_harvest", "living_machine"],
                food_systems=["food_forest", "intensive_annual", "passive_greenhouse"],
                skill_requirements={
                    "ecological_restoration": 5,
                    "forestry": 3,
                    "timber_framing": 2,
                    "renewable_energy": 2,
                    "education": 3,
                    "permaculture": 4,
                    "community_facilitation": 3
                },
                development_phases=[
                    {
                        "name": "Foundation Phase",
                        "duration_months": 6,
                        "focus": "Site assessment, initial infrastructure, temporary housing"
                    },
                    {
                        "name": "Core Establishment",
                        "duration_months": 18,
                        "focus": "Primary buildings, water systems, initial food systems"
                    },
                    {
                        "name": "Growth Phase",
                        "duration_months": 36,
                        "focus": "Additional housing, economic development, forest management plan"
                    },
                    {
                        "name": "Resilience Phase",
                        "duration_months": 60,
                        "focus": "Education center, expanded food production, seed saving program"
                    }
                ],
                special_features=[
                    "Forest education center",
                    "Riparian restoration project",
                    "Timber processing facility",
                    "Salmon habitat enhancement",
                    "Native plant nursery"
                ],
                estimated_implementation_cost=4000000.0,
                estimated_annual_operating_cost=250000.0,
                mutual_aid_connections=[]
            ),
            
            # Great Lakes Agrarian Town
            Community(
                community_id="great_lakes_agrarian",
                name="Great Lakes Agrarian Community",
                region_id="great_lakes",
                scale=CommunityScale.TOWN,
                focus=CommunityFocus.AGRICULTURAL,
                governance=GovernanceModel.COUNCIL,
                description="An agricultural community designed for the Great Lakes region, focusing on regenerative farming practices and value-added food processing.",
                target_population=500,
                land_area_acres=800.0,
                bioregion_features=[
                    "Prime agricultural land restoration",
                    "Four-season cultivation systems",
                    "Freshwater access management",
                    "Forest woodlot integration"
                ],
                building_systems=["advanced_framing", "timber_strawbale", "rammed_earth"],
                energy_systems=["solar_battery", "small_wind", "biogas"],
                water_systems=["rainwater_harvest", "drip_irrigation"],
                food_systems=["rotational_grazing", "intensive_annual", "passive_greenhouse", "food_forest"],
                skill_requirements={
                    "regenerative_agriculture": 8,
                    "animal_husbandry": 4,
                    "food_processing": 5,
                    "carpentry": 4,
                    "community_organizing": 3,
                    "equipment_maintenance": 4,
                    "seed_saving": 3
                },
                development_phases=[
                    {
                        "name": "Land Restoration",
                        "duration_months": 12,
                        "focus": "Soil remediation, water systems, initial pasture establishment"
                    },
                    {
                        "name": "Core Infrastructure",
                        "duration_months": 18,
                        "focus": "Primary housing, barns, processing facilities, energy systems"
                    },
                    {
                        "name": "Agricultural Development",
                        "duration_months": 24,
                        "focus": "Expanding fields, food forests, animal systems, greenhouses"
                    },
                    {
                        "name": "Community Completion",
                        "duration_months": 48,
                        "focus": "Education facilities, additional housing, markets, distribution systems"
                    }
                ],
                special_features=[
                    "Grain processing facility",
                    "Community supported agriculture program",
                    "Regional seed bank",
                    "Four-season farmers market",
                    "Agricultural equipment sharing system"
                ],
                estimated_implementation_cost=7000000.0,
                estimated_annual_operating_cost=400000.0,
                mutual_aid_connections=[]
            ),
            
            # Southwest Desert Oasis
            Community(
                community_id="southwest_oasis",
                name="Desert Oasis Community",
                region_id="southwest",
                scale=CommunityScale.NEIGHBORHOOD,
                focus=CommunityFocus.WATER,
                governance=GovernanceModel.CONSENSUS,
                description="A water-wise desert community demonstrating regenerative living in arid conditions through careful water harvesting and management.",
                target_population=75,
                land_area_acres=50.0,
                bioregion_features=[
                    "Desert wash water harvesting",
                    "Xeriscaping throughout",
                    "Shaded microclimate creation",
                    "Desert soil building"
                ],
                building_systems=["rammed_earth", "modified_earthship"],
                energy_systems=["solar_battery"],
                water_systems=["rainwater_harvest", "drip_irrigation"],
                food_systems=["food_forest", "aquaponics"],
                skill_requirements={
                    "water_management": 7,
                    "desert_ecology": 4,
                    "natural_building": 5,
                    "solar_energy": 4,
                    "arid_land_restoration": 4,
                    "xeriscaping": 3,
                    "community_facilitation": 2
                },
                development_phases=[
                    {
                        "name": "Water Systems Establishment",
                        "duration_months": 12,
                        "focus": "Water harvesting earthworks, cisterns, initial shade structures"
                    },
                    {
                        "name": "Core Habitat Development",
                        "duration_months": 18,
                        "focus": "Primary buildings, solar systems, initial food production"
                    },
                    {
                        "name": "Expansion Phase",
                        "duration_months": 24,
                        "focus": "Additional housing, expanded water catchment, food forest"
                    },
                    {
                        "name": "Demonstration Completion",
                        "duration_months": 24,
                        "focus": "Education center, visitor facilities, expanded systems"
                    }
                ],
                special_features=[
                    "Desert water harvesting demonstration site",
                    "Shadehouse nursery for native and food plants",
                    "Passive cooling systems",
                    "Desert permaculture educational programs",
                    "Native pollinator habitat restoration"
                ],
                estimated_implementation_cost=2500000.0,
                estimated_annual_operating_cost=150000.0,
                mutual_aid_connections=[]
            ),
            
            # Northern Plains Regenerative Hub
            Community(
                community_id="plains_regenerative",
                name="Great Plains Regeneration Center",
                region_id="northern_plains",
                scale=CommunityScale.SMALL_CITY,
                focus=CommunityFocus.MIXED_USE,
                governance=GovernanceModel.SOCIOCRACY,
                description="A regenerative hub for the Great Plains designed to restore grasslands while creating a resilient community with agricultural and manufacturing capacity.",
                target_population=2000,
                land_area_acres=5000.0,
                bioregion_features=[
                    "Tallgrass prairie restoration",
                    "Watershed regeneration",
                    "Windbreak development",
                    "Soil carbon sequestration"
                ],
                building_systems=["advanced_framing", "straw_bale", "rammed_earth"],
                energy_systems=["small_wind", "solar_battery", "biogas"],
                water_systems=["rainwater_harvest", "drip_irrigation"],
                food_systems=["rotational_grazing", "intensive_annual", "food_forest"],
                skill_requirements={
                    "grassland_restoration": 5,
                    "regenerative_agriculture": 8,
                    "renewable_energy": 6,
                    "community_planning": 4,
                    "manufacturing": 7,
                    "water_management": 5,
                    "education": 4
                },
                development_phases=[
                    {
                        "name": "Initial Settlement",
                        "duration_months": 12,
                        "focus": "Core infrastructure, temporary housing, initial watershed work"
                    },
                    {
                        "name": "Agricultural Systems",
                        "duration_months": 24,
                        "focus": "Grazing setup, wind systems, primary housing, soil building"
                    },
                    {
                        "name": "Manufacturing Development",
                        "duration_months": 36,
                        "focus": "Production facilities, additional housing, expanded energy"
                    },
                    {
                        "name": "Regional Hub Completion",
                        "duration_months": 48,
                        "focus": "Education center, processing facilities, distribution network"
                    }
                ],
                special_features=[
                    "Bison restoration program",
                    "Wind turbine manufacturing facility",
                    "Regenerative grazing demonstration",
                    "Climate-appropriate building center",
                    "Prairie seed bank and nursery"
                ],
                estimated_implementation_cost=15000000.0,
                estimated_annual_operating_cost=1200000.0,
                mutual_aid_connections=[]
            )
        ]
        
        # Add communities
        for community in default_communities:
            self.communities[community.community_id] = community
            self._save_community(community)
            
        logger.info(f"Initialized {len(default_communities)} default community templates")
    
    def get_community(self, community_id: str) -> Optional[Community]:
        """
        Get a community by ID.
        
        Args:
            community_id: Community identifier
            
        Returns:
            Community if found, None otherwise
        """
        return self.communities.get(community_id)
    
    def get_all_communities(self) -> List[Community]:
        """
        Get all communities.
        
        Returns:
            List of communities
        """
        return list(self.communities.values())
    
    def add_community(self, community: Community) -> bool:
        """
        Add a new community.
        
        Args:
            community: Community to add
            
        Returns:
            Success status
        """
        # Check if already exists
        if community.community_id in self.communities:
            return False
            
        # Add community
        self.communities[community.community_id] = community
        
        # Save to disk
        self._save_community(community)
        
        return True
    
    def update_community(self, community: Community) -> bool:
        """
        Update an existing community.
        
        Args:
            community: Community to update
            
        Returns:
            Success status
        """
        # Check if exists
        if community.community_id not in self.communities:
            return False
            
        # Update community
        self.communities[community.community_id] = community
        
        # Save to disk
        self._save_community(community)
        
        return True
    
    def get_building_system(self, system_id: str) -> Optional[BuildingSystem]:
        """Get a building system by ID."""
        return self.building_systems.get(system_id)
    
    def get_energy_system(self, system_id: str) -> Optional[EnergySystem]:
        """Get an energy system by ID."""
        return self.energy_systems.get(system_id)
    
    def get_water_system(self, system_id: str) -> Optional[WaterSystem]:
        """Get a water system by ID."""
        return self.water_systems.get(system_id)
    
    def get_food_system(self, system_id: str) -> Optional[FoodSystem]:
        """Get a food system by ID."""
        return self.food_systems.get(system_id)
    
    def find_communities_for_region(self, region_id: str) -> List[Community]:
        """
        Find community templates suitable for a specific region.
        
        Args:
            region_id: Region identifier
            
        Returns:
            List of suitable communities
        """
        # Find all communities for this region
        region_communities = [c for c in self.communities.values() if c.region_id == region_id]
        
        # If none specific to this region, find communities with adaptable designs
        if not region_communities:
            # Check all communities
            region_communities = []
            
            for community in self.communities.values():
                # Check if building systems are adaptable to this region
                building_suitable = any(
                    self.building_systems.get(b_id) and region_id in self.building_systems[b_id].region_suitability
                    for b_id in community.building_systems
                )
                
                # Check if water systems are adaptable to this region
                water_suitable = any(
                    self.water_systems.get(w_id) and region_id in self.water_systems[w_id].region_suitability
                    for w_id in community.water_systems
                )
                
                if building_suitable and water_suitable:
                    region_communities.append(community)
                    
        return region_communities
    
    def design_community_for_region(self, 
                                 region_id: str,
                                 scale: CommunityScale,
                                 focus: CommunityFocus,
                                 name: str = None) -> Optional[Community]:
        """
        Design a custom community template for a specific region.
        
        Args:
            region_id: Region identifier
            scale: Community scale
            focus: Community focus
            name: Optional name
            
        Returns:
            Custom community design
        """
        # Get region
        region = self.mapper.get_region(region_id)
        if not region:
            return None
            
        # Generate community ID
        community_id = f"{region_id}_{focus.name.lower()}_{scale.name.lower()}"
        
        # Generate name if not provided
        if not name:
            name = f"{region.name} {focus.name.title()} {scale.name.title()}"
            
        # Determine appropriate governance models based on scale
        governance = GovernanceModel.CONSENSUS
        if scale == CommunityScale.TOWN:
            governance = GovernanceModel.SOCIOCRACY
        elif scale == CommunityScale.SMALL_CITY:
            governance = GovernanceModel.COUNCIL
        elif scale == CommunityScale.REGIONAL_HUB:
            governance = GovernanceModel.REPRESENTATIVE
            
        # Determine population based on scale
        population_by_scale = {
            CommunityScale.NEIGHBORHOOD: 100,
            CommunityScale.VILLAGE: 250,
            CommunityScale.TOWN: 1000,
            CommunityScale.SMALL_CITY: 5000,
            CommunityScale.REGIONAL_HUB: 10000
        }
        target_population = population_by_scale.get(scale, 250)
        
        # Determine land area based on scale and region characteristics
        base_land_area = {
            CommunityScale.NEIGHBORHOOD: 50.0,
            CommunityScale.VILLAGE: 200.0,
            CommunityScale.TOWN: 800.0,
            CommunityScale.SMALL_CITY: 3000.0,
            CommunityScale.REGIONAL_HUB: 8000.0
        }
        land_area = base_land_area.get(scale, 200.0)
        
        # Adjust land area based on region characteristics
        if region.metrics.water_availability.value <= WaterAvailability.STRESSED.value:
            land_area *= 1.5  # Need more land in water-stressed regions
        if region.metrics.soil_quality.value <= SoilQuality.MODERATE.value:
            land_area *= 1.3  # Need more land with moderate soil
            
        # Select suitable building systems
        climate_zone = region.metrics.climate_zone
        building_systems = []
        
        for system_id, system in self.building_systems.items():
            if region_id in system.region_suitability or climate_zone in system.climate_suitability:
                building_systems.append(system_id)
                
        building_systems = building_systems[:3]  # Limit to top 3
        
        # Select suitable energy systems
        energy_systems = []
        
        # Check region's energy potential
        if region.metrics.renewable_energy_potential.get("solar", 0) > 20000000000:
            energy_systems.append("solar_battery")
        if region.metrics.renewable_energy_potential.get("wind", 0) > 20000000000:
            energy_systems.append("small_wind")
        if region.metrics.renewable_energy_potential.get("hydro", 0) > 5000000000:
            energy_systems.append("micro_hydro")
            
        # Add biogas for agricultural focus
        if focus == CommunityFocus.AGRICULTURAL:
            energy_systems.append("biogas")
            
        # Add geothermal where appropriate
        if climate_zone in [ClimateZone.CONTINENTAL_COOL, ClimateZone.CONTINENTAL_WARM, 
                           ClimateZone.CONTINENTAL_HOT, ClimateZone.SUBARCTIC]:
            energy_systems.append("geothermal_heat")
            
        # Ensure at least one energy system
        if not energy_systems:
            energy_systems.append("solar_battery")
            
        # Select suitable water systems
        water_systems = []
        
        if region.metrics.water_availability.value >= WaterAvailability.SUFFICIENT.value:
            water_systems.append("rainwater_harvest")
            
        # Add appropriate water management systems based on climate
        if climate_zone in [ClimateZone.DESERT_HOT, ClimateZone.DESERT_COLD, 
                           ClimateZone.STEPPE_HOT, ClimateZone.STEPPE_COLD]:
            water_systems.append("drip_irrigation")
        else:
            water_systems.append("living_machine")
            
        # Add slow sand filtration for most regions
        water_systems.append("slow_sand")
        
        # Add fog collection for suitable regions
        if climate_zone in [ClimateZone.OCEANIC, ClimateZone.MEDITERRANEAN] and "coastal" in region.name.lower():
            water_systems.append("fog_collection")
            
        # Select suitable food systems
        food_systems = []
        
        # Add food systems based on focus
        if focus == CommunityFocus.AGRICULTURAL:
            food_systems.extend(["rotational_grazing", "intensive_annual"])
        else:
            food_systems.append("intensive_annual")
            
        # Add appropriate systems based on climate
        if climate_zone in [ClimateZone.CONTINENTAL_COOL, ClimateZone.CONTINENTAL_WARM, 
                           ClimateZone.CONTINENTAL_HOT, ClimateZone.SUBARCTIC]:
            food_systems.append("passive_greenhouse")
            
        # Add food forest for most regions
        if climate_zone not in [ClimateZone.DESERT_HOT, ClimateZone.DESERT_COLD, ClimateZone.POLAR_ICE]:
            food_systems.append("food_forest")
            
        # Add aquaponics for specialized production
        if focus in [CommunityFocus.TECHNOLOGICAL, CommunityFocus.EDUCATIONAL]:
            food_systems.append("aquaponics")
            
        # Determine bioregion features
        bioregion_features = []
        
        # Add features based on region ecosystems
        for ecosystem in region.metrics.ecosystem_types:
            if ecosystem == EcosystemType.FOREST_TEMPERATE:
                bioregion_features.append("Temperate forest integration")
            elif ecosystem == EcosystemType.GRASSLAND:
                bioregion_features.append("Native grassland restoration")
            elif ecosystem == EcosystemType.DESERT:
                bioregion_features.append("Desert ecology preservation")
            elif ecosystem == EcosystemType.WETLAND:
                bioregion_features.append("Wetland conservation and expansion")
                
        # Add water-related feature
        if region.metrics.water_availability.value >= WaterAvailability.SUFFICIENT.value:
            bioregion_features.append("Watershed protection and enhancement")
        else:
            bioregion_features.append("Water conservation and harvesting systems")
            
        # Add climate feature
        bioregion_features.append(f"{climate_zone.name.replace('_', ' ').title()} climate adaptation strategies")
        
        # Determine required skills based on focus and systems
        skill_requirements = {
            "community_facilitation": 3,  # Always needed
            "ecological_literacy": 4,     # Always needed
            "infrastructure_maintenance": 3  # Always needed
        }
        
        # Add skills based on focus
        if focus == CommunityFocus.AGRICULTURAL:
            skill_requirements.update({
                "regenerative_agriculture": 5,
                "food_processing": 4,
                "seed_saving": 3
            })
        elif focus == CommunityFocus.ECOLOGICAL:
            skill_requirements.update({
                "ecosystem_restoration": 5,
                "wildlife_management": 3,
                "botanical_knowledge": 4
            })
        elif focus == CommunityFocus.EDUCATIONAL:
            skill_requirements.update({
                "teaching": 5,
                "curriculum_development": 4,
                "facilitation": 4
            })
        elif focus == CommunityFocus.MANUFACTURING:
            skill_requirements.update({
                "fabrication": 5,
                "material_processing": 4,
                "design": 4
            })
        elif focus == CommunityFocus.ENERGY:
            skill_requirements.update({
                "renewable_energy": 5,
                "electrical_systems": 4,
                "energy_storage": 4
            })
            
        # Create phased development plan
        development_phases = [
            {
                "name": "Foundation Phase",
                "duration_months": 12,
                "focus": "Site assessment, initial infrastructure, temporary housing, resource inventory"
            },
            {
                "name": "Core Development",
                "duration_months": 24,
                "focus": "Primary buildings, basic systems, initial food production, governance establishment"
            },
            {
                "name": "Expansion Phase",
                "duration_months": 36,
                "focus": "Additional housing, expanded production, specialized facilities, refinement of systems"
            },
            {
                "name": "Maturity & Outreach",
                "duration_months": 48,
                "focus": "Education programs, regional connections, resilience enhancements, cultural development"
            }
        ]
        
        # Calculate estimated costs
        base_implementation_cost = {
            CommunityScale.NEIGHBORHOOD: 2000000.0,
            CommunityScale.VILLAGE: 5000000.0,
            CommunityScale.TOWN: 15000000.0,
            CommunityScale.SMALL_CITY: 50000000.0,
            CommunityScale.REGIONAL_HUB: 120000000.0
        }
        
        base_operating_cost = {
            CommunityScale.NEIGHBORHOOD: 150000.0,
            CommunityScale.VILLAGE: 400000.0,
            CommunityScale.TOWN: 1200000.0,
            CommunityScale.SMALL_CITY: 4000000.0,
            CommunityScale.REGIONAL_HUB: 10000000.0
        }
        
        # Adjust costs based on region and focus
        implementation_cost = base_implementation_cost.get(scale, 5000000.0)
        operating_cost = base_operating_cost.get(scale, 400000.0)
        
        # Adjust for infrastructure status
        if region.metrics.infrastructure_status.value <= InfrastructureStatus.DEGRADED.value:
            implementation_cost *= 1.3  # Higher cost in regions with poor infrastructure
            
        # Create community design
        community = Community(
            community_id=community_id,
            name=name,
            region_id=region_id,
            scale=scale,
            focus=focus,
            governance=governance,
            description=f"Custom {focus.name.lower()} community designed for the {region.name}, emphasizing sustainable development tailored to local bioregional characteristics.",
            target_population=target_population,
            land_area_acres=land_area,
            bioregion_features=bioregion_features,
            building_systems=building_systems,
            energy_systems=energy_systems,
            water_systems=water_systems,
            food_systems=food_systems,
            skill_requirements=skill_requirements,
            development_phases=development_phases,
            special_features=[],  # To be customized
            estimated_implementation_cost=implementation_cost,
            estimated_annual_operating_cost=operating_cost,
            mutual_aid_connections=[]
        )
        
        return community
    
    def calculate_community_requirements(self, community: Community) -> Dict[str, Any]:
        """
        Calculate detailed requirements for implementing a community design.
        
        Args:
            community: Community design
            
        Returns:
            Detailed requirements
        """
        try:
            # Calculate total material requirements
            building_materials = {}
            
            # Process building systems
            for system_id in community.building_systems:
                building_system = self.building_systems.get(system_id)
                if building_system:
                    # Calculate average dwelling size
                    avg_dwelling_size = 100.0  # square meters
                    
                    # Estimate number of dwellings based on population
                    dwellings = math.ceil(community.target_population / 2.5)  # Average household size
                    
                    # Calculate material requirements
                    total_area = dwellings * avg_dwelling_size
                    
                    for material in building_system.primary_materials:
                        if material in building_materials:
                            building_materials[material] += total_area / len(building_system.primary_materials)
                        else:
                            building_materials[material] = total_area / len(building_system.primary_materials)
            
            # Calculate infrastructure requirements
            infrastructure_requirements = {
                "road_length_km": math.sqrt(community.land_area_acres * 0.004) * 3,  # Approximate road network
                "water_storage_liters": community.target_population * 200,  # 200 liters per person
                "common_buildings": math.ceil(community.target_population / 200) + 3  # Community buildings
            }
            
            # Calculate energy requirements
            energy_requirements = {
                "daily_consumption_kwh": community.target_population * 2.5,  # Per person
                "peak_capacity_kw": community.target_population * 0.8,
                "storage_capacity_kwh": community.target_population * 3.0
            }
            
            # Calculate water requirements
            water_requirements = {
                "daily_consumption_liters": community.target_population * 150,  # 150 liters per person per day
                "irrigation_liters": sum(
                    self.food_systems.get(f_id).water_required_liters_per_day
                    for f_id in community.food_systems
                    if f_id in self.food_systems
                )
            }
            
            # Calculate food production capacity
            food_capacity = 0.0
            food_area_required = 0.0
            
            for system_id in community.food_systems:
                food_system = self.food_systems.get(system_id)
                if food_system:
                    # Calculate area based on scale
                    if food_system.production_type == "garden":
                        area = max(food_system.area_required_sqm * (community.target_population / 100), food_system.area_required_sqm)
                    elif food_system.production_type == "agroforestry":
                        area = max(food_system.area_required_sqm * (community.target_population / 50), food_system.area_required_sqm)
                    elif food_system.production_type == "grazing":
                        area = max(food_system.area_required_sqm * (community.target_population / 25), food_system.area_required_sqm)
                    else:
                        area = food_system.area_required_sqm * (community.target_population / 100)
                        
                    # Calculate calories produced
                    calories = area * food_system.typical_yield_calories_per_sqm
                    
                    # Add to totals
                    food_capacity += calories
                    food_area_required += area
                    
            # Calculate percentage of food self-sufficiency
            daily_calorie_needs = community.target_population * 2200  # 2200 calories per person per day
            annual_calorie_needs = daily_calorie_needs * 365
            annual_production = food_capacity * 365
            
            food_self_sufficiency = min(100.0, (annual_production / annual_calorie_needs) * 100) if annual_calorie_needs > 0 else 0
            
            # Calculate labor requirements
            core_team_size = max(3, math.ceil(community.target_population / 100))
            
            labor_requirements = {
                "core_planning_team": core_team_size,
                "construction_phase": math.ceil(dwellings / 4) + 5,  # Based on building needs
                "agricultural_workers": math.ceil(food_area_required / 10000)  # 1 worker per hectare
            }
            
            # Calculate implementation timeline
            total_implementation_months = max(
                phase["duration_months"] for phase in community.development_phases
            ) if community.development_phases else 60
            
            # Return all calculations
            return {
                "building_materials": building_materials,
                "infrastructure_requirements": infrastructure_requirements,
                "energy_requirements": energy_requirements,
                "water_requirements": water_requirements,
                "food_production": {
                    "annual_calories": annual_production,
                    "self_sufficiency_percent": food_self_sufficiency,
                    "area_required_sqm": food_area_required
                },
                "labor_requirements": labor_requirements,
                "implementation_timeline_months": total_implementation_months
            }
            
        except Exception as e:
            logger.error(f"Error calculating community requirements: {e}")
            return {"error": str(e)}


# ====================================================================
# 3. COLLABORATIVE RELOCATION NETWORK
# ====================================================================

class RelocationProjectStatus(Enum):
    """Status of relocation project."""
    PROPOSED = auto()       # Initial proposal stage
    PLANNING = auto()       # Active planning stage
    RECRUITING = auto()     # Recruiting participants
    PREPARING = auto()      # Preparations underway
    RELOCATING = auto()     # Active relocation happening
    ESTABLISHED = auto()    # Community established
    ON_HOLD = auto()        # Temporarily paused
    CANCELLED = auto()      # Project cancelled


class SkillCategory(Enum):
    """Categories of skills for relocation matching."""
    AGRICULTURE = auto()     # Farming, gardening, etc.
    BUILDING = auto()        # Construction, building trades
    ENERGY = auto()          # Renewable energy systems
    WATER = auto()           # Water management
    HEALTHCARE = auto()      # Medical, first aid, herbalism
    EDUCATION = auto()       # Teaching, facilitation
    GOVERNANCE = auto()      # Community organization
    MANUFACTURING = auto()   # Making, fabrication
    ECOLOGY = auto()         # Ecosystem knowledge
    CRAFT = auto()           # Traditional crafts
    TECHNOLOGY = auto()      # Digital, communications
    CARE = auto()            # Childcare, elder care


@dataclass
class HumanRelocator:
    """Human participant in relocation project."""
    human_id: str
    name: str
    current_region: str
    preferred_regions: List[str]
    skills: Dict[str, float]  # Skill category -> proficiency (0-1)
    interests: List[str]
    constraints: List[str]
    household_size: int
    has_children: bool
    preferred_community_scale: Optional[CommunityScale] = None
    preferred_community_focus: Optional[CommunityFocus] = None
    preferred_governance: Optional[GovernanceModel] = None
    relocation_timeline_months: Optional[int] = None
    resources_available: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RelocationProject:
    """Collaborative community relocation project."""
    project_id: str
    name: str
    target_region_id: str
    status: RelocationProjectStatus
    description: str
    community_model_id: Optional[str]  # Reference to Community template
    target_population: int
    current_participants: List[str]  # Human IDs
    project_coordinators: List[str]  # Human IDs of coordinators
    start_date: float
    projected_completion_date: Optional[float] = None
    land_status: str = "Seeking"  # "Seeking", "In negotiation", "Secured"
    project_phases: List[Dict[str, Any]] = field(default_factory=list)
    community_agreements: Dict[str, Any] = field(default_factory=dict)
    skill_coverage: Dict[str, float] = field(default_factory=dict)
    skill_gaps: Dict[str, float] = field(default_factory=dict)
    mutual_aid_partnerships: List[str] = field(default_factory=list)  # Other project IDs
    updates: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MutualAidOffer:
    """Offer of mutual aid between communities."""
    offer_id: str
    source_id: str  # Community or project ID
    target_id: str  # Community or project ID
    offer_type: str  # "skills", "resources", "knowledge", etc.
    description: str
    quantity: Optional[str] = None
    duration: Optional[str] = None
    conditions: List[str] = field(default_factory=list)
    status: str = "offered"  # "offered", "accepted", "fulfilled", "declined"
    contact_human_id: str = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class CollaborativeRelocationNetwork:
    """
    Network for coordinating collaborative relocation and community formation.
    """
    
    def __init__(self,
                bioregional_mapper: BioregionalMapper,
                community_designer: SustainableCommunityDesigner,
                data_path: str = "relocation_data"):
        """
        Initialize collaborative relocation network.
        
        Args:
            bioregional_mapper: Bioregional mapper
            community_designer: Sustainable community designer
            data_path: Path for storing relocation data
        """
        self.mapper = bioregional_mapper
        self.designer = community_designer
        self.data_path = data_path
        
        # Ensure paths exist
        os.makedirs(data_path, exist_ok=True)
        os.makedirs(os.path.join(data_path, "relocators"), exist_ok=True)
        os.makedirs(os.path.join(data_path, "projects"), exist_ok=True)
        os.makedirs(os.path.join(data_path, "aid_offers"), exist_ok=True)
        
        # Load data
        self.relocators: Dict[str, HumanRelocator] = {}
        self.projects: Dict[str, RelocationProject] = {}
        self.aid_offers: Dict[str, MutualAidOffer] = {}
        
        self._load_data()
    
    def _load_data(self) -> None:
        """Load relocation data from disk."""
        try:
            # Load relocators
            relocators_dir = os.path.join(self.data_path, "relocators")
            for filename in os.listdir(relocators_dir):
                if filename.endswith(".json"):
                    file_path = os.path.join(relocators_dir, filename)
                    try:
                        with open(file_path, "r") as f:
                            data = json.load(f)
                            
                            # Parse community scale preference if present
                            preferred_scale = None
                            if "preferred_community_scale" in data and data["preferred_community_scale"]:
                                preferred_scale = CommunityScale[data["preferred_community_scale"]]
                                
                            # Parse community focus preference if present
                            preferred_focus = None
                            if "preferred_community_focus" in data and data["preferred_community_focus"]:
                                preferred_focus = CommunityFocus[data["preferred_community_focus"]]
                                
                            # Parse governance preference if present
                            preferred_governance = None
                            if "preferred_governance" in data and data["preferred_governance"]:
                                preferred_governance = GovernanceModel[data["preferred_governance"]]
                            
                            relocator = HumanRelocator(
                                human_id=data.get("human_id", filename.replace(".json", "")),
                                name=data.get("name", "Unknown"),
                                current_region=data.get("current_region", ""),
                                preferred_regions=data.get("preferred_regions", []),
                                skills=data.get("skills", {}),
                                interests=data.get("interests", []),
                                constraints=data.get("constraints", []),
                                household_size=data.get("household_size", 1),
                                has_children=data.get("has_children", False),
                                preferred_community_scale=preferred_scale,
                                preferred_community_focus=preferred_focus,
                                preferred_governance=preferred_governance,
                                relocation_timeline_months=data.get("relocation_timeline_months"),
                                resources_available=data.get("resources_available", {}),
                                metadata=data.get("metadata", {})
                            )
                            self.relocators[relocator.human_id] = relocator
                    except Exception as e:
                        logger.error(f"Error loading relocator from {file_path}: {e}")
                        
            # Load projects
            projects_dir = os.path.join(self.data_path, "projects")
            for filename in os.listdir(projects_dir):
                if filename.endswith(".json"):
                    file_path = os.path.join(projects_dir, filename)
                    try:
                        with open(file_path, "r") as f:
                            data = json.load(f)
                            project = RelocationProject(
                                project_id=data.get("project_id", filename.replace(".json", "")),
                                name=data.get("name", "Unknown Project"),
                                target_region_id=data.get("target_region_id", ""),
                                status=RelocationProjectStatus[data.get("status", "PROPOSED")],
                                description=data.get("description", ""),
                                community_model_id=data.get("community_model_id"),
                                target_population=data.get("target_population", 0),
                                current_participants=data.get("current_participants", []),
                                project_coordinators=data.get("project_coordinators", []),
                                start_date=data.get("start_date", time.time()),
                                projected_completion_date=data.get("projected_completion_date"),
                                land_status=data.get("land_status", "Seeking"),
                                project_phases=data.get("project_phases", []),
                                community_agreements=data.get("community_agreements", {}),
                                skill_coverage=data.get("skill_coverage", {}),
                                skill_gaps=data.get("skill_gaps", {}),
                                mutual_aid_partnerships=data.get("mutual_aid_partnerships", []),
                                updates=data.get("updates", []),
                                metadata=data.get("metadata", {})
                            )
                            self.projects[project.project_id] = project
                    except Exception as e:
                        logger.error(f"Error loading project from {file_path}: {e}")
                        
            # Load aid offers
            aid_offers_dir = os.path.join(self.data_path, "aid_offers")
            for filename in os.listdir(aid_offers_dir):
                if filename.endswith(".json"):
                    file_path = os.path.join(aid_offers_dir, filename)
                    try:
                        with open(file_path, "r") as f:
                            data = json.load(f)
                            offer = MutualAidOffer(
                                offer_id=data.get("offer_id", filename.replace(".json", "")),
                                source_id=data.get("source_id", ""),
                                target_id=data.get("target_id", ""),
                                offer_type=data.get("offer_type", ""),
                                description=data.get("description", ""),
                                quantity=data.get("quantity"),
                                duration=data.get("duration"),
                                conditions=data.get("conditions", []),
                                status=data.get("status", "offered"),
                                contact_human_id=data.get("contact_human_id"),
                                metadata=data.get("metadata", {})
                            )
                            self.aid_offers[offer.offer_id] = offer
                    except Exception as e:
                        logger.error(f"Error loading aid offer from {file_path}: {e}")
                        
            logger.info(f"Loaded {len(self.relocators)} relocators, {len(self.projects)} projects, and {len(self.aid_offers)} aid offers")
            
        except Exception as e:
            logger.error(f"Error loading relocation data: {e}")
    
    def _save_relocator(self, relocator: HumanRelocator) -> None:
        """Save relocator to disk."""
        try:
            file_path = os.path.join(self.data_path, "relocators", f"{relocator.human_id}.json")
            
            # Format preferences for serialization
            preferred_scale = relocator.preferred_community_scale.name if relocator.preferred_community_scale else None
            preferred_focus = relocator.preferred_community_focus.name if relocator.preferred_community_focus else None
            preferred_governance = relocator.preferred_governance.name if relocator.preferred_governance else None
            
            # Prepare relocator data
            relocator_data = {
                "human_id": relocator.human_id,
                "name": relocator.name,
                "current_region": relocator.current_region,
                "preferred_regions": relocator.preferred_regions,
                "skills": relocator.skills,
                "interests": relocator.interests,
                "constraints": relocator.constraints,
                "household_size": relocator.household_size,
                "has_children": relocator.has_children,
                "preferred_community_scale": preferred_scale,
                "preferred_community_focus": preferred_focus,
                "preferred_governance": preferred_governance,
                "relocation_timeline_months": relocator.relocation_timeline_months,
                "resources_available": relocator.resources_available,
                "metadata": relocator.metadata
            }
            
            with open(file_path, "w") as f:
                json.dump(relocator_data, f, indent=2)
                
        except Exception as e:
            logger.error(f"Error saving relocator: {e}")
    
    def _save_project(self, project: RelocationProject) -> None:
        """Save project to disk."""
        try:
            file_path = os.path.join(self.data_path, "projects", f"{project.project_id}.json")
            
            # Prepare project data
            project_data = {
                "project_id": project.project_id,
                "name": project.name,
                "target_region_id": project.target_region_id,
                "status": project.status.name,
                "description": project.description,
                "community_model_id": project.community_model_id,
                "target_population": project.target_population,
                "current_participants": project.current_participants,
                "project_coordinators": project.project_coordinators,
                "start_date": project.start_date,
                "projected_completion_date": project.projected_completion_date,
                "land_status": project.land_status,
                "project_phases": project.project_phases,
                "community_agreements": project.community_agreements,
                "skill_coverage": project.skill_coverage,
                "skill_gaps": project.skill_gaps,
                "mutual_aid_partnerships": project.mutual_aid_partnerships,
                "updates": project.updates,
                "metadata": project.metadata
            }
            
            with open(file_path, "w") as f:
                json.dump(project_data, f, indent=2)
                
        except Exception as e:
            logger.error(f"Error saving project: {e}")
    
    def _save_aid_offer(self, offer: MutualAidOffer) -> None:
        """Save aid offer to disk."""
        try:
            file_path = os.path.join(self.data_path, "aid_offers", f"{offer.offer_id}.json")
            
            # Prepare offer data
            offer_data = {
                "offer_id": offer.offer_id,
                "source_id": offer.source_id,
                "target_id": offer.target_id,
                "offer_type": offer.offer_type,
                "description": offer.description,
                "quantity": offer.quantity,
                "duration": offer.duration,
                "conditions": offer.conditions,
                "status": offer.status,
                "contact_human_id": offer.contact_human_id,
                "metadata": offer.metadata
            }
            
            with open(file_path, "w") as f:
                json.dump(offer_data, f, indent=2)
                
        except Exception as e:
            logger.error(f"Error saving aid offer: {e}")
    
    def register_relocator(self, relocator: Dict[str, Any]) -> Dict[str, Any]:
        """
        Register a human relocator.
        
        Args:
            relocator: Relocator information
            
        Returns:
            Registration result
        """
        try:
            # Validate required fields
            required_fields = ["name", "current_region"]
            for field in required_fields:
                if field not in relocator:
                    return {
                        "success": False,
                        "error": f"Missing required field: {field}"
                    }
                    
            # Generate ID if not provided
            human_id = relocator.get("human_id")
            if not human_id:
                human_id = f"relocator_{hashlib.md5(f'{relocator['name']}_{time.time()}'.encode()).hexdigest()[:8]}"
                
            # Parse community scale preference if present
            preferred_scale = None
            if "preferred_community_scale" in relocator:
                try:
                    preferred_scale = CommunityScale[relocator["preferred_community_scale"]]
                except KeyError:
                    return {
                        "success": False,
                        "error": f"Invalid community scale: {relocator['preferred_community_scale']}"
                    }
                    
            # Parse community focus preference if present
            preferred_focus = None
            if "preferred_community_focus" in relocator:
                try:
                    preferred_focus = CommunityFocus[relocator["preferred_community_focus"]]
                except KeyError:
                    return {
                        "success": False,
                        "error": f"Invalid community focus: {relocator['preferred_community_focus']}"
                    }
                    
            # Parse governance preference if present
            preferred_governance = None
            if "preferred_governance" in relocator:
                try:
                    preferred_governance = GovernanceModel[relocator["preferred_governance"]]
                except KeyError:
                    return {
                        "success": False,
                        "error": f"Invalid governance model: {relocator['preferred_governance']}"
                    }
                    
            # Create relocator
            new_relocator = HumanRelocator(
                human_id=human_id,
                name=relocator["name"],
                current_region=relocator["current_region"],
                preferred_regions=relocator.get("preferred_regions", []),
                skills=relocator.get("skills", {}),
                interests=relocator.get("interests", []),
                constraints=relocator.get("constraints", []),
                household_size=relocator.get("household_size", 1),
                has_children=relocator.get("has_children", False),
                preferred_community_scale=preferred_scale,
                preferred_community_focus=preferred_focus,
                preferred_governance=preferred_governance,
                relocation_timeline_months=relocator.get("relocation_timeline_months"),
                resources_available=relocator.get("resources_available", {}),
                metadata=relocator.get("metadata", {})
            )
            
            # Add relocator
            self.relocators[human_id] = new_relocator
            
            # Save to disk
            self._save_relocator(new_relocator)
            
            return {
                "success": True,
                "human_id": human_id,
                "message": f"Registered relocator: {new_relocator.name}"
            }
            
        except Exception as e:
            logger.error(f"Error registering relocator: {e}")
            return {
                "success": False,
                "error": f"Registration error: {str(e)}"
            }
    
    def create_relocation_project(self, project: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new relocation project.
        
        Args:
            project: Project information
            
        Returns:
            Creation result
        """
        try:
            # Validate required fields
            required_fields = ["name", "target_region_id", "description"]
            for field in required_fields:
                if field not in project:
                    return {
                        "success": False,
                        "error": f"Missing required field: {field}"
                    }
                    
            # Check region validity
            region = self.mapper.get_region(project["target_region_id"])
            if not region:
                return {
                    "success": False,
                    "error": f"Invalid region ID: {project['target_region_id']}"
                }
                
            # Generate ID if not provided
            project_id = project.get("project_id")
            if not project_id:
                project_id = f"project_{hashlib.md5(f'{project['name']}_{time.time()}'.encode()).hexdigest()[:8]}"
                
            # Parse status
            try:
                status = RelocationProjectStatus[project.get("status", "PROPOSED")]
            except KeyError:
                return {
                    "success": False,
                    "error": f"Invalid project status: {project.get('status')}"
                }
                
            # Create project
            new_project = RelocationProject(
                project_id=project_id,
                name=project["name"],
                target_region_id=project["target_region_id"],
                status=status,
                description=project["description"],
                community_model_id=project.get("community_model_id"),
                target_population=project.get("target_population", 100),
                current_participants=project.get("current_participants", []),
                project_coordinators=project.get("project_coordinators", []),
                start_date=project.get("start_date", time.time()),
                projected_completion_date=project.get("projected_completion_date"),
                land_status=project.get("land_status", "Seeking"),
                project_phases=project.get("project_phases", []),
                community_agreements=project.get("community_agreements", {}),
                skill_coverage=project.get("skill_coverage", {}),
                skill_gaps=project.get("skill_gaps", {}),
                mutual_aid_partnerships=project.get("mutual_aid_partnerships", []),
                updates=[
                    {
                        "timestamp": time.time(),
                        "type": "creation",
                        "content": f"Project created targeting the {region.name} region."
                    }
                ],
                metadata=project.get("metadata", {})
            )
            
            # Add project
            self.projects[project_id] = new_project
            
            # Save to disk
            self._save_project(new_project)
            
            return {
                "success": True,
                "project_id": project_id,
                "message": f"Created relocation project: {new_project.name}"
            }
            
        except Exception as e:
            logger.error(f"Error creating project: {e}")
            return {
                "success": False,
                "error": f"Project creation error: {str(e)}"
            }
    
    def join_project(self, project_id: str, human_id: str, role: str = "participant") -> Dict[str, Any]:
        """
        Join a relocation project.
        
        Args:
            project_id: Project identifier
            human_id: Human identifier
            role: Role in project ("participant", "coordinator")
            
        Returns:
            Join result
        """
        # Check project exists
        if project_id not in self.projects:
            return {
                "success": False,
                "error": "Project not found"
            }
            
        # Check human exists
        if human_id not in self.relocators:
            return {
                "success": False,
                "error": "Relocator not found"
            }
            
        try:
            project = self.projects[project_id]
            relocator = self.relocators[human_id]
            
            # Check if already in project
            if human_id in project.current_participants:
                return {
                    "success": False,
                    "error": f"Human {relocator.name} is already a participant in this project"
                }
                
            # Add to project
            project.current_participants.append(human_id)
            
            # Add as coordinator if requested
            if role == "coordinator" and human_id not in project.project_coordinators:
                project.project_coordinators.append(human_id)
                
            # Update skill coverage
            self._update_project_skill_coverage(project)
            
            # Add update
            project.updates.append({
                "timestamp": time.time(),
                "type": "new_member",
                "content": f"{relocator.name} joined the project as a {role}."
            })
            
            # Save project
            self._save_project(project)
            
            return {
                "success": True,
                "project_id": project_id,
                "human_id": human_id,
                "message": f"{relocator.name} joined project as a {role}"
            }
            
        except Exception as e:
            logger.error(f"Error joining project: {e}")
            return {
                "success": False,
                "error": f"Join error: {str(e)}"
            }
    
    def find_matching_projects(self, human_id: str, max_results: int = 3) -> Dict[str, Any]:
        """
        Find relocation projects matching a human's preferences.
        
        Args:
            human_id: Human identifier
            max_results: Maximum number of results
            
        Returns:
            Matching projects
        """
        # Check human exists
        if human_id not in self.relocators:
            return {
                "success": False,
                "error": "Relocator not found"
            }
            
        try:
            relocator = self.relocators[human_id]
            matches = []
            
            # Match to all active projects
            for project in self.projects.values():
                # Skip if not in active status
                if project.status not in [RelocationProjectStatus.PROPOSED, 
                                         RelocationProjectStatus.PLANNING,
                                         RelocationProjectStatus.RECRUITING]:
                    continue
                    
                # Calculate match score
                score = self._calculate_project_match_score(relocator, project)
                
                # Include match details
                match = {
                    "project_id": project.project_id,
                    "project_name": project.name,
                    "match_score": score,
                    "region_id": project.target_region_id,
                    "region_name": self.mapper.get_region(project.target_region_id).name if self.mapper.get_region(project.target_region_id) else "Unknown",
                    "description": project.description,
                    "target_population": project.target_population,
                    "current_participants": len(project.current_participants),
                    "status": project.status.name,
                    "community_model": None,
                    "skill_gaps": project.skill_gaps
                }
                
                # Add community model details if available
                if project.community_model_id:
                    community = self.designer.get_community(project.community_model_id)
                    if community:
                        match["community_model"] = {
                            "name": community.name,
                            "scale": community.scale.name,
                            "focus": community.focus.name,
                            "governance": community.governance.name
                        }
                        
                matches.append(match)
                
            # Sort by match score
            matches.sort(key=lambda x: x["match_score"], reverse=True)
            
            # Return top matches
            return {
                "success": True,
                "human_id": human_id,
                "human_name": relocator.name,
                "matches": matches[:max_results],
                "total_projects_searched": len(self.projects)
            }
            
        except Exception as e:
            logger.error(f"Error finding matching projects: {e}")
            return {
                "success": False,
                "error": f"Matching error: {str(e)}"
            }
    
    def find_matching_humans(self, project_id: str, max_results: int = 10) -> Dict[str, Any]:
        """
        Find humans matching a project's needs.
        
        Args:
            project_id: Project identifier
            max_results: Maximum number of results
            
        Returns:
            Matching humans
        """
        # Check project exists
        if project_id not in self.projects:
            return {
                "success": False,
                "error": "Project not found"
            }
            
        try:
            project = self.projects[project_id]
            matches = []
            
            # Match to all relocators
            for relocator in self.relocators.values():
                # Skip if already in project
                if relocator.human_id in project.current_participants:
                    continue
                    
                # Calculate match score
                score = self._calculate_project_match_score(relocator, project)
                
                # Calculate skill match
                skill_match = {}
                for skill, gap in project.skill_gaps.items():
                    if gap > 0.3 and skill in relocator.skills:
                        skill_match[skill] = relocator.skills[skill]
                
                # Include match details
                match = {
                    "human_id": relocator.human_id,
                    "name": relocator.name,
                    "match_score": score,
                    "current_region": relocator.current_region,
                    "preferred_regions": relocator.preferred_regions,
                    "household_size": relocator.household_size,
                    "skill_match": skill_match,
                    "relocation_timeline_months": relocator.relocation_timeline_months
                }
                
                matches.append(match)
                
            # Sort by match score
            matches.sort(key=lambda x: x["match_score"], reverse=True)
            
            # Return top matches
            return {
                "success": True,
                "project_id": project_id,
                "project_name": project.name,
                "matches": matches[:max_results],
                "skill_gaps": project.skill_gaps,
                "total_relocators_searched": len(self.relocators)
            }
            
        except Exception as e:
            logger.error(f"Error finding matching humans: {e}")
            return {
                "success": False,
                "error": f"Matching error: {str(e)}"
            }
    
    def update_project_status(self, project_id: str, new_status: str, update_note: str = None) -> Dict[str, Any]:
        """
        Update project status.
        
        Args:
            project_id: Project identifier
            new_status: New status
            update_note: Optional update note
            
        Returns:
            Update result
        """
        # Check project exists
        if project_id not in self.projects:
            return {
                "success": False,
                "error": "Project not found"
            }
            
        try:
            # Parse status
            try:
                status = RelocationProjectStatus[new_status]
            except KeyError:
                return {
                    "success": False,
                    "error": f"Invalid project status: {new_status}"
                }
                
            project = self.projects[project_id]
            
            # Record old status
            old_status = project.status
            
            # Update status
            project.status = status
            
            # Add update
            note = update_note if update_note else f"Status changed from {old_status.name} to {status.name}"
            project.updates.append({
                "timestamp": time.time(),
                "type": "status_change",
                "content": note
            })
            
            # Save project
            self._save_project(project)
            
            return {
                "success": True,
                "project_id": project_id,
                "old_status": old_status.name,
                "new_status": status.name,
                "message": f"Updated project status: {status.name}"
            }
            
        except Exception as e:
            logger.error(f"Error updating project status: {e}")
            return {
                "success": False,
                "error": f"Status update error: {str(e)}"
            }
    
    def create_mutual_aid_offer(self, offer: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a mutual aid offer between communities.
        
        Args:
            offer: Offer information
            
        Returns:
            Creation result
        """
        try:
            # Validate required fields
            required_fields = ["source_id", "target_id", "offer_type", "description"]
            for field in required_fields:
                if field not in offer:
                    return {
                        "success": False,
                        "error": f"Missing required field: {field}"
                    }
                    
            # Generate ID if not provided
            offer_id = offer.get("offer_id")
            if not offer_id:
                offer_id = f"offer_{hashlib.md5(f'{offer['source_id']}_{offer['target_id']}_{time.time()}'.encode()).hexdigest()[:8]}"
                
            # Create offer
            new_offer = MutualAidOffer(
                offer_id=offer_id,
                source_id=offer["source_id"],
                target_id=offer["target_id"],
                offer_type=offer["offer_type"],
                description=offer["description"],
                quantity=offer.get("quantity"),
                duration=offer.get("duration"),
                conditions=offer.get("conditions", []),
                status=offer.get("status", "offered"),
                contact_human_id=offer.get("contact_human_id"),
                metadata=offer.get("metadata", {})
            )
            
            # Add offer
            self.aid_offers[offer_id] = new_offer
            
            # Save to disk
            self._save_aid_offer(new_offer)
            
            # Update project partnerships if both are projects
            if offer["source_id"] in self.projects and offer["target_id"] in self.projects:
                source_project = self.projects[offer["source_id"]]
                target_project = self.projects[offer["target_id"]]
                
                if target_project.project_id not in source_project.mutual_aid_partnerships:
                    source_project.mutual_aid_partnerships.append(target_project.project_id)
                    self._save_project(source_project)
                    
                if source_project.project_id not in target_project.mutual_aid_partnerships:
                    target_project.mutual_aid_partnerships.append(source_project.project_id)
                    self._save_project(target_project)
                
            return {
                "success": True,
                "offer_id": offer_id,
                "message": f"Created mutual aid offer from {offer['source_id']} to {offer['target_id']}"
            }
            
        except Exception as e:
            logger.error(f"Error creating mutual aid offer: {e}")
            return {
                "success": False,
                "error": f"Offer creation error: {str(e)}"
            }
    
    def update_aid_offer_status(self, offer_id: str, new_status: str, note: str = None) -> Dict[str, Any]:
        """
        Update status of a mutual aid offer.
        
        Args:
            offer_id: Offer identifier
            new_status: New status
            note: Optional note
            
        Returns:
            Update result
        """
        # Check offer exists
        if offer_id not in self.aid_offers:
            return {
                "success": False,
                "error": "Offer not found"
            }
            
        try:
            offer = self.aid_offers[offer_id]
            
            # Validate status
            valid_statuses = ["offered", "accepted", "fulfilled", "declined"]
            if new_status not in valid_statuses:
                return {
                    "success": False,
                    "error": f"Invalid status: {new_status}"
                }
                
            # Update status
            old_status = offer.status
            offer.status = new_status
            
            # Add note to metadata if provided
            if note:
                if "status_notes" not in offer.metadata:
                    offer.metadata["status_notes"] = []
                    
                offer.metadata["status_notes"].append({
                    "timestamp": time.time(),
                    "from_status": old_status,
                    "to_status": new_status,
                    "note": note
                })
                
            # Save offer
            self._save_aid_offer(offer)
            
            return {
                "success": True,
                "offer_id": offer_id,
                "old_status": old_status,
                "new_status": new_status,
                "message": f"Updated offer status: {new_status}"
            }
            
        except Exception as e:
            logger.error(f"Error updating offer status: {e}")
            return {
                "success": False,
                "error": f"Status update error: {str(e)}"
            }
    
    def _calculate_project_match_score(self, relocator: HumanRelocator, project: RelocationProject) -> float:
        """
        Calculate match score between relocator and project.
        
        Args:
            relocator: Human relocator
            project: Relocation project
            
        Returns:
            Match score (0.0 to 1.0)
        """
        score_components = []
        
        # Region preference
        region_score = 0.0
        if project.target_region_id in relocator.preferred_regions:
            region_score = 1.0
        elif not relocator.preferred_regions:  # No preferences specified
            region_score = 0.5
        score_components.append(("region", region_score))
        
        # Skill needs
        skill_score = 0.0
        if project.skill_gaps:
            skill_matches = 0
            for skill, gap in project.skill_gaps.items():
                if gap > 0.2 and skill in relocator.skills and relocator.skills[skill] > 0.5:
                    skill_matches += 1
                    
            skill_score = min(1.0, skill_matches / max(1, len(project.skill_gaps.keys()) / 2))
        else:
            skill_score = 0.5  # Neutral if no gaps defined
            
        score_components.append(("skills", skill_score))
        
        # Community model preferences
        community_score = 0.5  # Neutral default
        if project.community_model_id and relocator.preferred_community_scale:
            community = self.designer.get_community(project.community_model_id)
            if community:
                scale_match = relocator.preferred_community_scale == community.scale
                focus_match = relocator.preferred_community_focus == community.focus if relocator.preferred_community_focus else False
                governance_match = relocator.preferred_governance == community.governance if relocator.preferred_governance else False
                
                matches = sum([scale_match, focus_match, governance_match])
                if relocator.preferred_community_focus and relocator.preferred_governance:
                    community_score = matches / 3.0
                elif relocator.preferred_community_focus or relocator.preferred_governance:
                    community_score = matches / 2.0
                else:
                    community_score = matches / 1.0
                    
        score_components.append(("community", community_score))
        
        # Timeline compatibility
        timeline_score = 0.5  # Neutral default
        if relocator.relocation_timeline_months is not None:
            # Calculate approx project timeline
            if project.projected_completion_date:
                project_months = (project.projected_completion_date - time.time()) / (30 * 24 * 3600)
                timeline_diff = abs(relocator.relocation_timeline_months - project_months)
                timeline_score = max(0.0, 1.0 - (timeline_diff / 24))  # Within 24 months
            else:
                timeline_score = 0.5  # Neutral if no project timeline
                
        score_components.append(("timeline", timeline_score))
        
        # Current participants and preferred scale
        scale_score = 0.5  # Neutral default
        if relocator.preferred_community_scale:
            # Determine ideal population ranges for scales
            scale_sizes = {
                CommunityScale.NEIGHBORHOOD: (50, 150),
                CommunityScale.VILLAGE: (150, 500),
                CommunityScale.TOWN: (500, 2000),
                CommunityScale.SMALL_CITY: (2000, 10000),
                CommunityScale.REGIONAL_HUB: (10000, 50000)
            }
            
            ideal_range = scale_sizes.get(relocator.preferred_community_scale, (100, 500))
            if project.target_population >= ideal_range[0] and project.target_population <= ideal_range[1]:
                scale_score = 1.0
            else:
                # Calculate distance from range
                if project.target_population < ideal_range[0]:
                    distance = ideal_range[0] - project.target_population
                    scale_score = max(0.0, 1.0 - (distance / ideal_range[0]))
                else:
                    distance = project.target_population - ideal_range[1]
                    scale_score = max(0.0, 1.0 - (distance / ideal_range[1]))
                    
        score_components.append(("scale", scale_score))
        
        # Calculate weighted score
        weights = {
            "region": 0.3,
            "skills": 0.25,
            "community": 0.2,
            "timeline": 0.15,
            "scale": 0.1
        }
        
        weighted_score = sum(score * weights[name] for name, score in score_components)
        
        return weighted_score
    
    def _update_project_skill_coverage(self, project: RelocationProject) -> None:
        """
        Update skill coverage and gaps for a project.
        
        Args:
            project: Project to update
        """
        # Define standard skill categories to track
        standard_skills = {skill.name.lower(): 0.0 for skill in SkillCategory}
        
        # Initialize coverage
        skill_coverage = standard_skills.copy()
        
        # Calculate coverage from participants
        for human_id in project.current_participants:
            if human_id in self.relocators:
                relocator = self.relocators[human_id]
                
                # Add skills
                for skill, level in relocator.skills.items():
                    skill_lower = skill.lower()
                    if skill_lower in skill_coverage:
                        skill_coverage[skill_lower] = max(skill_coverage[skill_lower], level)
                    else:
                        skill_coverage[skill_lower] = level
                        
        # Calculate gaps
        skill_gaps = {}
        for skill, coverage in skill_coverage.items():
            if coverage < 0.7:  # Less than 70% coverage is a gap
                skill_gaps[skill] = 1.0 - coverage
                
        # Update project
        project.skill_coverage = skill_coverage
        project.skill_gaps = skill_gaps