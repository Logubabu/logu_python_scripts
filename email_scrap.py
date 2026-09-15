import imaplib
import email
import re
import os
import html
from email.header import decode_header
from email.utils import parsedate_to_datetime
from urllib.parse import urlparse, parse_qsl, urlencode, urlunparse

import pandas as pd
from bs4 import BeautifulSoup


# ============================================================
# CONFIGURATION
# ============================================================

EMAIL_ADDRESS = "your_email@gmail.com"
EMAIL_PASSWORD = "your_app_password"

# Gmail
IMAP_SERVER = "imap.gmail.com"
IMAP_PORT = 993

# For Outlook use:
# IMAP_SERVER = "outlook.office365.com"
# IMAP_PORT = 993

OUTPUT_DIR = "output"
EXCEL_FILE = os.path.join(OUTPUT_DIR, "jobs.xlsx")
CSV_FILE = os.path.join(OUTPUT_DIR, "jobs.csv")


# ============================================================
# JOB KEYWORDS
# ============================================================

JOB_KEYWORDS = [
    "job",
    "jobs",
    "career",
    "careers",
    "vacancy",
    "vacancies",
    "hiring",
    "job opening",
    "job openings",
    "recruitment",
    "recruiter",
    "employment",
    "software engineer",
    "software developer",
    "python developer",
    "backend developer",
    "frontend developer",
    "full stack developer",
    "full-stack developer",
    "data engineer",
    "data scientist",
    "devops engineer",
    "technical lead",
    "web developer",
    "application developer",
    "programmer",
    "engineer",
]


# ============================================================
# JOB SOURCES
# ============================================================

JOB_SOURCES = {
    "indeed.com": "Indeed",
    "linkedin.com": "LinkedIn",
    "naukri.com": "Naukri",
    "foundit.in": "Foundit",
    "monster.com": "Monster",
    "glassdoor.com": "Glassdoor",
    "instahyre.com": "Instahyre",
    "wellfound.com": "Wellfound",
    "hirist.tech": "Hirist",
    "cutshort.io": "Cutshort",
    "shine.com": "Shine",
    "timesjobs.com": "TimesJobs",
}


# ============================================================
# CONNECT TO EMAIL
# ============================================================

def connect_email():

    print("Connecting to email...")

    mail = imaplib.IMAP4_SSL(
        IMAP_SERVER,
        IMAP_PORT
    )

    try:

        mail.login(
            EMAIL_ADDRESS,
            EMAIL_PASSWORD
        )

        print("Login successful.")

        return mail

    except imaplib.IMAP4.error as error:

        print("Login failed.")
        print(error)

        raise


# ============================================================
# DECODE EMAIL HEADER
# ============================================================

def decode_text(value):

    if not value:
        return ""

    decoded_parts = decode_header(value)

    result = ""

    for part, encoding in decoded_parts:

        if isinstance(part, bytes):

            try:

                result += part.decode(
                    encoding or "utf-8",
                    errors="ignore"
                )

            except Exception:

                result += part.decode(
                    "utf-8",
                    errors="ignore"
                )

        else:

            result += part

    return result


# ============================================================
# HTML TO TEXT
# ============================================================

def html_to_text(html_content):

    if not html_content:
        return ""

    soup = BeautifulSoup(
        html_content,
        "html.parser"
    )

    for tag in soup(
        ["script", "style", "noscript"]
    ):
        tag.decompose()

    return soup.get_text(
        separator=" ",
        strip=True
    )


# ============================================================
# EXTRACT EMAIL BODY
# ============================================================

def extract_body(message):

    plain_text = []
    html_text = []

    if message.is_multipart():

        for part in message.walk():

            content_type = part.get_content_type()

            disposition = str(
                part.get("Content-Disposition")
            )

            if "attachment" in disposition.lower():
                continue

            payload = part.get_payload(
                decode=True
            )

            if not payload:
                continue

            charset = (
                part.get_content_charset()
                or "utf-8"
            )

            try:

                content = payload.decode(
                    charset,
                    errors="ignore"
                )

            except Exception:

                content = payload.decode(
                    "utf-8",
                    errors="ignore"
                )

            if content_type == "text/plain":
                plain_text.append(content)

            elif content_type == "text/html":
                html_text.append(content)

    else:

        payload = message.get_payload(
            decode=True
        )

        if payload:

            charset = (
                message.get_content_charset()
                or "utf-8"
            )

            content = payload.decode(
                charset,
                errors="ignore"
            )

            if message.get_content_type() == "text/html":

                html_text.append(content)

            else:

                plain_text.append(content)

    text = "\n".join(plain_text)

    html_body = "\n".join(html_text)

    if html_body:

        text += "\n" + html_to_text(
            html_body
        )

    return text, html_body


