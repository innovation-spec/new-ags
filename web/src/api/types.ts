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
