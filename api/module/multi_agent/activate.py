import asyncio
import logging
import json
from collections import defaultdict, deque

from module.multi_agent.dto import MultiAgentArgs, AgentNode, EdgeNode
from module.llm.helper import get_prompt_from_mongo, get_vendor_and_model
from utils.constants import *



class RunMultiAgent:
    """
    멀티 에이전트 오케스트레이터\n
    ---\n
    graphType에 따라 에이전트들을 연결하고 실행\n
    - linear: A → B → C 순차 실행, 이전 에이전트 결과가 다음 에이전트의 컨텍스트\n
    - debate: 에이전트들이 라운드별로 토론, 마지막에 종합\n
    - parallel: 전 에이전트 병렬 실행 후 마지막 에이전트가 종합\n
    - router: 첫 번째 에이전트가 질문 분석 → 적합한 에이전트 선택\n
    - custom: edge 기반 DAG 실행, 조건 평가 → 통과/재시도/분기\n
    """

    def __init__(self, args: dict):
        self.args = args
        self.ma_args: MultiAgentArgs = None


    async def activate(self):
        try:
            await self._init_args()
            await self._load_agents()

            runners = {
                GRAPH_TYPE_LINEAR: self._run_linear,
                GRAPH_TYPE_DEBATE: self._run_debate,
                GRAPH_TYPE_PARALLEL: self._run_parallel,
                GRAPH_TYPE_ROUTER: self._run_router,
                GRAPH_TYPE_CUSTOM: self._run_custom,
            }
            runner = runners.get(self.ma_args.graph_type)
            if runner:
                async for chunk in runner():
                    yield chunk
            else:
                yield json.dumps({"type": "error", "content": f"지원하지 않는 그래프 타입: {self.ma_args.graph_type}"})

        except Exception as e:
            logging.error(f"[module.multi_agent.activate] 🔴 Exception: {e}")
            yield json.dumps({"type": "error", "content": "멀티 에이전트 실행 중 오류가 발생했습니다."})


    async def _init_args(self):
        """dict args → MultiAgentArgs 변환"""
        self.ma_args = MultiAgentArgs(
            server_stage=self.args.get("server_stage"),
            session_key=self.args.get("session_key"),
            question=self.args.get("question"),
            graph_id=self.args.get("graph_id"),
            graph_type=self.args.get("graph_type"),
            max_iterations=self.args.get("max_iterations", 3),
            streaming=self.args.get("streaming", True),
            llm_proxy_client=self.args.get("llm_proxy_client"),
            main_db_client=self.args.get("main_db_client"),
            memory_db_client=self.args.get("memory_db_client"),
            message_client=self.args.get("message_client"),
            lang=self.args.get("lang"),
        )

        # # agents 정보 변환 (원본)
        # for agent_info in self.args.get("agents", []):
        #     self.ma_args.agents.append(AgentNode(
        #         agent=agent_info["agent"],
        #         role=agent_info.get("role", ""),
        #     ))
        self.ma_args.agents = [
            AgentNode(agent=info["agent"], role=info.get("role", ""))
            for info in self.args.get("agents", [])
        ]

        # # edges 정보 변환 (원본)
        # for edge_info in self.args.get("edges", []):
        #     self.ma_args.edges.append(EdgeNode(
        #         source=edge_info["from"],
        #         target=edge_info["to"],
        #         condition=edge_info.get("condition"),
        #         on_failure=edge_info.get("onFailure", "end"),
        #         max_retries=edge_info.get("maxRetries", 2),
        #     ))
        self.ma_args.edges = [
            EdgeNode(
                source=info["from"], target=info["to"],
                condition=info.get("condition"),
                on_failure=info.get("onFailure", "end"),
                max_retries=info.get("maxRetries", 2),
            )
            for info in self.args.get("edges", [])
        ]


    async def _load_agents(self):
        """각 에이전트의 프롬프트, 모델 정보를 DB에서 로드"""
        # tasks = []
        # for node in self.ma_args.agents:
        #     tasks.append(self._load_agent_config(node))
        # await asyncio.gather(*tasks)
        await asyncio.gather(*(self._load_agent_config(node) for node in self.ma_args.agents))


    async def _load_agent_config(self, node: AgentNode):
        """개별 에이전트 설정 로드 (프롬프트, 모델)"""
        try:
            # 프롬프트 로드
            result = await get_prompt_from_mongo(
                self.ma_args.main_db_client,
                agent=node.agent
            )
            node.system_message = result[1] if result else None
        except Exception as e:
            logging.warning(f"[multi_agent._load_agent_config] 프롬프트 로드 실패 agent={node.agent}: {e}")
            node.system_message = None

        try:
            # 모델 로드
            vendor, model = await get_vendor_and_model(
                self.ma_args.main_db_client,
                node.agent
            )
            node.vendor, node.model = vendor, model
        except Exception:
            node.vendor = BASE_VENDOR
            node.model = BASE_MODEL


    async def _stream_agent(self, node: AgentNode, human_message: str, context: str = None):
        """개별 에이전트 LLM 호출 → GroxyStreamingResponse async generator 반환"""
        system_message = node.system_message or ""
        if node.role:
            system_message = f"당신의 역할: {node.role}\n\n{system_message}"
        if context:
            system_message += f"\n\n[이전 에이전트 결과]\n{context}"

        async for response_obj in self.ma_args.llm_proxy_client.stream(
            service="solomon",
            vendor=node.vendor,
            model=node.model,
            system_message=system_message,
            human_message=human_message,
            session_key=self.ma_args.session_key,
        ):
            yield response_obj


    async def _run_linear(self):
        """
        선형 실행: A → B → C
        이전 에이전트의 결과가 다음 에이전트의 컨텍스트로 전달
        """
        context = None

        for step, node in enumerate(self.ma_args.agents):
            step_num = step + 1
            meta = {"agent": node.agent, "step": step_num}

            yield json.dumps({
                "type": "agent_start",
                "agent": node.agent,
                "role": node.role,
                "step": step_num,
                "totalSteps": len(self.ma_args.agents)
            }) + "\n"

            # LLM 스트리밍 호출 & 응답 수집
            answer = ""
            async for response_obj in self._stream_agent(node, self.ma_args.question, context):
                text = response_obj.text or ""
                if text:
                    answer += text
                    yield json.dumps({**meta, "type": "content", "content": text}) + "\n"

            context = answer

            yield json.dumps({"type": "agent_end", **meta}) + "\n"

        yield json.dumps({"type": "done"}) + "\n"


    async def _run_debate(self):
        """
        토론형 실행: 에이전트들이 라운드별로 응답, 마지막 에이전트가 종합
        - 라운드 1: 각 에이전트가 질문에 독립 응답
        - 라운드 2~N: 이전 라운드 전체 응답을 보고 각자 재응답
        - 마지막 라운드 마지막 에이전트: 모더레이터로 전체 종합
        """
        # all_responses = {}  # (원본)
        all_responses = defaultdict(list)

        for round_num in range(1, self.ma_args.max_iterations + 1):
            is_last_round = (round_num == self.ma_args.max_iterations)

            yield json.dumps({
                "type": "round_start",
                "round": round_num,
                "totalRounds": self.ma_args.max_iterations
            }) + "\n"

            for node in self.ma_args.agents:
                is_moderator = is_last_round and node == self.ma_args.agents[-1]

                context = self._build_debate_context(
                    all_responses, round_num, node.agent, is_moderator
                )

                yield json.dumps({
                    "type": "agent_start",
                    "agent": node.agent,
                    "role": "모더레이터 (종합)" if is_moderator else node.role,
                    "round": round_num,
                    "isModerator": is_moderator
                }) + "\n"

                human_message = self.ma_args.question
                if is_moderator:
                    human_message = (
                        f"다음은 '{self.ma_args.question}'에 대한 토론 내용입니다. "
                        f"모든 의견을 종합하여 최종 결론을 내려주세요."
                    )

                meta = {"agent": node.agent, "round": round_num, "isModerator": is_moderator}

                answer = ""
                async for response_obj in self._stream_agent(node, human_message, context):
                    text = response_obj.text or ""
                    if text:
                        answer += text
                        yield json.dumps({**meta, "type": "content", "content": text}) + "\n"

                # if node.agent not in all_responses:  # (원본 - defaultdict로 불필요)
                #     all_responses[node.agent] = []
                all_responses[node.agent].append(answer)

                yield json.dumps({
                    "type": "agent_end",
                    "agent": node.agent,
                    "round": round_num
                }) + "\n"

            yield json.dumps({"type": "round_end", "round": round_num}) + "\n"

        yield json.dumps({"type": "done"}) + "\n"


    async def _run_parallel(self):
        """
        병렬 실행: 모든 에이전트가 동시에 처리 후 마지막 에이전트가 종합
        - Phase 1: 모든 에이전트 병렬 실행 (asyncio.gather)
        - Phase 2: 마지막 에이전트가 전체 결과를 종합
        """
        node_map = {node.agent: node for node in self.ma_args.agents}

        # Phase 1: 병렬 실행
        yield json.dumps({
            "type": "phase_start",
            "phase": "parallel",
            "totalAgents": len(self.ma_args.agents)
        }) + "\n"

        async def run_single(node):
            answer = ""
            async for response_obj in self._stream_agent(node, self.ma_args.question):
                text = response_obj.text or ""
                if text:
                    answer += text
            return node.agent, answer

        results = await asyncio.gather(*(run_single(node) for node in self.ma_args.agents))

        # 각 에이전트 결과 전달
        # agent_results = {}  # (원본)
        # for agent_name, answer in results:
        #     agent_results[agent_name] = answer
        #     node = next(n for n in self.ma_args.agents if n.agent == agent_name)
        agent_results = dict(results)
        for agent_name, answer in results:
            yield json.dumps({
                "type": "agent_result",
                "agent": agent_name,
                "role": node_map[agent_name].role,
                "content": answer
            }) + "\n"

        # Phase 2: 마지막 에이전트가 종합
        aggregator = self.ma_args.agents[-1]
        context_parts = [f"[{name}의 결과]\n{ans}" for name, ans in agent_results.items()]
        context = "\n\n".join(context_parts)

        yield json.dumps({
            "type": "agent_start",
            "agent": aggregator.agent,
            "role": "종합",
            "phase": "aggregate"
        }) + "\n"

        async for response_obj in self._stream_agent(
            aggregator,
            f"다음은 '{self.ma_args.question}'에 대한 여러 에이전트의 분석 결과입니다. 종합하여 최종 답변을 작성해주세요.",
            context
        ):
            text = response_obj.text or ""
            if text:
                yield json.dumps({
                    "type": "content",
                    "agent": aggregator.agent,
                    "phase": "aggregate",
                    "content": text
                }) + "\n"

        yield json.dumps({"type": "agent_end", "agent": aggregator.agent, "phase": "aggregate"}) + "\n"
        yield json.dumps({"type": "done"}) + "\n"


    async def _run_router(self):
        """
        라우터형: 첫 번째 에이전트가 질문을 분석해 적합한 에이전트를 선택
        - Phase 1: 라우터 에이전트가 질문 분석 → 적합한 에이전트 이름 반환
        - Phase 2: 선택된 에이전트가 실제 답변 생성
        """
        if len(self.ma_args.agents) < 2:
            yield json.dumps({"type": "error", "content": "라우터 모드는 최소 2개 에이전트가 필요합니다."}) + "\n"
            return

        router = self.ma_args.agents[0]
        candidates = self.ma_args.agents[1:]
        candidate_names = [f"- {n.agent}: {n.role}" for n in candidates]
        candidate_list = "\n".join(candidate_names)

        # Phase 1: 라우터가 에이전트 선택
        yield json.dumps({
            "type": "agent_start",
            "agent": router.agent,
            "role": "라우터",
            "phase": "routing"
        }) + "\n"

        routing_prompt = (
            f"다음 질문을 처리하기에 가장 적합한 에이전트를 하나 선택하세요.\n\n"
            f"[후보 에이전트]\n{candidate_list}\n\n"
            f"[질문]\n{self.ma_args.question}\n\n"
            f"선택한 에이전트의 이름만 정확히 응답하세요. 다른 설명은 필요 없습니다."
        )

        router_answer = ""
        async for response_obj in self._stream_agent(router, routing_prompt):
            text = response_obj.text or ""
            if text:
                router_answer += text

        selected_name = router_answer.strip()
        selected_node = next((n for n in candidates if n.agent == selected_name), None)

        yield json.dumps({
            "type": "agent_end",
            "agent": router.agent,
            "phase": "routing",
            "selectedAgent": selected_name
        }) + "\n"

        # 매칭 실패 시 첫 번째 후보 사용
        if not selected_node:
            selected_node = candidates[0]
            yield json.dumps({
                "type": "info",
                "content": f"'{selected_name}'을(를) 찾을 수 없어 '{selected_node.agent}'로 대체합니다."
            }) + "\n"

        # Phase 2: 선택된 에이전트 실행
        yield json.dumps({
            "type": "agent_start",
            "agent": selected_node.agent,
            "role": selected_node.role,
            "phase": "execution"
        }) + "\n"

        async for response_obj in self._stream_agent(selected_node, self.ma_args.question):
            text = response_obj.text or ""
            if text:
                yield json.dumps({
                    "type": "content",
                    "agent": selected_node.agent,
                    "content": text
                }) + "\n"

        yield json.dumps({"type": "agent_end", "agent": selected_node.agent, "phase": "execution"}) + "\n"
        yield json.dumps({"type": "done"}) + "\n"


    def _build_debate_context(self, all_responses: dict, current_round: int, current_agent: str, is_moderator: bool) -> str:
        """토론 컨텍스트 구성"""
        if current_round == 1 and not is_moderator:
            return None  # 첫 라운드는 독립 응답

        parts = []
        for agent_name, responses in all_responses.items():
            if agent_name == current_agent and not is_moderator:
                continue  # 자기 이전 응답은 제외 (모더레이터는 전체 봄)
            latest = responses[-1] if responses else ""
            parts.append(f"[{agent_name}의 의견]\n{latest}")

        return "\n\n".join(parts) if parts else None


    # async def _collect_answer(self, node: AgentNode, human_message: str, context: str = None) -> str:
    #     """에이전트 호출 후 전체 응답 텍스트만 수집 (스트리밍 없이) — 현재 미사용"""
    #     answer = ""
    #     async for response_obj in self._stream_agent(node, human_message, context):
    #         text = response_obj.text or ""
    #         if text:
    #             answer += text
    #     return answer


    @staticmethod
    def _build_context(edges: list[EdgeNode], agent_results: dict, target: str) -> str | None:
        """incoming edge들의 source 결과를 컨텍스트 문자열로 조합"""
        parts = [
            f"[{e.source}의 결과]\n{agent_results[e.source]}"
            for e in edges if e.target == target and e.source in agent_results
        ]
        return "\n\n".join(parts) or None


    async def _evaluate_condition(self, condition: str, agent_answer: str) -> bool:
        """
        LLM으로 edge 조건 평가.
        조건 프롬프트와 에이전트 결과를 넘기면 YES/NO로 판정.
        """
        evaluator = self.ma_args.agents[0]  # 첫 번째 에이전트의 모델로 평가

        eval_system = (
            "당신은 조건 평가자입니다. 주어진 조건과 결과를 보고 조건이 충족되었는지 판단하세요.\n"
            "반드시 YES 또는 NO 한 단어로만 응답하세요."
        )
        eval_human = (
            f"[조건]\n{condition}\n\n"
            f"[에이전트 결과]\n{agent_answer}\n\n"
            f"위 결과가 조건을 충족합니까? YES 또는 NO로 답하세요."
        )

        eval_answer = ""
        async for response_obj in self.ma_args.llm_proxy_client.stream(
            service="solomon",
            vendor=evaluator.vendor,
            model=evaluator.model,
            system_message=eval_system,
            human_message=eval_human,
            session_key=self.ma_args.session_key,
        ):
            text = response_obj.text or ""
            if text:
                eval_answer += text

        return "YES" in eval_answer.strip().upper()


    async def _run_custom(self):
        """
        커스텀 DAG 실행: edge 기반 그래프 순회
        - 위상정렬로 실행 순서 결정
        - 각 edge의 condition을 LLM으로 평가
        - on_failure에 따라 retry / end / 분기 처리
        """
        if not self.ma_args.edges:
            yield json.dumps({"type": "error", "content": "custom 그래프에는 edges가 필요합니다."}) + "\n"
            return

        node_map = {node.agent: node for node in self.ma_args.agents}
        agent_names = [node.agent for node in self.ma_args.agents]

        # 인접 리스트 & 진입 차수 계산
        adjacency = defaultdict(list)
        in_degree = dict.fromkeys(agent_names, 0)

        for edge in self.ma_args.edges:
            adjacency[edge.source].append(edge.target)
            in_degree[edge.target] += 1

        # 위상정렬 (Kahn's algorithm)
        # queue = [name for name in agent_names if in_degree[name] == 0]  # (원본 - list.pop(0)은 O(n))
        queue = deque(name for name in agent_names if in_degree[name] == 0)
        execution_order = []
        while queue:
            current = queue.popleft()
            execution_order.append(current)
            for neighbor in adjacency[current]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

        if len(execution_order) != len(agent_names):
            yield json.dumps({"type": "error", "content": "그래프에 순환(cycle)이 존재합니다."}) + "\n"
            return

        yield json.dumps({
            "type": "graph_start",
            "graphType": "custom",
            "executionOrder": execution_order,
            "totalNodes": len(execution_order)
        }) + "\n"

        # 각 에이전트의 결과 저장
        agent_results = {}
        # 건너뛴 에이전트 추적
        skipped_agents = set()

        for step, agent_name in enumerate(execution_order):
            node = node_map[agent_name]

            # 이미 실행된 에이전트 (fallback으로 먼저 실행된 경우) skip
            if agent_name in agent_results:
                continue

            # 이 노드로 들어오는 edge들 중 하나라도 source가 skip되었으면 이 노드도 skip
            incoming_edges = [e for e in self.ma_args.edges if e.target == agent_name]
            if incoming_edges and all(e.source in skipped_agents for e in incoming_edges):
                skipped_agents.add(agent_name)
                yield json.dumps({
                    "type": "agent_skip",
                    "agent": agent_name,
                    "reason": "모든 선행 에이전트가 건너뛰어짐"
                }) + "\n"
                continue

            # # 선행 에이전트 결과를 컨텍스트로 구성 (원본)
            # context_parts = []
            # for e in incoming_edges:
            #     if e.source in agent_results:
            #         context_parts.append(f"[{e.source}의 결과]\n{agent_results[e.source]}")
            # context = "\n\n".join(context_parts) if context_parts else None
            context = self._build_context(self.ma_args.edges, agent_results, agent_name)

            # 이 노드로 들어오는 edge 중 condition이 있는 것의 retry 설정 확인
            condition_edges = [e for e in incoming_edges if e.condition and e.source in agent_results]

            # 들어오는 edge의 조건 먼저 평가 (이전 에이전트 결과가 조건 충족하는지)
            edge_failed = False
            for edge in condition_edges:
                source_answer = agent_results[edge.source]

                yield json.dumps({
                    "type": "condition_eval",
                    "edge": {"from": edge.source, "to": edge.target},
                    "condition": edge.condition
                }) + "\n"

                passed = await self._evaluate_condition(edge.condition, source_answer)

                yield json.dumps({
                    "type": "condition_result",
                    "edge": {"from": edge.source, "to": edge.target},
                    "passed": passed
                }) + "\n"

                if not passed:
                    # 조건 실패 처리
                    if edge.on_failure == "retry":
                        # source 에이전트 재시도
                        retry_success = False
                        for attempt in range(1, edge.max_retries + 1):
                            yield json.dumps({
                                "type": "retry",
                                "agent": edge.source,
                                "attempt": attempt,
                                "maxRetries": edge.max_retries,
                                "condition": edge.condition
                            }) + "\n"

                            source_node = node_map[edge.source]
                            # retry_context_parts = []  # (원본)
                            # for prev_e in self.ma_args.edges:
                            #     if prev_e.target == edge.source and prev_e.source in agent_results:
                            #         retry_context_parts.append(...)
                            # retry_context = "\n\n".join(retry_context_parts) if retry_context_parts else None
                            retry_context = self._build_context(self.ma_args.edges, agent_results, edge.source)

                            retry_message = (
                                f"{self.ma_args.question}\n\n"
                                f"[주의] 이전 응답이 다음 조건을 충족하지 못했습니다: {edge.condition}\n"
                                f"조건을 충족하도록 다시 응답해주세요."
                            )

                            # 재시도 실행 & 스트리밍
                            retry_answer = ""
                            yield json.dumps({
                                "type": "agent_start",
                                "agent": edge.source,
                                "role": source_node.role,
                                "phase": "retry",
                                "attempt": attempt
                            }) + "\n"

                            async for response_obj in self._stream_agent(source_node, retry_message, retry_context):
                                text = response_obj.text or ""
                                if text:
                                    retry_answer += text
                                    yield json.dumps({
                                        "type": "content",
                                        "agent": edge.source,
                                        "phase": "retry",
                                        "attempt": attempt,
                                        "content": text
                                    }) + "\n"

                            yield json.dumps({
                                "type": "agent_end",
                                "agent": edge.source,
                                "phase": "retry",
                                "attempt": attempt
                            }) + "\n"

                            # 재평가
                            passed = await self._evaluate_condition(edge.condition, retry_answer)
                            yield json.dumps({
                                "type": "condition_result",
                                "edge": {"from": edge.source, "to": edge.target},
                                "passed": passed,
                                "attempt": attempt
                            }) + "\n"

                            if passed:
                                agent_results[edge.source] = retry_answer
                                # # 컨텍스트 갱신 (원본)
                                # context_parts = []
                                # for e2 in incoming_edges:
                                #     if e2.source in agent_results:
                                #         context_parts.append(...)
                                # context = "\n\n".join(context_parts) if context_parts else None
                                context = self._build_context(self.ma_args.edges, agent_results, agent_name)
                                retry_success = True
                                break

                        if not retry_success:
                            yield json.dumps({
                                "type": "retry_exhausted",
                                "agent": edge.source,
                                "condition": edge.condition
                            }) + "\n"
                            edge_failed = True
                            break

                    elif edge.on_failure == "end":
                        yield json.dumps({
                            "type": "edge_end",
                            "edge": {"from": edge.source, "to": edge.target},
                            "reason": f"조건 미충족: {edge.condition}"
                        }) + "\n"
                        edge_failed = True
                        break

                    else:
                        # on_failure가 에이전트명 → 해당 에이전트로 분기
                        fallback_name = edge.on_failure
                        if fallback_name in node_map and fallback_name not in agent_results:
                            yield json.dumps({
                                "type": "edge_redirect",
                                "from": edge.source,
                                "originalTarget": edge.target,
                                "redirectTo": fallback_name,
                                "reason": f"조건 미충족: {edge.condition}"
                            }) + "\n"

                            fallback_node = node_map[fallback_name]
                            fallback_context = f"[{edge.source}의 결과]\n{agent_results[edge.source]}"

                            yield json.dumps({
                                "type": "agent_start",
                                "agent": fallback_name,
                                "role": fallback_node.role,
                                "phase": "fallback"
                            }) + "\n"

                            fallback_answer = ""
                            async for response_obj in self._stream_agent(fallback_node, self.ma_args.question, fallback_context):
                                text = response_obj.text or ""
                                if text:
                                    fallback_answer += text
                                    yield json.dumps({
                                        "type": "content",
                                        "agent": fallback_name,
                                        "phase": "fallback",
                                        "content": text
                                    }) + "\n"

                            agent_results[fallback_name] = fallback_answer
                            yield json.dumps({
                                "type": "agent_end",
                                "agent": fallback_name,
                                "phase": "fallback"
                            }) + "\n"

                        # 현재 노드는 skip하되, fallback 결과는 agent_results에 저장됨
                        # → fallback에서 나가는 edge의 target 노드들이 후속 실행 시 fallback 결과를 컨텍스트로 받음
                        edge_failed = True
                        break

            if edge_failed:
                skipped_agents.add(agent_name)
                continue

            # 에이전트 실행
            yield json.dumps({
                "type": "agent_start",
                "agent": agent_name,
                "role": node.role,
                "step": step + 1,
                "totalSteps": len(execution_order)
            }) + "\n"

            meta = {"agent": agent_name, "step": step + 1}
            answer = ""
            async for response_obj in self._stream_agent(node, self.ma_args.question, context):
                text = response_obj.text or ""
                if text:
                    answer += text
                    yield json.dumps({**meta, "type": "content", "content": text}) + "\n"

            agent_results[agent_name] = answer

            yield json.dumps({"type": "agent_end", **meta}) + "\n"

        yield json.dumps({"type": "done"}) + "\n"