# ============================================================
# EXTRACT URLS
# ============================================================

def extract_urls(text):

    if not text:
        return []

    pattern = (
        r'https?://[^\s<>"\'\]\)]+'
    )

    urls = re.findall(
        pattern,
        text,
        re.IGNORECASE
    )

    cleaned = []

    for url in urls:

        url = html.unescape(url)

        url = url.rstrip(
            ".,;:!?)]}>"
        )

        if url not in cleaned:
            cleaned.append(url)

    return cleaned


# ============================================================
# NORMALIZE URL
# ============================================================

def normalize_url(url):

    try:

        parsed = urlparse(url)

        tracking_parameters = {
            "utm_source",
            "utm_medium",
            "utm_campaign",
            "utm_term",
            "utm_content",
            "trk",
            "ref",
            "referrer",
            "source",
        }

        query = []

        for key, value in parse_qsl(
            parsed.query
        ):

            if key.lower() not in tracking_parameters:
                query.append(
                    (key, value)
                )

        parsed = parsed._replace(
            query=urlencode(query),
            fragment=""
        )

        return urlunparse(parsed).rstrip("/")

    except Exception:

        return url


# ============================================================
# JOB EMAIL DETECTION
# ============================================================

def is_job_email(
    subject,
    sender,
    body
):

    content = (
        subject
        + " "
        + sender
        + " "
        + body
    ).lower()

    score = 0

    for keyword in JOB_KEYWORDS:

        if keyword in content:
            score += 1

    # At least two job signals
    return score >= 2


# ============================================================
# DETECT SOURCE
# ============================================================

def detect_source(
    urls,
    sender,
    body
):

    content = (
        " ".join(urls)
        + " "
        + sender
        + " "
        + body
    ).lower()

    for domain, source in JOB_SOURCES.items():

        if domain in content:
            return source

    return "Other"


# ============================================================
# EXTRACT COMPANY
# ============================================================

def extract_company(
    subject,
    sender,
    body
):

    combined = (
        subject
        + "\n"
        + body
    )

    patterns = [

        r"(?:at|with|from)\s+"
        r"([A-Z][A-Za-z0-9&.,' -]{2,80})",

        r"([A-Z][A-Za-z0-9&.,' -]{2,80})"
        r"\s+is hiring",

        r"([A-Z][A-Za-z0-9&.,' -]{2,80})"
        r"\s+is looking",

        r"company\s*[:\-]\s*"
        r"([A-Za-z0-9&.,' -]{2,80})",

        r"employer\s*[:\-]\s*"
        r"([A-Za-z0-9&.,' -]{2,80})",
    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            combined,
            re.IGNORECASE
        )

        if match:

            company = match.group(1).strip()

            company = re.sub(
                r"\s+",
                " ",
                company
            )

            return company[:100]

    # Fallback to sender domain

    match = re.search(
        r"@([A-Za-z0-9.-]+)",
        sender
    )

    if match:

        domain = match.group(1)

        company = domain.split(".")[0]

        return company.title()

    return ""


# ============================================================
# EXTRACT JOB TITLE
# ============================================================

def extract_job_title(
    subject,
    body
):

    combined = (
        subject
        + "\n"
        + body
    )

    patterns = [

        r"job title\s*[:\-]\s*"
        r"([^\n|]+)",

        r"position\s*[:\-]\s*"
        r"([^\n|]+)",

        r"role\s*[:\-]\s*"
        r"([^\n|]+)",

        r"hiring\s+for\s+"
        r"([^\n|]+)",
    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            combined,
            re.IGNORECASE
        )

        if match:

            title = match.group(1).strip()

            return re.sub(
                r"\s+",
                " ",
                title
            )[:150]

    # Common job titles

    job_titles = [
        "software engineer",
        "software developer",
        "python developer",
        "backend developer",
        "frontend developer",
        "full stack developer",
        "full-stack developer",
        "data engineer",
        "data scientist",
        "devops engineer",
        "technical lead",
        "engineering manager",
        "web developer",
        "application developer",
        "machine learning engineer",
    ]

    for title in job_titles:

        if re.search(
            r"\b"
            + re.escape(title)
            + r"\b",
            combined,
            re.IGNORECASE
        ):
            return title.title()

    # Fallback

    result = re.sub(
        r"(?i)"
        r"(job alert|job opening|new job|hiring|career)",
        "",
        subject
    )

    return result.strip(
        " :-|"
    )[:150]


