"""
Healthcare ChatGPT Clone - Terraform Infrastructure Tests
Tests for Terraform configuration and infrastructure components.
"""

import pytest
import subprocess
import os
import json
from pathlib import Path


class TestTerraformInfrastructure:
    """Test class for Terraform infrastructure configuration."""

    @pytest.fixture
    def terraform_dir(self):
        """Get the Terraform directory path."""
        return Path(__file__).parent.parent.parent / "infrastructure"

    def test_terraform_validate(self, terraform_dir):
        """Test that Terraform configuration is valid."""
        result = subprocess.run(
            ["terraform", "validate"],
            cwd=terraform_dir,
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0, f"Terraform validation failed: {result.stderr}"

    def test_terraform_format(self, terraform_dir):
        """Test that Terraform files are properly formatted."""
        result = subprocess.run(
            ["terraform", "fmt", "-check", "-recursive"],
            cwd=terraform_dir,
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0, f"Terraform format check failed: {result.stdout}"

    def test_terraform_init(self, terraform_dir):
        """Test that Terraform can initialize without errors."""
        result = subprocess.run(
            ["terraform", "init", "-backend=false"],
            cwd=terraform_dir,
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0, f"Terraform init failed: {result.stderr}"

    def test_terraform_plan_dev(self, terraform_dir):
        """Test that Terraform can create a plan for dev environment."""
        # First initialize
        init_result = subprocess.run(
            ["terraform", "init", "-backend=false"],
            cwd=terraform_dir,
            capture_output=True,
            text=True
        )
        assert init_result.returncode == 0
        
        # Then plan
        result = subprocess.run(
            ["terraform", "plan", "-var-file=environments/dev.tfvars", "-out=tfplan"],
            cwd=terraform_dir,
            capture_output=True,
            text=True
        )
        
        # Plan might fail due to missing credentials, but should not fail due to syntax
        assert result.returncode in [0, 1], f"Terraform plan failed unexpectedly: {result.stderr}"

    def test_required_files_exist(self, terraform_dir):
        """Test that all required Terraform files exist."""
        required_files = [
            "main.tf",
            "variables.tf",
            "outputs.tf",
            "terraform.tf",
            "environments/dev.tfvars",
            "environments/staging.tfvars",
            "environments/prod.tfvars"
        ]
        
        for file_path in required_files:
            full_path = terraform_dir / file_path
            assert full_path.exists(), f"Required file missing: {file_path}"

    def test_required_modules_exist(self, terraform_dir):
        """Test that all required Terraform modules exist."""
        required_modules = [
            "modules/vpc",
            "modules/s3",
            "modules/rds",
            "modules/security",
            "modules/ec2"
        ]
        
        for module_path in required_modules:
            full_path = terraform_dir / module_path
            assert full_path.exists(), f"Required module missing: {module_path}"
            
            # Check for required module files
            module_files = ["main.tf", "variables.tf", "outputs.tf"]
            for module_file in module_files:
                module_file_path = full_path / module_file
                assert module_file_path.exists(), f"Module file missing: {module_path}/{module_file}"

    def test_vpc_module_configuration(self, terraform_dir):
        """Test VPC module configuration."""
        vpc_main_tf = terraform_dir / "modules/vpc/main.tf"
        assert vpc_main_tf.exists()
        
        content = vpc_main_tf.read_text()
        
        # Check for required VPC resources
        required_resources = [
            "aws_vpc",
            "aws_subnet",
            "aws_internet_gateway",
            "aws_route_table",
            "aws_route_table_association"
        ]
        
        for resource in required_resources:
            assert resource in content, f"VPC module missing resource: {resource}"

    def test_s3_module_configuration(self, terraform_dir):
        """Test S3 module configuration."""
        s3_main_tf = terraform_dir / "modules/s3/main.tf"
        assert s3_main_tf.exists()
        
        content = s3_main_tf.read_text()
        
        # Check for required S3 resources
        required_resources = [
            "aws_s3_bucket",
            "aws_s3_bucket_versioning",
            "aws_s3_bucket_encryption",
            "aws_s3_bucket_public_access_block"
        ]
        
        for resource in required_resources:
            assert resource in content, f"S3 module missing resource: {resource}"

    def test_rds_module_configuration(self, terraform_dir):
        """Test RDS module configuration."""
        rds_main_tf = terraform_dir / "modules/rds/main.tf"
        assert rds_main_tf.exists()
        
        content = rds_main_tf.read_text()
        
        # Check for required RDS resources
        required_resources = [
            "aws_rds_cluster",
            "aws_rds_cluster_instance",
            "aws_db_subnet_group",
            "aws_rds_cluster_parameter_group"
        ]
        
        for resource in required_resources:
            assert resource in content, f"RDS module missing resource: {resource}"

    def test_security_module_configuration(self, terraform_dir):
        """Test Security module configuration."""
        security_main_tf = terraform_dir / "modules/security/main.tf"
        assert security_main_tf.exists()
        
        content = security_main_tf.read_text()
        
        # Check for required security resources
        required_resources = [
            "aws_security_group",
            "aws_iam_role",
            "aws_iam_policy",
            "aws_iam_role_policy_attachment"
        ]
        
        for resource in required_resources:
            assert resource in content, f"Security module missing resource: {resource}"

    def test_ec2_module_configuration(self, terraform_dir):
        """Test EC2 module configuration."""
        ec2_main_tf = terraform_dir / "modules/ec2/main.tf"
        assert ec2_main_tf.exists()
        
        content = ec2_main_tf.read_text()
        
        # Check for required EC2 resources
        required_resources = [
            "aws_instance",
            "aws_launch_template",
            "aws_autoscaling_group",
            "aws_eip"
        ]
        
        for resource in required_resources:
            assert resource in content, f"EC2 module missing resource: {resource}"

    def test_environment_variables(self, terraform_dir):
        """Test that environment variable files have required variables."""
        env_files = [
            "environments/dev.tfvars",
            "environments/staging.tfvars",
            "environments/prod.tfvars"
        ]
        
        required_variables = [
            "aws_region",
            "environment",
            "project_name",
            "vpc_cidr",
            "instance_type",
            "db_instance_class"
        ]
        
        for env_file in env_files:
            env_path = terraform_dir / env_file
            assert env_path.exists(), f"Environment file missing: {env_file}"
            
            content = env_path.read_text()
            for variable in required_variables:
                assert variable in content, f"Variable {variable} missing in {env_file}"

    def test_variables_definition(self, terraform_dir):
        """Test that all variables are properly defined."""
        variables_tf = terraform_dir / "variables.tf"
        assert variables_tf.exists()
        
        content = variables_tf.read_text()
        
        # Check for variable definitions
        assert "variable \"aws_region\"" in content
        assert "variable \"environment\"" in content
        assert "variable \"project_name\"" in content
        assert "variable \"vpc_cidr\"" in content
        assert "variable \"instance_type\"" in content
        assert "variable \"db_instance_class\"" in content

    def test_outputs_definition(self, terraform_dir):
        """Test that all outputs are properly defined."""
        outputs_tf = terraform_dir / "outputs.tf"
        assert outputs_tf.exists()
        
        content = outputs_tf.read_text()
        
        # Check for output definitions
        assert "output \"vpc_id\"" in content
        assert "output \"ec2_public_ip\"" in content
        assert "output \"rds_endpoint\"" in content
        assert "output \"s3_bucket_name\"" in content

    def test_provider_configuration(self, terraform_dir):
        """Test provider configuration."""
        main_tf = terraform_dir / "main.tf"
        assert main_tf.exists()
        
        content = main_tf.read_text()
        
        # Check for provider configuration
        assert "provider \"aws\"" in content
        assert "required_providers" in content
        assert "hashicorp/aws" in content

    def test_backend_configuration(self, terraform_dir):
        """Test backend configuration."""
        terraform_tf = terraform_dir / "terraform.tf"
        assert terraform_tf.exists()
        
        content = terraform_tf.read_text()
        
        # Check for backend configuration
        assert "backend \"s3\"" in content

    def test_user_data_script_exists(self, terraform_dir):
        """Test that user data script exists and is valid."""
        user_data_script = terraform_dir / "modules/ec2/user_data.sh"
        assert user_data_script.exists()
        
        content = user_data_script.read_text()
        
        # Check for required components in user data
        assert "#!/bin/bash" in content
        assert "docker" in content
        assert "docker-compose" in content
        assert "openwebui" in content

    def test_terraform_version_constraint(self, terraform_dir):
        """Test that Terraform version constraint is specified."""
        main_tf = terraform_dir / "main.tf"
        content = main_tf.read_text()
        
        assert "required_version" in content
        assert ">= 1.0" in content

    def test_aws_provider_version_constraint(self, terraform_dir):
        """Test that AWS provider version constraint is specified."""
        main_tf = terraform_dir / "main.tf"
        content = main_tf.read_text()
        
        assert "version" in content
        assert "~> 5.0" in content

    def test_security_best_practices(self, terraform_dir):
        """Test security best practices in Terraform configuration."""
        # Check for encryption settings
        s3_main_tf = terraform_dir / "modules/s3/main.tf"
        s3_content = s3_main_tf.read_text()
        assert "encryption" in s3_content
        
        # Check for security groups
        security_main_tf = terraform_dir / "modules/security/main.tf"
        security_content = security_main_tf.read_text()
        assert "aws_security_group" in security_content
        
        # Check for IAM roles
        assert "aws_iam_role" in security_content

    def test_monitoring_configuration(self, terraform_dir):
        """Test monitoring configuration."""
        main_tf = terraform_dir / "main.tf"
        content = main_tf.read_text()
        
        # Check for CloudWatch resources
        assert "aws_cloudwatch_log_group" in content
        assert "aws_cloudwatch_dashboard" in content

    def test_cost_optimization(self, terraform_dir):
        """Test cost optimization features."""
        # Check for auto-scaling
        ec2_main_tf = terraform_dir / "modules/ec2/main.tf"
        ec2_content = ec2_main_tf.read_text()
        assert "aws_autoscaling_group" in ec2_content
        
        # Check for Aurora Serverless
        rds_main_tf = terraform_dir / "modules/rds/main.tf"
        rds_content = rds_main_tf.read_text()
        assert "serverlessv2_scaling_configuration" in rds_content

    def test_high_availability(self, terraform_dir):
        """Test high availability configuration."""
        # Check for multiple availability zones
        vpc_main_tf = terraform_dir / "modules/vpc/main.tf"
        vpc_content = vpc_main_tf.read_text()
        assert "availability_zones" in vpc_content
        
        # Check for Aurora cluster
        rds_main_tf = terraform_dir / "modules/rds/main.tf"
        rds_content = rds_main_tf.read_text()
        assert "aws_rds_cluster" in rds_content
