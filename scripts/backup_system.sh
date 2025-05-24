#!/bin/bash
# backup_system.sh
# Production-ready backup system for OpenSourceControlledEnvironments
# Includes automated backups, verification, and recovery procedures

set -euo pipefail  # Exit on error, undefined variables, pipe failures

# Configuration
BACKUP_BASE_DIR="/home/pi/backups"
DATA_DIR="/home/pi/farm/data"
CONFIG_DIR="/home/pi/farm/config"
SYSTEM_CONFIG_DIR="/etc/farm"
LOG_DIR="/var/log/farm"
BACKUP_LOG="/var/log/farm/backup.log"
RETENTION_DAYS=30
REMOTE_BACKUP_HOST=""  # Set to enable remote backups
REMOTE_BACKUP_DIR=""
REMOTE_BACKUP_USER=""
HEALTHCHECK_URL=""  # Optional: webhook for monitoring

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Ensure script is run with appropriate permissions
if [[ $EUID -ne 0 ]] && [[ ! -w "$BACKUP_BASE_DIR" ]]; then
   echo -e "${RED}This script must be run as root or with write permissions to $BACKUP_BASE_DIR${NC}" 
   exit 1
fi

# Create necessary directories
mkdir -p "$BACKUP_BASE_DIR"/{daily,weekly,monthly,temp}
mkdir -p "$(dirname "$BACKUP_LOG")"

# Logging function
log() {
    local level=$1
    shift
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [$level] $*" | tee -a "$BACKUP_LOG"
}

# Error handling
error_exit() {
    log "ERROR" "$1"
    send_notification "ERROR" "$1"
    exit 1
}

# Send notification (implement based on your notification system)
send_notification() {
    local level=$1
    local message=$2
    
    # If healthcheck URL is configured, send notification
    if [[ -n "$HEALTHCHECK_URL" ]]; then
        curl -s -X POST "$HEALTHCHECK_URL" \
            -H "Content-Type: application/json" \
            -d "{\"level\":\"$level\",\"message\":\"$message\",\"timestamp\":\"$(date -u +%Y-%m-%dT%H:%M:%SZ)\"}" \
            > /dev/null 2>&1 || true
    fi
}

# Check available disk space
check_disk_space() {
    local required_space_mb=$1
    local available_space_mb=$(df -m "$BACKUP_BASE_DIR" | awk 'NR==2 {print $4}')
    
    if [[ $available_space_mb -lt $required_space_mb ]]; then
        error_exit "Insufficient disk space. Required: ${required_space_mb}MB, Available: ${available_space_mb}MB"
    fi
    
    log "INFO" "Disk space check passed. Available: ${available_space_mb}MB"
}

# Calculate size of directories to backup
calculate_backup_size() {
    local total_size=0
    
    for dir in "$DATA_DIR" "$CONFIG_DIR" "$SYSTEM_CONFIG_DIR"; do
        if [[ -d "$dir" ]]; then
            size=$(du -sm "$dir" 2>/dev/null | cut -f1)
            total_size=$((total_size + size))
        fi
    done
    
    # Add 20% overhead for compression variation
    echo $((total_size * 120 / 100))
}

# Stop services before backup (to ensure data consistency)
stop_services() {
    log "INFO" "Stopping farm services..."
    
    # Stop services gracefully
    if systemctl is-active --quiet farm-controller; then
        systemctl stop farm-controller || log "WARNING" "Failed to stop farm-controller"
    fi
    
    if systemctl is-active --quiet farm-api; then
        systemctl stop farm-api || log "WARNING" "Failed to stop farm-api"
    fi
    
    # Wait for services to fully stop
    sleep 5
}

# Start services after backup
start_services() {
    log "INFO" "Starting farm services..."
    
    systemctl start farm-controller || log "ERROR" "Failed to start farm-controller"
    systemctl start farm-api || log "ERROR" "Failed to start farm-api"
    
    # Verify services are running
    sleep 5
    
    if ! systemctl is-active --quiet farm-controller; then
        error_exit "farm-controller failed to start after backup"
    fi
    
    if ! systemctl is-active --quiet farm-api; then
        error_exit "farm-api failed to start after backup"
    fi
}

