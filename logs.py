# # This sends the actual logs to slack and not an alert
import urllib3
import json
import os
import boto3

def lambda_handler(event, context):
    slack_url = os.environ['WEBHOOK_URL']
    client = boto3.client('logs')
    headers = {
        'Content-Type': "application/json"
    }
    message = json.loads(event["Records"][0]["Sns"]["Message"])

    response = client.describe_metric_filters(
        metricName = message['Trigger']['MetricName'],
        metricNamespace = message['Trigger']['Namespace']
    )

    metricFilter = response['metricFilters'][0]
    timestamp = message['StateChangeTime'].split(".")[0]
    timestamp = datetime.datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S").timestamp()*1000
    offset = message['Trigger']['Period'] * (message['Trigger']['EvaluationPeriods'] +5)* 1000 #+5 is to get 5 minutes more of past log data

    response = client.filter_log_events(
        logGroupName=metricFilter['logGroupName'],
        startTime=int(timestamp - offset),
        endTime=int(timestamp),
        filterPattern = metricFilter['filterPattern'] if metricFilter['filterPattern'] else "",
        interleaved=True
    )
    log_events = response['events']
    
    blocks = [
        {
    			"type": "header",
    			"text": {
    				"type": "plain_text",
    				"text": f"{message['AlarmName']}"
    			}
		    },
        {
			    "type": "divider"
		    }
    ]
    
    for event in log_events:
          try:
              message = json.loads(event['message'])
              indented_message = json.dumps(message, indent=4)
          except ValueError:
              indented_message = event['message']
          log = {
              "type": "section",
              "text": {
                  "type": "mrkdwn",
                  "text": event['logStreamName'] + "\n\n" + indented_message
              }
          }
          blocks.append(log)

          blocks.append({
                  "type": "divider"
              })
    body = {
        "blocks": blocks
    }
    
    encoded_msg = json.dumps(body, ensure_ascii=True, default=set_default)
    resp = http.request('POST', url, body=encoded_msg, headers=headers)