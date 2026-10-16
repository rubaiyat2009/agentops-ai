from google import genai

client = genai.Client()

response = client.models.generate_content(
    model="gemini-3.5-flash-lite",
    contents="""
    You are a Kubernetes Kueue operations expert.

    Analyze this incident:

    - 120 workloads pending
    - CPU quota 96/96 used
    - Admission check reports insufficient CPU quota
    - One worker failed with OOMKilled

    Identify:
    1. Probable root causes
    2. Supporting evidence
    3. Scheduling versus execution failures
    4. Safe remediation recommendations

    Do not invent missing telemetry.
    """
)

print(response.text)