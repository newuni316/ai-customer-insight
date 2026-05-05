"""订单 CRUD 路由"""
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from database import get_db
from models import User, Order
from schemas import OrderCreate, OrderResponse
from auth import get_current_user
from services.profile_updater import update_user_profile

router = APIRouter(prefix="/api/orders", tags=["订单管理"])


@router.post("", response_model=OrderResponse)
def create_order(
    data: OrderCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """创建订单并自动更新用户画像"""
    order = Order(
        user_id=current_user.id,
        amount=data.amount,
        product=data.product,
        status=data.status,
    )
    db.add(order)
    db.flush()

    # 自动更新用户画像
    update_user_profile(current_user.id, db)
    db.commit()
    db.refresh(order)
    return order


@router.get("", response_model=list[OrderResponse])
def list_orders(
    user_id: Optional[int] = None,
    status: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """查询订单列表，支持筛选和分页"""
    query = db.query(Order).filter(Order.user_id == current_user.id)

    if user_id:
        query = query.filter(Order.user_id == user_id)
    if status:
        query = query.filter(Order.status == status)
    if start_date:
        query = query.filter(Order.created_at >= datetime.fromisoformat(start_date))
    if end_date:
        query = query.filter(Order.created_at <= datetime.fromisoformat(end_date))

    return query.order_by(Order.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()


@router.get("/{order_id}", response_model=OrderResponse)
def get_order(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """查询单个订单详情"""
    order = db.query(Order).filter(Order.id == order_id, Order.user_id == current_user.id).first()
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")
    return order
