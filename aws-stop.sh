#!/bin/bash
echo "Stopping MedRAG AWS services..."

# Scale ECS services to zero
echo "Stopping ECS services..."
aws ecs update-service \
  --cluster Medrag-Cluster \
  --service medrag-api-service \
  --desired-count 0 \
  --region us-east-1 > /dev/null

aws ecs update-service \
  --cluster Medrag-Cluster \
  --service medrag-frontend-service \
  --desired-count 0 \
  --region us-east-1 > /dev/null

echo "ECS services scaled to zero."

# Stop RDS
echo "Stopping RDS instance..."
aws rds stop-db-instance \
  --db-instance-identifier medrag-db \
  --region us-east-1 > /dev/null

echo "RDS stop initiated (takes a few minutes to fully stop)."
echo ""
echo "MedRAG is offline. Run ./aws-start.sh to bring it back up."
