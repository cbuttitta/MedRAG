#!/bin/bash
echo "Starting MedRAG AWS services..."

# Start RDS
echo "Starting RDS instance..."
aws rds start-db-instance \
  --db-instance-identifier medrag-db \
  --region us-east-1

echo "Waiting for RDS to be available (this takes a few minutes)..."
aws rds wait db-instance-available \
  --db-instance-identifier medrag-db \
  --region us-east-1

echo "RDS is up."

# Start ECS services
echo "Starting ECS services..."
aws ecs update-service \
  --cluster Medrag-Cluster \
  --service medrag-api-service \
  --desired-count 1 \
  --region us-east-1 > /dev/null

aws ecs update-service \
  --cluster Medrag-Cluster \
  --service medrag-frontend-service \
  --desired-count 1 \
  --region us-east-1 > /dev/null

echo "Waiting for ECS services to stabilize..."
aws ecs wait services-stable \
  --cluster Medrag-Cluster \
  --services medrag-api-service medrag-frontend-service \
  --region us-east-1

# Print the URL
ALB_DNS=$(aws elbv2 describe-load-balancers \
  --names medrag-alb \
  --query "LoadBalancers[0].DNSName" \
  --output text \
  --region us-east-1)

echo ""
echo "MedRAG is live!"
echo "Frontend:
