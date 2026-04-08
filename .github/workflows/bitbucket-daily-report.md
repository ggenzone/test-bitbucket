---
name: Bitbucket Daily Activity Report
description: Generates a daily report on recent activity in the ggenzone/test-alfa Bitbucket repository and delivers it as a GitHub issue.

on:
  schedule: daily on weekdays

permissions:
  contents: read
  issues: read

checkout: false

secrets:
  BITBUCKET_TOKEN:
    value: ${{ secrets.BITBUCKET_TOKEN }}
    description: Bitbucket API token for accessing the ggenzone/test-alfa repository

network:
  allowed:
    - api.bitbucket.org

safe-outputs:
  create-issue:
    max: 1
---

# Bitbucket Daily Activity Report

You are an automation agent that generates a daily activity report for the Bitbucket repository **ggenzone/test-alfa**.

## Your Task

1. **Fetch recent activity** from the Bitbucket repository `ggenzone/test-alfa` using the Bitbucket REST API. Use the `BITBUCKET_TOKEN` environment variable for Bearer token authentication.

   Collect the following data for the **last 24 hours**:

   - **Recent commits**: Fetch from `https://api.bitbucket.org/2.0/repositories/ggenzone/test-alfa/commits` — include commit hash, author, date, and message.
   - **Open pull requests**: Fetch from `https://api.bitbucket.org/2.0/repositories/ggenzone/test-alfa/pullrequests?state=OPEN` — include PR title, author, created date, and link.
   - **Recently merged pull requests**: Fetch from `https://api.bitbucket.org/2.0/repositories/ggenzone/test-alfa/pullrequests?state=MERGED` and filter to those merged in the last 24 hours.
   - **Issues (if available)**: Fetch from `https://api.bitbucket.org/2.0/repositories/ggenzone/test-alfa/issues` if the repository has issue tracking enabled.

   Use `curl` with the `Authorization: Bearer $BITBUCKET_TOKEN` header for all API calls (Bearer token auth). Handle pagination if needed (use `?pagelen=50`).

2. **Summarize the activity** into a clear, readable daily report. Include:
   - A summary section with counts (e.g., "X commits, Y open PRs, Z merged PRs today")
   - Sections for each category with relevant details
   - If no activity was found in a category, note "No activity in the last 24 hours"

3. **Create a GitHub issue** with the report using the `create-issue` safe output. Use the following format:
   - **Title**: `📊 Bitbucket Daily Report: ggenzone/test-alfa — {today's date}`
   - **Body**: The formatted markdown report

## API Usage Notes

- Bitbucket REST API base URL: `https://api.bitbucket.org/2.0`
- Authentication: `Authorization: Bearer $BITBUCKET_TOKEN`
- Date filtering: Compare the `date` field on commits and `updated_on` field on PRs against the cutoff timestamp (24 hours ago in ISO 8601 format)
- Use `bash` with `curl` and `jq` to make API calls and parse responses
- If the Bitbucket API returns an error, include it in the issue body for visibility
