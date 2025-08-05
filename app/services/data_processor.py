import asyncio
from typing import Dict, Any, List, Optional
from motor.motor_asyncio import AsyncIOMotorClient
from app.config.settings import settings

class DataProcessorService:
    def __init__(self):
        self.client = AsyncIOMotorClient(settings.mongodb_uri)
        self.db = self.client[settings.mongodb_db_name]

    async def get_inventory_data(self, company_id: str) -> Dict[str, Any]:
        """Get inventory data for a company"""
        try:
            # Get products
            products = await self.db.products.find(
                {"company": company_id}
            ).to_list(length=None)
            
            # Get raw materials
            raw_materials = await self.db.rawmaterials.find(
                {"company": company_id}
            ).to_list(length=None)
            
            # Get inventory movements
            movements = await self.db.movements.find(
                {"company": company_id}
            ).to_list(length=None)
            
            # Calculate statistics
            total_products = len(products)
            total_raw_materials = len(raw_materials)
            low_stock_items = sum(1 for p in products if p.get('stock', 0) <= p.get('stockMinimo', 0))
            low_stock_items += sum(1 for r in raw_materials if r.get('stock', 0) <= r.get('stockMinimo', 0))
            
            return {
                "products": products,
                "raw_materials": raw_materials,
                "movements": movements,
                "statistics": {
                    "total_products": total_products,
                    "total_raw_materials": total_raw_materials,
                    "low_stock_items": low_stock_items,
                    "total_movements": len(movements)
                }
            }
        except Exception as e:
            print(f"❌ Error getting inventory data: {e}")
            return {
                "products": [],
                "raw_materials": [],
                "movements": [],
                "statistics": {
                    "total_products": 0,
                    "total_raw_materials": 0,
                    "low_stock_items": 0,
                    "total_movements": 0
                }
            }

    async def get_company_info(self, company_id: str) -> Dict[str, Any]:
        """Get company information"""
        try:
            # Get company info from users collection
            company_user = await self.db.users.find_one(
                {"company": company_id, "role": "empresajefe"}
            )
            
            if company_user:
                return {
                    "company_id": company_id,
                    "company_name": company_user.get('companyName', 'Unknown'),
                    "admin_user": company_user.get('name', 'Unknown'),
                    "email": company_user.get('email', ''),
                    "created_at": company_user.get('createdAt', ''),
                    "status": "active"
                }
            else:
                return {
                    "company_id": company_id,
                    "company_name": "Unknown",
                    "admin_user": "Unknown",
                    "email": "",
                    "created_at": "",
                    "status": "not_found"
                }
        except Exception as e:
            print(f"❌ Error getting company info: {e}")
            return {
                "company_id": company_id,
                "company_name": "Unknown",
                "admin_user": "Unknown",
                "email": "",
                "created_at": "",
                "status": "error"
            }

    async def format_inventory_for_rag(self, inventory_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Format inventory data for RAG indexing"""
        try:
            formatted_data = []
            
            # Format products
            for product in inventory_data.get('products', []):
                formatted_data.append({
                    "content": f"Producto: {product.get('name', 'Unknown')} - Stock: {product.get('stock', 0)} - Precio: {product.get('precio', 0)} - Categoría: {product.get('categoria', 'Unknown')}",
                    "metadata": {
                        "type": "product",
                        "id": str(product.get('_id', '')),
                        "name": product.get('name', ''),
                        "stock": product.get('stock', 0),
                        "precio": product.get('precio', 0),
                        "categoria": product.get('categoria', ''),
                        "company": product.get('company', '')
                    }
                })
            
            # Format raw materials
            for material in inventory_data.get('raw_materials', []):
                formatted_data.append({
                    "content": f"Materia Prima: {material.get('name', 'Unknown')} - Stock: {material.get('stock', 0)} - Precio: {material.get('precio', 0)} - Proveedor: {material.get('proveedor', 'Unknown')}",
                    "metadata": {
                        "type": "raw_material",
                        "id": str(material.get('_id', '')),
                        "name": material.get('name', ''),
                        "stock": material.get('stock', 0),
                        "precio": material.get('precio', 0),
                        "proveedor": material.get('proveedor', ''),
                        "company": material.get('company', '')
                    }
                })
            
            # Format movements
            for movement in inventory_data.get('movements', []):
                formatted_data.append({
                    "content": f"Movimiento: {movement.get('tipo', 'Unknown')} - Producto: {movement.get('productName', 'Unknown')} - Cantidad: {movement.get('cantidad', 0)} - Fecha: {movement.get('fecha', 'Unknown')}",
                    "metadata": {
                        "type": "movement",
                        "id": str(movement.get('_id', '')),
                        "tipo": movement.get('tipo', ''),
                        "productName": movement.get('productName', ''),
                        "cantidad": movement.get('cantidad', 0),
                        "fecha": movement.get('fecha', ''),
                        "company": movement.get('company', '')
                    }
                })
            
            return formatted_data
        except Exception as e:
            print(f"❌ Error formatting inventory for RAG: {e}")
            return []