# Create backup
create_backup() {
    local backup_type=$1  # daily, weekly, or monthly
    local timestamp=$(date +%Y%m%d_%H%M%S)
    local backup_name="farm_backup_${backup_type}_${timestamp}"
    local backup_file="$BACKUP_BASE_DIR/temp/${backup_name}.tar.gz"
    local backup_manifest="$BACKUP_BASE_DIR/temp/${backup_name}.manifest"
    
    log "INFO" "Starting $backup_type backup: $backup_name"
    
    # Create manifest file
    cat > "$backup_manifest" <<EOF
Backup Name: $backup_name
Backup Type: $backup_type
Date: $(date)
Hostname: $(hostname)
System Version: $(cat /home/pi/farm/VERSION 2>/dev/null || echo "unknown")
EOF
    
    # Create tar archive with progress
    log "INFO" "Creating archive..."
    
    tar_files=""
    [[ -d "$DATA_DIR" ]] && tar_files="$tar_files $DATA_DIR"
    [[ -d "$CONFIG_DIR" ]] && tar_files="$tar_files $CONFIG_DIR"
    [[ -d "$SYSTEM_CONFIG_DIR" ]] && tar_files="$tar_files $SYSTEM_CONFIG_DIR"
    
    if [[ -z "$tar_files" ]]; then
        error_exit "No directories found to backup"
    fi
    
    # Create tar with progress indicator
    tar -czf "$backup_file" \
        --exclude='*.log' \
        --exclude='*.tmp' \
        --exclude='__pycache__' \
        --exclude='.git' \
        $tar_files \
        "$backup_manifest" 2>&1 | \
        while read line; do
            echo -ne "."
        done
    
    echo ""  # New line after progress dots
    
    # Verify backup integrity
    log "INFO" "Verifying backup integrity..."
    if ! tar -tzf "$backup_file" > /dev/null 2>&1; then
        rm -f "$backup_file" "$backup_manifest"
        error_exit "Backup verification failed - archive is corrupted"
    fi
    
    # Calculate checksums
    local checksum=$(sha256sum "$backup_file" | cut -d' ' -f1)
    echo "SHA256: $checksum" >> "$backup_manifest"
    
    # Move to appropriate directory
    local final_dir="$BACKUP_BASE_DIR/$backup_type"
    mv "$backup_file" "$final_dir/"
    mv "$backup_manifest" "$final_dir/"
    
    log "INFO" "Backup completed successfully: ${final_dir}/${backup_name}.tar.gz"
    log "INFO" "Backup size: $(du -h "${final_dir}/${backup_name}.tar.gz" | cut -f1)"
    log "INFO" "Checksum: $checksum"
    
    echo "${final_dir}/${backup_name}.tar.gz"
}

# Upload backup to remote location
upload_remote_backup() {
    local backup_file=$1
    
    if [[ -z "$REMOTE_BACKUP_HOST" ]] || [[ -z "$REMOTE_BACKUP_DIR" ]]; then
        log "INFO" "Remote backup not configured, skipping"
        return 0
    fi
    
    log "INFO" "Uploading backup to remote server..."
    
    # Use rsync for efficient transfer with resume capability
    if rsync -avz --progress \
        -e "ssh -o StrictHostKeyChecking=no -o ConnectTimeout=30" \
        "$backup_file" \
        "${REMOTE_BACKUP_USER}@${REMOTE_BACKUP_HOST}:${REMOTE_BACKUP_DIR}/" 2>&1 | tee -a "$BACKUP_LOG"; then
        log "INFO" "Remote backup upload completed successfully"
    else
        log "ERROR" "Remote backup upload failed"
        return 1
    fi
}

# Cleanup old backups
cleanup_old_backups() {
    local backup_type=$1
    local retention_count=$2
    
    log "INFO" "Cleaning up old $backup_type backups (keeping last $retention_count)"
    
    # List backups sorted by date, keep newest N
    ls -t "$BACKUP_BASE_DIR/$backup_type"/farm_backup_*.tar.gz 2>/dev/null | \
        tail -n +$((retention_count + 1)) | \
        while read -r old_backup; do
            log "INFO" "Removing old backup: $(basename "$old_backup")"
            rm -f "$old_backup" "${old_backup%.tar.gz}.manifest"
        done
}

