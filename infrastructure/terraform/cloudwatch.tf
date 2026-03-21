resource "aws_sns_topic" "alerts" {
  count = var.enable_cloudwatch ? 1 : 0
  name  = "${local.name_prefix}-alerts"

  tags = local.common_tags
}

resource "aws_sns_topic_subscription" "email" {
  count     = var.enable_cloudwatch ? 1 : 0
  topic_arn = aws_sns_topic.alerts[0].arn
  protocol  = "email"
  endpoint  = var.alert_email
}

resource "aws_cloudwatch_dashboard" "langfuse" {
  count          = var.enable_cloudwatch ? 1 : 0
  dashboard_name = "${local.name_prefix}-dashboard"
  dashboard_body = jsonencode({
    widgets = [
      {
        type   = "metric"
        x      = 0
        y      = 0
        width  = 12
        height = 6
        properties = {
          title   = "EC2 CPU Utilization"
          view    = "timeSeries"
          stat    = "Average"
          period  = 300
          region  = var.aws_region
          metrics = [["AWS/EC2", "CPUUtilization", "InstanceId", aws_instance.langfuse.id]]
        }
      },
      {
        type   = "metric"
        x      = 12
        y      = 0
        width  = 12
        height = 6
        properties = {
          title   = "Network In/Out"
          view    = "timeSeries"
          stat    = "Sum"
          period  = 300
          region  = var.aws_region
          metrics = [
            ["AWS/EC2", "NetworkIn", "InstanceId", aws_instance.langfuse.id],
            [".", "NetworkOut", ".", "."],
          ]
        }
      },
      {
        type   = "metric"
        x      = 0
        y      = 6
        width  = 12
        height = 6
        properties = {
          title   = "Disk Used %"
          view    = "timeSeries"
          stat    = "Average"
          period  = 300
          region  = var.aws_region
          metrics = [["CWAgent", "disk_used_percent", "InstanceId", aws_instance.langfuse.id, "path", "/"]]
        }
      },
      {
        type   = "metric"
        x      = 12
        y      = 6
        width  = 12
        height = 6
        properties = {
          title   = "Memory Used %"
          view    = "timeSeries"
          stat    = "Average"
          period  = 300
          region  = var.aws_region
          metrics = [["CWAgent", "mem_used_percent", "InstanceId", aws_instance.langfuse.id]]
        }
      },
    ]
  })
}

resource "aws_cloudwatch_metric_alarm" "cpu_high" {
  count               = var.enable_cloudwatch ? 1 : 0
  alarm_name          = "${local.name_prefix}-cpu-high"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 1
  metric_name         = "CPUUtilization"
  namespace           = "AWS/EC2"
  period              = 300
  statistic           = "Average"
  threshold           = 80
  alarm_description   = "CPU utilization > 80% for 5 minutes"
  dimensions = {
    InstanceId = aws_instance.langfuse.id
  }
  alarm_actions = [aws_sns_topic.alerts[0].arn]
  ok_actions    = [aws_sns_topic.alerts[0].arn]
}

resource "aws_cloudwatch_metric_alarm" "disk_high" {
  count               = var.enable_cloudwatch ? 1 : 0
  alarm_name          = "${local.name_prefix}-disk-high"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 1
  metric_name         = "disk_used_percent"
  namespace           = "CWAgent"
  period              = 300
  statistic           = "Average"
  threshold           = 85
  alarm_description   = "Disk usage > 85%"
  dimensions = {
    InstanceId = aws_instance.langfuse.id
    path       = "/"
  }
  alarm_actions = [aws_sns_topic.alerts[0].arn]
  ok_actions    = [aws_sns_topic.alerts[0].arn]
}