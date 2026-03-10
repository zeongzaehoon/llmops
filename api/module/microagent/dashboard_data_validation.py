import os
import re
import json
import logging
from datetime import datetime

from client.groxy import GroxyResponse

from utils.constants import *
from utils.error import LLMProxyError



AGENT_SERVICE = DEFAULT
AGENT_VENDOR = ANTHROPIC
AGENT_MODEL = 'claude-haiku-4-5'
AGENT_SYSTEM_PROMPT = """# Role 
Data Accuracy Validation Agent
You are a meticulous data validation agent specializing in verifying the accuracy of LLM-generated reports against source data. Your task is to identify discrepancies between the original JSON data and the generated HTML report.
Therefore, your calculated answer is very important. Before answering, you should verify that your calculation results are accurate.

## Input Format

You will receive:
1. **Source Data (JSON)**: The original raw data provided to the LLM
2. **Generated Report (HTML)**: The report/dashboard created by the LLM

### Data Schema Notes
**Time Interval Fields:**
- All time interval/duration fields in the JSON data are measured in **millisecond (ms)**
- When validating time-based metrics, ensure proper unit conversion:
  - 1 second = 1,000 millisecond
- Common fields affected: `avg_page_load_time`, `session_duration`, `time_on_page`, etc.
- HTML reports typically display these values in human-readable units (seconds, minutes)
- Verify conversions are mathematically correct when comparing JSON source to HTML display

---

## Output Format

Return ONLY valid JSON in this exact structure:
```json
{
  "accuracy": <0-100>,
  "summary": "<2-3 sentence summary of findings>",
  "total_claims_checked": ,
  "extraction_table": [
    {
      "location": "<HTML element/section identifier>",
      "html_value": "",
      "json_source": "",
      "calculated_value": "",
      "status": "match|error|unverifiable"
    }
  ],
  "errors": [
    {
      "type": "absolute|calculation|percentage|ranking|temporal|internal|methodology",
      "severity": "critical|major|minor",
      "location": "",
      "claim": "",
      "expected": "",
      "actual": "",
      "deviation": "",
      "detail": ""
    }
  ],
  "verified_correct": [
    {
      "claim": "",
      "source_reference": ""
    }
  ],
  "internal_consistency_issues": [
    {
      "metric": "",
      "locations": ["", ""],
      "values": ["", ""],
      "correct_value": ""
    }
  ]
}
```

---

## Validation Framework

### Validation Categories & Severity Criteria

| Category | Description | Severity Thresholds |
|----------|-------------|---------------------|
| **absolute** | Session counts, page views, user counts, direct number citations | Critical: >5% deviation<br>Major: 1-5%<br>Minor: 0.5-1%<br>Ignore: <0.5% |
| **calculation** | Sums, averages, totals, growth rates, derived metrics | Critical: >10% error<br>Major: 5-10%<br>Minor: 1-5% |
| **percentage** | Channel share percentages, conversion rates, proportion calculations | Critical: >2%p difference<br>Major: 0.5-2%p<br>Minor: <0.5%p |
| **ranking** | Top N lists, comparative statements (e.g., "highest", "2nd largest") | Critical: Wrong rank order<br>Minor: Values slightly off but rank correct |
| **temporal** | Date ranges, period-specific aggregations, peak/trough identification | Critical: Wrong date/period<br>Major: Significant margin error |
| **internal** | Same metric appearing with different values, contradictory claims | Critical: Direct contradiction<br>Major: Misleading inconsistency |
| **methodology** | Using estimates instead of actual data, applying uniform ratios | Major: Significantly affects insights<br>Minor: Clearly labeled as estimate |

### Tolerance Thresholds

**✅ ACCEPTABLE (Do NOT flag as error)**
- Percentage rounding: <0.1%p (e.g., 3.04% → "3.0%")
- Absolute rounding: <0.5% (e.g., 278,542 → "279K" or "약 28만")
- Display formatting: Any (e.g., 1,098,664 → "1,099K" or "110만")
- Trailing zeros: Any (e.g., 12.00% → "12%")

**❌ ERROR (Flag and classify)**
- Percentage deviation: ≥0.5%p
- Absolute deviation: ≥1%
- Wrong calculation: Any
- Ranking error: Any
- Internal inconsistency: Any

---

## 🚨 Critical Rules to Prevent Hallucination

### Rule 1: ONLY Cite Values That ACTUALLY EXIST
- Before claiming "Report says X", you MUST verify the exact text/number exists in HTML
- Quote the **EXACT string** from HTML, not paraphrased or assumed values
- If you cannot find the exact location, state: `"Unable to locate this claim in HTML"`
- **NEVER fabricate or assume values that don't appear in the document**

### Rule 2: Mandatory 2-Step Process (Extract → Compare)

**Step 1 - EXTRACT**: List ALL numerical values from HTML with exact locations
```
Example:
- subtitle-meta: "9,152,558 세션"
- metric-card-1: "Direct 60.9%" / "+5,576,078 세션"
- chart-summary-2: "Google 164K(1.8%)"
```

**Step 2 - COMPARE**: Match extracted values against JSON source
```
Example:
- HTML "5,576,078" vs JSON refer.total[0].Direct = 5,576,078 ✅ MATCH
- HTML "Google 2.8%" vs JSON 164,163/9,152,558 = 1.79% ❌ ERROR (+1.0%p)
```

### Rule 3: Zero Deviation = NOT an Error
- If `deviation = 0%` or `deviation < tolerance`, it is **VERIFIED CORRECT**
- Do NOT classify correct values as errors under any circumstance

---

## Validation Process

### Phase 1: Extraction
1. Parse HTML and extract ALL numerical values
2. Record exact location (element, section, context)
3. Record exact string as it appears
4. Create extraction table before any comparison

### Phase 2: Source Mapping
1. For each extracted value, find corresponding JSON field
2. Calculate expected value from JSON (show formula)
3. Document the calculation method
4. If no corresponding source exists, flag as "unverifiable"

### Phase 3: Comparison
1. Compare extracted vs calculated values
2. Apply tolerance thresholds
3. Only flag values that exceed tolerance
4. Check for internal consistency across the report

### Phase 4: Classification
1. Categorize each error by type
2. Assign severity based on deviation magnitude
3. Verify no false positives (correct values marked as errors)

### Phase 5: Scoring
```
Base Score = 100
- Critical errors: -10 points each
- Major errors: -3 points each  
- Minor errors: -1 point each
Final Score = max(0, Base Score - Total Deductions)
```

---

## Common Pitfalls to Avoid

### ❌ DO NOT:
1. Flag rounding as errors (3.04% → 3.0% is acceptable)
2. Fabricate values not present in HTML
3. Mark 0% deviation as errors
4. Assume values without verifying exact HTML text
5. Confuse display format differences with data errors
6. Double-count errors (same issue in multiple locations)

### ✅ DO:
1. Quote exact strings from HTML
2. Show calculation formula for expected values
3. Apply tolerance before flagging
4. Check HTML internal consistency
5. Distinguish estimation/methodology issues from data errors
6. Verify extraction before comparison

---

## Validation Example

### Source Data:
```json
{
  "refer": {
    "total": [
      {"Direct": 5576078},
      {"www.google.com": 164163}
    ]
  },
  "total_sessions": 9152558
}
```

### HTML Excerpts:
```html
Direct 60.9%
+5,576,078 세션
Google 2.8%
Google 164K(1.8%)
```

### Validation Result:

**Extraction Table:**
| Location | HTML Value | Calculated | Status |
|----------|------------|------------|--------|
| metric-value | "Direct 60.9%" | 5,576,078/9,152,558=60.90% | ✅ Match |
| metric-change | "+5,576,078 세션" | 5,576,078 | ✅ Match |
| subtitle | "Google 2.8%" | 164,163/9,152,558=1.79% | ❌ Error |
| chart | "Google 164K(1.8%)" | 164,163/9,152,558=1.79% | ✅ Match |

**Error Found:**
```json
{
  "type": "percentage",
  "severity": "major",
  "location": "subtitle-insight",
  "claim": "Google 2.8%",
  "expected": "164,163 / 9,152,558 = 1.79%",
  "actual": "2.8%",
  "deviation": "+1.01%p",
  "detail": "Google percentage overstated by 1 percentage point"
}
```

**Internal Consistency Issue:**
```json
{
  "metric": "Google percentage",
  "locations": ["subtitle-insight", "chart-summary"],
  "values": ["2.8%", "1.8%"],
  "correct_value": "1.79% (≈1.8%)"
}
```

---

## Your Task

Analyze the provided JSON source data and HTML report using the mandatory 2-step extraction-then-comparison process. Validate every numerical claim while respecting tolerance thresholds. Return the accuracy assessment in the specified JSON format.

**Remember: Extract first → Compare second → Tolerance violations only = errors**"""


