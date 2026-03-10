import logging

from utils.constants import *
from utils.error import LLMProxyError



AGENT_SERVICE = DEFAULT
AGENT_VENDOR = ANTHROPIC
AGENT_MODEL = 'claude-haiku-4-5'
AGENT_SYSTEM_PROMPT = """<Role>
You are an HTML encoding validator for complex dashboard reports.
</Role>.

<Target>
HTML files with Korean text, emojis, charts, and inline JavaScript/CSS.
</Target>

<Check these CRITICAL points>
1. ✅ Korean text displays correctly (not mojibake like "ì•ˆë…•")
2. ✅ Emojis render properly (📊, 💡, 🔍, etc.)
3. ✅ HTML entities are valid (no &amp;nbsp; or broken &nbs;)
4. ✅ <meta charset="UTF-8"> is present
5. ✅ No encoding errors in JavaScript strings
</Check these CRITICAL points>

<Ignore>
IGNORE these (not in scope):
- CSS syntax errors
- JavaScript logic errors
- Missing external resources
- Chart rendering issues
</Ignore>

<Return ONLY>
- "True" if ALL encoding is correct and safe to import
- "False" if ANY encoding issue exists
</Return ONLY>

<Examples>
Input: <meta charset="UTF-8"><body>안녕하세요 📊</body>
Output: True

Input: <body>ì•ˆë…•í•˜ì„¸ìš"</body>
Output: False

Input: <body>&amp;nbsp;</body>
Output: False
</Examples>

No explanations. Just True or False."""


async def agent_http_validate(args):
    """
    ROLE: http validate
    """
    try:
        llm_proxy_client = getattr(args, "llm_proxy_client", None)
        main_db_client = getattr(args, "main_db_client", None)
        answer = getattr(args, "answer", None)
        service = getattr(args, "service", None)
        session_key = getattr(args, "session_key", None)

        if not all([llm_proxy_client, main_db_client, answer]):
            message = f"session_key: {session_key} | agent_http_validate should use main_db_client, llm_proxy_client, and response"
            logging.error(message)
            raise LLMProxyError(message)

        correct_answer = False
        iteration = 0
        judge = False
        while not correct_answer and iteration < 5:
            logging.info(f"session_key: {session_key}| iteration {iteration}")
            response = await llm_proxy_client.chat(
                service=service or AGENT_SERVICE,
                vendor=AGENT_VENDOR,
                model=AGENT_MODEL,
                system_message=AGENT_SYSTEM_PROMPT,
                human_message=answer,
                session_key=session_key
            )

            judge_str = getattr(response, "text", None)
            if not judge_str:
                err_message = f"session_key: {session_key} | There is not Answer Data"
                logging.error(err_message)
                raise LLMProxyError(err_message)


            if judge_str == "true" or judge_str == "True":
                judge = True
                correct_answer = True
                break
            elif judge_str == "false" or judge_str == "False":
                judge = False
                correct_answer = True
                break
            else:
                logging.info(f"session_key: {session_key} | answer of agent_http_validate is something wrong | answer: {judge_str}")
                iteration += 1
                pass

        logging.info(f"session_key: {session_key} | final_result ======= isAbleImport: {judge}")

    except LLMProxyError as e:
        session_key = getattr(args, "session_key", None)
        logging.error(f"session_key: {session_key} | LLMProxyError: {e.message}")
        raise LLMProxyError(e.message)
    except Exception as e:
        session_key = getattr(args, "session_key", None)
        logging.error(f"session_key: {session_key} | Exception: {e}")
        raise LLMProxyError(f"session_key: {session_key} | Exception: {e}")
