import boto3
import requests

SLACK_WEBHOOK_URL = "https://hooks.slack.com/services/ADD/YOUR/WEBHOOK"
WARN_THRESHOLD = 80
CRITICAL_THRESHOLD = 65


def get_scores(scores):
    parsed_scores = list()
    for item in scores:
        pack_name = item['ConformancePackName'].replace('-',' ')
        score = int(float(item['Score']))
        if score > WARN_THRESHOLD:
            icon = "white_check_mark"
        if score <= WARN_THRESHOLD:
            icon = "warning"
        if score <= CRITICAL_THRESHOLD:
            icon = "x"
        parsed_scores.append([pack_name, score, icon])
    return parsed_scores


def build_list(parsed_scores):
    list_elements = list()
    for pack in parsed_scores:
        element = {
                    "type": "rich_text_section",
                    "elements": [
                        {
                            "type": "emoji",
                            "name": pack[2]
                        },
                        {
                            "type": "text",
                            "text": f"\t{pack[0]} - {pack[1]}%"
                        }
                    ]
                }
        list_elements.append(element)
    return list_elements


def build_list_section(elements):
    list_section = {
            "type": "rich_text",
            "elements": [
                {
                    "type": "rich_text_section",
                    "elements": [
                        {
                            "type": "text",
                            "text": "Conformance Pack Scores\n\n"
                        }
                    ]
                },
                {
                    "type": "rich_text_list",
                    "style": "bullet",
                    "elements": elements
                }]}
    return list_section


def build_message(list_section):
    message = {"text": "AWS Config Conformance Pack Report", "blocks": []}
    title = {"type": "header", "text": {"type": "plain_text", "text": f"AWS Config Compliance Report"}}
    message["blocks"].append(title)
    thresholds = {"type": "section",
                  "text": {
                      "type": "mrkdwn",
                      "text": f"*WARN* <= {WARN_THRESHOLD}%\n*CRITICAL* <= {CRITICAL_THRESHOLD}%"
                  }}
    message["blocks"].append(thresholds)
    message["blocks"].append({"type": "divider"})
    message["blocks"].append(list_section)
    return message


def handler(event, context):
    client = boto3.client("config")
    response = client.list_conformance_pack_compliance_scores()
    scores = [x for x in response["ConformancePackComplianceScores"]]
    parsed_scores = get_scores(scores)
    score_list = build_list(parsed_scores)
    list_section = build_list_section(score_list)
    message = build_message(list_section)
    requests.post(SLACK_WEBHOOK_URL, json=message)
    return 200