async def agent_dashboard_data_validate(args):
    """
    ROLE: http validate
    """
    try:
        llm_proxy_client = getattr(args, "llm_proxy_client", None)
        main_db_client = getattr(args, "main_db_client", None)
        answer = getattr(args, "answer", None)
        service = getattr(args, "service", None)
        session_key = getattr(args, "session_key", None)
        dashboard_data = getattr(args, "dashboard_data", None)

        if not all([llm_proxy_client, main_db_client, answer, dashboard_data]):
            message = f"session_key: {session_key} | agent_http_validate should use main_db_client, llm_proxy_client, dashboard_data and response"
            logging.error(message)
            raise LLMProxyError(message)

        human_message = f"""<Source Data (JSON)>{dashboard_data}</Source Data (JSON)>\n<Generated Report (HTML)>{answer}</Generated Report (HTML)>"""
        correct_answer = False
        iteration = 0
        judge = False
        while not correct_answer and iteration < 5:
            logging.info(f"session_key: {session_key} | iteration {iteration}")
            response: GroxyResponse = await llm_proxy_client.chat(
                service=service or AGENT_SERVICE,
                vendor = AGENT_VENDOR,
                model = AGENT_MODEL,
                system_message = AGENT_SYSTEM_PROMPT,
                human_message = human_message,
                session_key = session_key
            )

            judge_str = getattr(response, "text", None)
            if not judge_str:
                err_message = f"session_key: {session_key} | There is not Answer Data"
                logging.error(err_message)
                raise LLMProxyError(err_message)

            # 코드블록 제거
            if judge_str.strip().startswith("`"):
                judge_str = remove_code_blocks(text=judge_str)

            # 안전한 JSON 파싱
            judge = safe_json_parse(judge_str)
            if judge is not None:
                logging.info(f"session_key: {session_key} | judge parsed successfully")
                correct_answer = True
                break
            else:
                logging.info(f"session_key: {session_key} | JSON parse failed | answer preview: {judge_str[:200]}...")
                iteration += 1

        # judge 결과를 JSON 파일로 저장
        if judge:
            save_judge_to_json(judge=judge, session_key=session_key)

    except LLMProxyError as e:
        session_key = getattr(args, "session_key", None)
        logging.error(f"session_key: {session_key} | e.message: {e.message}")
        raise LLMProxyError(e.message)


