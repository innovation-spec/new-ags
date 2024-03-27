from __future__ import annotations
import json, uuid
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.domain import AgentRun, AgentEvent
from app.llm.client import LLMClient
from app.llm.tools import build_tool_registry, dispatch_tool, openai_tool_specs
from app.services.recommendation.service import RecommendationService

class AgentService:
    def __init__(self, db: Session, llm_client=None):
        self.db = db
        self.llm_client = llm_client or LLMClient()

    def _event(self, run: AgentRun, event_type: str, payload: dict | None = None, agent_name: str = "Supervisor Agent"):
        self.db.add(AgentEvent(
            id=str(uuid.uuid4()), tenant_id=run.tenant_id, run_id=run.id,
            agent_name=agent_name, event_type=event_type, payload=payload or {},
        ))
        run.status = event_type if event_type in {"PLANNING", "RUNNING", "WAITING_TOOL", "VALIDATING", "COMPLETED", "FAILED", "CANCELLED", "TIMED_OUT"} else run.status
        self.db.commit()

    def chat(self, tenant_id: str, customer_id: str, message: str) -> dict:
        run = AgentRun(id=str(uuid.uuid4()), tenant_id=tenant_id, customer_id=customer_id, status="CREATED", input_text=message)
        self.db.add(run); self.db.commit()
        self._event(run, "CREATED", {"message": message})
        self._event(run, "PLANNING")

        deterministic = RecommendationService(self.db).generate(tenant_id, customer_id, limit=5)
        if deterministic is None:
            self._event(run, "FAILED", {"error": "customer not found"})
            return {"run": self._serialize_run(run), "llm_enabled": self.llm_client.enabled, "answer": "Customer not found.", "recommendations": []}

        self._event(run, "RUNNING", {"backend_recommendation_id": deterministic["recommendation_id"]})
        registry = build_tool_registry(self.db, tenant_id, customer_id)
        dispatch = lambda name, args: dispatch_tool(registry, name, args)
        safe_summary = [{
            "product_id": item["product_id"], "name": item["name"], "price": item["price"],
            "available": item["available"], "score": item["score"],
        } for item in deterministic["items"]]
        instructions = (
            "You are the Agasthya retail Supervisor Agent. Authoritative product selection is already computed by the backend. "
            "You may use the supplied tools for verified context. Do not invent product IDs, prices, inventory, or tenant data. "
            "Explain only the backend recommendations supplied here: " + json.dumps(safe_summary)
        )
        llm_result = self.llm_client.chat(message, openai_tool_specs(), dispatch, instructions=instructions)
        for call in llm_result.tool_calls:
            self._event(run, "WAITING_TOOL", {"tool": call["name"], "arguments": call["arguments"]}, agent_name="Tool Gateway")
            self._event(run, "RUNNING", {"tool": call["name"], "output": call["output"]}, agent_name="Tool Gateway")
        self._event(run, "VALIDATING", {"authoritative_product_ids": [x["product_id"] for x in safe_summary]})
        answer = llm_result.text
        run.output_text = answer
        self._event(run, "COMPLETED", {"llm_enabled": llm_result.enabled, "llm_error": llm_result.error})
        return {
            "run": self._serialize_run(run), "llm_enabled": llm_result.enabled,
            "answer": answer, "recommendations": deterministic["items"],
            "tool_calls": llm_result.tool_calls,
