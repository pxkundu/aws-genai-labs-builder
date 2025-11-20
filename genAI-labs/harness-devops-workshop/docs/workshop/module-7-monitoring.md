# Module 7: Monitoring and Optimization

## Overview

In this final module, you'll set up comprehensive monitoring, analytics, and optimization strategies for your Harness pipelines and deployed applications.

**Duration**: 60 minutes  
**Difficulty**: Intermediate

## Learning Objectives

By the end of this module, you will:
- Set up Harness Analytics
- Configure CloudWatch dashboards
- Implement log aggregation
- Set up performance monitoring
- Optimize costs
- Create troubleshooting runbooks

## Prerequisites

- Completed Modules 1-6
- Application deployed
- CloudWatch access
- Monitoring tools knowledge

## Step 1: Harness Analytics

### 1.1 Enable Analytics

1. Navigate to **"Analytics"** in Harness
2. Review pipeline metrics:
   - Execution times
   - Success rates
   - Failure reasons
   - Resource usage

### 1.2 Create Custom Dashboards

1. Create dashboard for CI/CD metrics
2. Add widgets for:
   - Pipeline execution trends
   - Deployment frequency
   - Mean time to recovery
   - Success rates

## Step 2: CloudWatch Integration

### 2.1 Create CloudWatch Dashboard

1. In AWS Console, create dashboard
2. Add widgets for:
   - ECS service metrics
   - ALB metrics
   - Application logs
   - Custom metrics

### 2.2 Set up Alarms

1. Create alarms for:
   - High error rates
   - Low success rates
   - Resource utilization
   - Cost thresholds

## Step 3: Log Aggregation

### 3.1 Configure Log Groups

1. Verify CloudWatch log groups exist
2. Set retention policies
3. Configure log streaming

### 3.2 Set up Log Insights

1. Create log insights queries
2. Save queries for common issues
3. Set up alerts on log patterns

## Step 4: Performance Monitoring

### 4.1 Application Performance

1. Monitor response times
2. Track error rates
3. Monitor resource usage
4. Set up APM if needed

### 4.2 Pipeline Performance

1. Track pipeline execution times
2. Identify bottlenecks
3. Optimize slow steps
4. Parallelize where possible

## Step 5: Cost Optimization

### 5.1 Review Costs

1. Analyze CloudWatch billing
2. Review ECS costs
3. Identify optimization opportunities

### 5.2 Implement Optimizations

1. Right-size ECS tasks
2. Use spot instances where possible
3. Implement auto-scaling
4. Clean up unused resources

## Step 6: Troubleshooting

### 6.1 Create Runbooks

1. Document common issues
2. Create troubleshooting guides
3. Document rollback procedures

### 6.2 Set up Alerts

1. Configure alerting channels
2. Set up on-call rotation
3. Test alert delivery

## Next Steps

Congratulations! You've completed the entire Harness DevOps Workshop! 🎉

You now have:
- ✅ Complete CI/CD pipeline
- ✅ Automated deployments
- ✅ Monitoring and alerting
- ✅ Cost optimization
- ✅ Best practices implemented

Continue learning with:
- Harness certification programs
- Advanced Harness features
- Community forums
- Additional workshops