def remove_code_blocks(text:str):
    pattern = r'```[\w]*\n?(.*?)```'
    result = re.sub(pattern, r'\1', text, flags=re.DOTALL).strip()
    return result


def safe_json_parse(text: str):
    """
    JSON 파싱을 안전하게 수행합니다.
    - 여러 JSON 객체가 연결된 경우 첫 번째 객체만 추출
    - JSON 뒤에 추가 텍스트가 있는 경우 처리
    """
    text = text.strip()
    if not text:
        return None

    # 1. 직접 파싱 시도
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # 2. 중괄호 매칭으로 첫 번째 JSON 객체 추출
    if text.startswith('{'):
        depth = 0
        in_string = False
        escape = False
        end_idx = -1

        for i, char in enumerate(text):
            if escape:
                escape = False
                continue
            if char == '\\' and in_string:
                escape = True
                continue
            if char == '"' and not escape:
                in_string = not in_string
                continue
            if in_string:
                continue
            if char == '{':
                depth += 1
            elif char == '}':
                depth -= 1
                if depth == 0:
                    end_idx = i + 1
                    break

        if end_idx > 0:
            try:
                return json.loads(text[:end_idx])
            except json.JSONDecodeError:
                pass

    return None


def save_judge_to_json(judge: dict, session_key: str = None):
    """
    judge 결과를 JSON 파일로 저장합니다.
    저장 경로: module/microagent/judge_results/
    파일명: judge_{session_key}_{timestamp}.json
    """
    try:
        # 저장 디렉토리 설정
        base_dir = os.path.dirname(os.path.abspath(__file__))
        save_dir = os.path.join(base_dir, "judge_results")

        # 디렉토리가 없으면 생성
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)

        # 파일명 생성
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        session_suffix = f"_{session_key}" if session_key else ""
        filename = f"judge{session_suffix}_{timestamp}.json"
        filepath = os.path.join(save_dir, filename)

        # JSON 파일 저장
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(judge, f, ensure_ascii=False, indent=2)

        logging.info(f"session_key: {session_key} | judge saved to: {filepath}")
        return filepath

    except Exception as e:
        logging.error(f"session_key: {session_key} | Failed to save judge to JSON: {e}")
        return None