# ============================================================
# EXPERIENCE
# ============================================================

def extract_experience(body):

    patterns = [

        r"experience\s*[:\-]?\s*"
        r"(\d+\s*[-–]\s*\d+\s*(?:years?|yrs?))",

        r"(\d+\s*[-–]\s*\d+\s*"
        r"(?:years?|yrs?))",

        r"(\d+\s*\+\s*"
        r"(?:years?|yrs?))",

        r"experience\s*[:\-]?\s*"
        r"(\d+\+?\s*(?:years?|yrs?))",
    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            body,
            re.IGNORECASE
        )

        if match:

            return match.group(1).strip()

    return ""


# ============================================================
# SALARY
# ============================================================

def extract_salary(body):

    patterns = [

        r"(₹?\s*\d+(?:\.\d+)?\s*"
        r"(?:LPA|Lakh|Lakhs)"
        r"\s*[-–]\s*"
        r"₹?\s*\d+(?:\.\d+)?\s*"
        r"(?:LPA|Lakh|Lakhs))",

        r"(\d+(?:\.\d+)?\s*"
        r"[-–]\s*\d+(?:\.\d+)?\s*"
        r"(?:LPA|Lakh|Lakhs))",

        r"(₹?\s*\d+(?:\.\d+)?\s*"
        r"(?:LPA|Lakh|Lakhs))",

        r"salary\s*[:\-]?\s*"
        r"([^\n|]+)",

        r"ctc\s*[:\-]?\s*"
        r"([^\n|]+)",

        r"package\s*[:\-]?\s*"
        r"([^\n|]+)",
    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            body,
            re.IGNORECASE
        )

        if match:

            return re.sub(
                r"\s+",
                " ",
                match.group(1).strip()
            )[:100]

    return ""


# ============================================================
# APPLY LINK
# ============================================================

def find_apply_link(
    urls
):

    preferred_domains = [
        "indeed.com",
        "linkedin.com",
        "naukri.com",
        "foundit.in",
        "glassdoor.com",
        "instahyre.com",
        "wellfound.com",
        "hirist.tech",
        "cutshort.io",
        "shine.com",
        "timesjobs.com",
    ]

    # First preference:
    # known job websites

    for url in urls:

        lower = url.lower()

        for domain in preferred_domains:

            if domain in lower:

                return normalize_url(url)

    # Second preference:
    # job/career/apply links

    for url in urls:

        lower = url.lower()

        if any(
            x in lower
            for x in [
                "/apply",
                "/job/",
                "/jobs/",
                "/career/",
                "/careers/",
                "jobid="
            ]
        ):

            return normalize_url(url)

    # Last URL

    if urls:
        return normalize_url(
            urls[0]
        )

    return ""


# ============================================================
# DATE
# ============================================================

def get_email_date(date_string):

    try:

        date = parsedate_to_datetime(
            date_string
        )

        return date.strftime(
            "%d-%m-%Y"
        )

    except Exception:

        return ""


# ============================================================
# NORMALIZE TEXT
# ============================================================

def normalize_text(value):

    if not value:
        return ""

    value = value.lower().strip()

    value = re.sub(
        r"[^a-z0-9]+",
        " ",
        value
    )

    return re.sub(
        r"\s+",
        " ",
        value
    ).strip()


# ============================================================
# DUPLICATE KEY
# ============================================================

def duplicate_key(job):

    company = normalize_text(
        job["company_name"]
    )

    title = normalize_text(
        job["job_title"]
    )

    link = normalize_url(
        job["apply_link"]
    ).lower()

    # Apply URL is the strongest identifier.

    if link:
        return "URL:" + link

    # Otherwise company + title.

    return (
        "JOB:"
        + company
        + ":"
        + title
    )