# Restore from backup
restore_backup() {
    local backup_file=$1
    local restore_dir=${2:-"/"}
    
    if [[ ! -f "$backup_file" ]]; then
        error_exit "Backup file not found: $backup_file"
    fi
    
    log "INFO" "Starting restore from: $backup_file"
    
    # Verify backup integrity first
    log "INFO" "Verifying backup integrity..."
    if ! tar -tzf "$backup_file" > /dev/null 2>&1; then
        error_exit "Backup verification failed - archive is corrupted"
    fi
    
    # Stop services
    stop_services
    
    # Create restore point
    local restore_point="$BACKUP_BASE_DIR/restore_points/before_restore_$(date +%Y%m%d_%H%M%S)"
    mkdir -p "$restore_point"
    
    # Backup current state
    log "INFO" "Creating restore point..."
    for dir in "$DATA_DIR" "$CONFIG_DIR" "$SYSTEM_CONFIG_DIR"; do
        if [[ -d "$dir" ]]; then
            cp -a "$dir" "$restore_point/" || log "WARNING" "Failed to backup $dir"
        fi
    done
    
    # Extract backup
    log "INFO" "Extracting backup..."
    tar -xzf "$backup_file" -C "$restore_dir" || {
        log "ERROR" "Restore failed, attempting to recover from restore point"
        # Attempt to recover from restore point
        cp -a "$restore_point"/* / 2>/dev/null || true
        start_services
        error_exit "Restore failed"
    }
    
    # Set proper permissions
    chown -R pi:pi "$DATA_DIR" "$CONFIG_DIR" 2>/dev/null || true
    
    # Start services
    start_services
    
    log "INFO" "Restore completed successfully"
    send_notification "INFO" "System restored from backup: $(basename "$backup_file")"
}

# List available backups
list_backups() {
    echo -e "${GREEN}Available Backups:${NC}"
    echo ""
    
    for backup_type in daily weekly monthly; do
        echo -e "${YELLOW}${backup_type^} Backups:${NC}"
        ls -lh "$BACKUP_BASE_DIR/$backup_type"/farm_backup_*.tar.gz 2>/dev/null | \
            awk '{print "  " $9 " (" $5 ")"}' || echo "  No backups found"
        echo ""
    done
}

# Test backup system
test_backup_system() {
    log "INFO" "Running backup system test..."
    
    # Check directories exist
    for dir in "$DATA_DIR" "$CONFIG_DIR"; do
        if [[ ! -d "$dir" ]]; then
            log "WARNING" "Directory not found: $dir"
        fi
    done
    
    # Check disk space
    check_disk_space 100
    
    # Test service control
    log "INFO" "Testing service control..."
    if systemctl is-active --quiet farm-controller; then
        log "INFO" "farm-controller is running"
    else
        log "WARNING" "farm-controller is not running"
    fi
    
    # Test remote backup if configured
    if [[ -n "$REMOTE_BACKUP_HOST" ]]; then
        log "INFO" "Testing remote backup connection..."
        if ssh -o ConnectTimeout=10 "${REMOTE_BACKUP_USER}@${REMOTE_BACKUP_HOST}" "echo 'Connection successful'" 2>/dev/null; then
            log "INFO" "Remote backup connection successful"
        else
            log "ERROR" "Remote backup connection failed"
        fi
    fi
    
    log "INFO" "Backup system test completed"
}

# Main backup routine
main_backup() {
    local backup_type=${1:-daily}
    
    log "INFO" "=== Starting $backup_type backup routine ==="
    
    # Check disk space (require at least 2x the backup size)
    local required_space=$(calculate_backup_size)
    required_space=$((required_space * 2))
    check_disk_space $required_space
    
    # Stop services for consistency
    stop_services
    
    # Create backup
    local backup_file
    backup_file=$(create_backup "$backup_type")
    
    # Start services immediately
    start_services
    
    # Upload to remote if configured
    upload_remote_backup "$backup_file"
    
    # Cleanup old backups based on type
    case $backup_type in
        daily)
            cleanup_old_backups "daily" 7    # Keep 7 daily backups
            ;;
        weekly)
            cleanup_old_backups "weekly" 4   # Keep 4 weekly backups
            ;;
        monthly)
            cleanup_old_backups "monthly" 12  # Keep 12 monthly backups
            ;;
    esac
    
    log "INFO" "=== Backup routine completed successfully ==="
    send_notification "INFO" "$backup_type backup completed successfully"
}

# Parse command line arguments
case "${1:-}" in
    daily|weekly|monthly)
        main_backup "$1"
        ;;
    restore)
        if [[ -z "${2:-}" ]]; then
            echo "Usage: $0 restore <backup_file> [restore_directory]"
            exit 1
        fi
        restore_backup "$2" "${3:-/}"
        ;;
    list)
        list_backups
        ;;
    test)
        test_backup_system
        ;;
    *)
        echo "OpenSource Controlled Environments Backup System"
        echo ""
        echo "Usage: $0 {daily|weekly|monthly|restore|list|test}"
        echo ""
        echo "Commands:"
        echo "  daily    - Run daily backup"
        echo "  weekly   - Run weekly backup"
        echo "  monthly  - Run monthly backup"
        echo "  restore  - Restore from backup"
        echo "  list     - List available backups"
        echo "  test     - Test backup system configuration"
        echo ""
        echo "Examples:"
        echo "  $0 daily"
        echo "  $0 restore /home/pi/backups/daily/farm_backup_daily_20240101_120000.tar.gz"
        echo ""
        echo "Schedule with cron:"
        echo "  0 2 * * * $0 daily    # Daily at 2 AM"
        echo "  0 3 * * 0 $0 weekly   # Weekly on Sunday at 3 AM"
        echo "  0 4 1 * * $0 monthly  # Monthly on 1st at 4 AM"
        exit 1
        ;;
esac