export type Tenant = { id: string; name: string }
export type Customer = { id: string; name: string; segment?: string | null; preferences: Record<string, unknown> }
export type Product = { id: string; tenant_id: string; name: string; category: string; brand: string; price: number; popularity: number }
export type InventoryRow = {
  inventory_id: string; sku_id: string; sku_code: string; product_id: string; product_name: string;
  category: string; brand: string; price: number; warehouse_id: string; warehouse_name: string;
  on_hand: number; reserved: number; available: number; version: number;
}
export type LedgerRow = {
  id: string; tenant_id: string; sku_id: string; warehouse_id: string; event_type: string;
  quantity_delta: number; reference_id?: string | null; created_at?: string | null;
}
export type RecommendationItem = {
  product_id: string; name: string; category?: string; brand?: string; price?: number; score: number;
  rank: number; available?: number; sku_ids?: string[]; reasons?: Record<string, number | string | boolean>;
}
export type Recommendation = {
  recommendation_id: string; tenant_id: string; customer_id: string; model_name: string; model_version: string;
  profile?: Record<string, unknown>; items: RecommendationItem[];
}
export type AgentRun = { id: string; tenant_id: string; customer_id?: string | null; status: string; input_text?: string | null; output_text?: string | null }
export type AgentEvent = { agent: string; event_type: string; payload: Record<string, unknown>; created_at: string }