# ============================================================
# PROCESS EMAIL
# ============================================================

def process_email(raw_email):

    message = email.message_from_bytes(
        raw_email
    )

    subject = decode_text(
        message.get("Subject", "")
    )

    sender = decode_text(
        message.get("From", "")
    )

    date = get_email_date(
        message.get("Date", "")
    )

    body, html_body = extract_body(
        message
    )

    if not is_job_email(
        subject,
        sender,
        body
    ):
        return None

    urls = extract_urls(
        html_body
        + "\n"
        + body
    )

    source = detect_source(
        urls,
        sender,
        body
    )

    job = {

        "company_name":
            extract_company(
                subject,
                sender,
                body
            ),

        "job_title":
            extract_job_title(
                subject,
                body
            ),

        "date":
            date,

        "experience":
            extract_experience(
                body
            ),

        "salary_range":
            extract_salary(
                body
            ),

        "apply_link":
            find_apply_link(
                urls
            ),

        "source":
            source,
    }

    return job


# ============================================================
# REMOVE DUPLICATES
# ============================================================

def remove_duplicates(jobs):

    unique = {}

    for job in jobs:

        key = duplicate_key(
            job
        )

        if key not in unique:

            unique[key] = job

        else:

            existing = unique[key]

            # Fill missing fields
            # from duplicate emails.

            for field in [
                "company_name",
                "job_title",
                "date",
                "experience",
                "salary_range",
                "apply_link",
                "source",
            ]:

                if (
                    not existing[field]
                    and job[field]
                ):

                    existing[field] = (
                        job[field]
                    )

    return list(
        unique.values()
    )


# ============================================================
# EXPORT
# ============================================================

def export_jobs(jobs):

    os.makedirs(
        OUTPUT_DIR,
        exist_ok=True
    )

    columns = [
        "company_name",
        "job_title",
        "date",
        "experience",
        "salary_range",
        "apply_link",
        "source",
    ]

    df = pd.DataFrame(
        jobs,
        columns=columns
    )

    if not df.empty:

        df = df.drop_duplicates()

    df.to_excel(
        EXCEL_FILE,
        index=False
    )

    df.to_csv(
        CSV_FILE,
        index=False,
        encoding="utf-8-sig"
    )

    print("\n================================")
    print("JOB EXTRACTION COMPLETED")
    print("================================")

    print(
        f"Total unique jobs: {len(df)}"
    )

    print(
        f"Excel file: {EXCEL_FILE}"
    )

    print(
        f"CSV file:   {CSV_FILE}"
    )


# ============================================================
# MAIN
# ============================================================

def main():

    print(
        "\n================================"
    )

    print(
        "EMAIL JOB EXTRACTOR"
    )

    print(
        "================================\n"
    )

    mail = connect_email()

    # Select all mail instead of only inbox.
    status, _ = mail.select(
        '"[Gmail]/All Mail"'
    )

    if status != "OK":

        # Fallback for other providers

        status, _ = mail.select(
            "INBOX"
        )

    print(
        "Reading emails..."
    )

    status, data = mail.search(
        None,
        "ALL"
    )

    if status != "OK":

        print(
            "Unable to read emails."
        )

        mail.logout()

        return

    email_ids = data[0].split()

    print(
        f"Total emails found: "
        f"{len(email_ids)}"
    )

    jobs = []

    for index, email_id in enumerate(
        email_ids,
        start=1
    ):

        try:

            status, message_data = (
                mail.fetch(
                    email_id,
                    "(RFC822)"
                )
            )

            if status != "OK":
                continue

            for response in message_data:

                if not isinstance(
                    response,
                    tuple
                ):
                    continue

                raw_email = response[1]

                job = process_email(
                    raw_email
                )

                if job:

                    jobs.append(job)

                    print(
                        f"[{len(jobs)}] "
                        f"{job['company_name']} | "
                        f"{job['job_title']}"
                    )

        except Exception as error:

            print(
                f"Error processing email "
                f"{index}: {error}"
            )

    print(
        f"\nJob emails found: {len(jobs)}"
    )

    jobs = remove_duplicates(
        jobs
    )

    print(
        f"Unique jobs: {len(jobs)}"
    )

    export_jobs(
        jobs
    )

    mail.logout()


if __name__ == "__main__":
    main()