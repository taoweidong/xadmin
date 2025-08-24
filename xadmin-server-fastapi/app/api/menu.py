"""
菜单管理API路由
"""
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import require_permission, get_current_active_user
from app.schemas.base import BaseResponse, ListResponse, BatchDeleteRequest
from app.schemas.menu import (
    MenuProfile, MenuCreate, MenuUpdate, MenuListParams, MenuBatchDeleteRequest
)
from app.services.menu import MenuService
from app.models.user import UserInfo
from app.models.system import MenuInfo
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("", response_model=ListResponse[List[MenuProfile]])
async def get_menu_list(
    params: MenuListParams = Depends(),
    db: Session = Depends(get_db),
    current_user: UserInfo = Depends(require_permission("menu:read"))
):
    """获取菜单列表"""
    menu_service = MenuService(db)
    
    # 构建过滤条件
    filters = {}
    if params.search:
        filters['search'] = params.search
    if params.name:
        filters['name'] = params.name
    if params.component:
        filters['component'] = params.component
    if params.path:
        filters['path'] = params.path
    
    result = menu_service.get_menu_list(params, filters)
    
    # 转换为响应格式
    menu_profiles = []
    for menu in result['results']:
        # 获取父菜单信息
        parent_info = None
        if menu.parent:
            parent_info = {
                'id': menu.parent.id,
                'name': menu.parent.name
            }
        
        # 构建菜单元数据
        meta_profile = {
            'id': menu.meta.id,
            'title': menu.meta.title,
            'icon': menu.meta.icon,
            'r_svg_name': menu.meta.r_svg_name,
            'is_show_menu': menu.meta.is_show_menu,
            'is_show_parent': menu.meta.is_show_parent,
            'is_keepalive': menu.meta.is_keepalive,
            'frame_url': menu.meta.frame_url,
            'frame_loading': menu.meta.frame_loading,
            'transition_enter': menu.meta.transition_enter,
            'transition_leave': menu.meta.transition_leave,
            'is_hidden_tag': menu.meta.is_hidden_tag,
            'fixed_tag': menu.meta.fixed_tag,
            'dynamic_level': menu.meta.dynamic_level,
            'created_at': menu.meta.created_at,
            'updated_at': menu.meta.updated_at
        } if menu.meta else None
        
        # 获取关联模型ID列表
        model_ids = [model.id for model in menu.model] if menu.model else []
        
        profile = MenuProfile(
            id=menu.id,
            name=menu.name,
            rank=menu.sort,
            path=menu.path,
            component=menu.component,
            menu_type=menu.menu_type,
            is_active=menu.is_active,
            method=menu.method,
            parent_id=menu.parent_id,
            model_ids=model_ids,
            created_at=menu.created_at,
            updated_at=menu.updated_at,
            meta=meta_profile
        )
        menu_profiles.append(profile)
    
    return ListResponse(
        code=1000,
        detail="success",
        data={
            "results": menu_profiles,
            "total": result['total'],
            "page": result['page'],
            "size": result['size'],
            "pages": result['pages']
        }
    )


@router.post("", response_model=BaseResponse[MenuProfile])
async def create_menu(
    menu_data: MenuCreate,
    db: Session = Depends(get_db),
    current_user: UserInfo = Depends(require_permission("menu:create"))
):
    """创建菜单"""
    menu_service = MenuService(db)
    
    # 检查菜单名称是否已存在
    if menu_service.check_name_exists(menu_data.name):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="菜单名称已存在"
        )
    
    # 检查父菜单是否有效
    if menu_data.parent_id:
        parent_menu = menu_service.get_by_id(menu_data.parent_id)
        if not parent_menu:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="父菜单不存在"
            )
    
    # 创建菜单
    try:
        created_menu = menu_service.create_menu(menu_data)
        # 构建返回数据
        meta_profile = {
            'id': created_menu.meta.id,
            'title': created_menu.meta.title,
            'icon': created_menu.meta.icon,
            'r_svg_name': created_menu.meta.r_svg_name,
            'is_show_menu': created_menu.meta.is_show_menu,
            'is_show_parent': created_menu.meta.is_show_parent,
            'is_keepalive': created_menu.meta.is_keepalive,
            'frame_url': created_menu.meta.frame_url,
            'frame_loading': created_menu.meta.frame_loading,
            'transition_enter': created_menu.meta.transition_enter,
            'transition_leave': created_menu.meta.transition_leave,
            'is_hidden_tag': created_menu.meta.is_hidden_tag,
            'fixed_tag': created_menu.meta.fixed_tag,
            'dynamic_level': created_menu.meta.dynamic_level,
            'created_at': created_menu.meta.created_at,
            'updated_at': created_menu.meta.updated_at
        } if created_menu.meta else None
        
        # 获取关联模型ID列表
        model_ids = [model.id for model in created_menu.model] if created_menu.model else []
        
        profile = MenuProfile(
            id=created_menu.id,
            name=created_menu.name,
            rank=created_menu.sort,
            path=created_menu.path,
            component=created_menu.component,
            menu_type=created_menu.menu_type,
            is_active=created_menu.is_active,
            method=created_menu.method,
            parent_id=created_menu.parent_id,
            model_ids=model_ids,
            created_at=created_menu.created_at,
            updated_at=created_menu.updated_at,
            meta=meta_profile
        )
        
        return BaseResponse(
            code=1000,
            detail="菜单创建成功",
            data=profile
        )
    except Exception as e:
        logger.error(f"创建菜单失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="创建菜单失败"
        )


@router.get("/{menu_id}", response_model=BaseResponse[MenuProfile])
async def get_menu_detail(
    menu_id: int,
    db: Session = Depends(get_db),
    current_user: UserInfo = Depends(require_permission("menu:read"))
):
    """获取菜单详情"""
    menu_service = MenuService(db)
    menu = menu_service.get_by_id(menu_id)
    
    if not menu:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="菜单不存在"
        )
    
    # 构建返回数据
    meta_profile = {
        'id': menu.meta.id,
        'title': menu.meta.title,
        'icon': menu.meta.icon,
        'r_svg_name': menu.meta.r_svg_name,
        'is_show_menu': menu.meta.is_show_menu,
        'is_show_parent': menu.meta.is_show_parent,
        'is_keepalive': menu.meta.is_keepalive,
        'frame_url': menu.meta.frame_url,
        'frame_loading': menu.meta.frame_loading,
        'transition_enter': menu.meta.transition_enter,
        'transition_leave': menu.meta.transition_leave,
        'is_hidden_tag': menu.meta.is_hidden_tag,
        'fixed_tag': menu.meta.fixed_tag,
        'dynamic_level': menu.meta.dynamic_level,
        'created_at': menu.meta.created_at,
        'updated_at': menu.meta.updated_at
    } if menu.meta else None
    
    # 获取关联模型ID列表
    model_ids = [model.id for model in menu.model] if menu.model else []
    
    profile = MenuProfile(
        id=menu.id,
        name=menu.name,
        rank=menu.sort,
        path=menu.path,
        component=menu.component,
        menu_type=menu.menu_type,
        is_active=menu.is_active,
        method=menu.method,
        parent_id=menu.parent_id,
        model_ids=model_ids,
        created_at=menu.created_at,
        updated_at=menu.updated_at,
        meta=meta_profile
    )
    
    return BaseResponse(
        code=1000,
        detail="success",
        data=profile
    )


@router.put("/{menu_id}", response_model=BaseResponse[MenuProfile])
async def update_menu(
    menu_id: int,
    menu_data: MenuUpdate,
    db: Session = Depends(get_db),
    current_user: UserInfo = Depends(require_permission("menu:update"))
):
    """更新菜单"""
    menu_service = MenuService(db)
    
    # 检查菜单是否存在
    existing_menu = menu_service.get_by_id(menu_id)
    if not existing_menu:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="菜单不存在"
        )
    
    # 检查菜单名称是否已存在（排除自己）
    if menu_data.name and menu_service.check_name_exists(menu_data.name, menu_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="菜单名称已存在"
        )
    
    # 检查父菜单是否有效
    if menu_data.parent_id:
        if menu_data.parent_id == menu_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="不能将自己设置为父菜单"
            )
        
        parent_menu = menu_service.get_by_id(menu_data.parent_id)
        if not parent_menu:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="父菜单不存在"
            )
    
    # 更新菜单
    try:
        updated_menu = menu_service.update_menu(menu_id, menu_data)
        if not updated_menu:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="更新菜单失败"
            )
        
        # 构建返回数据
        meta_profile = {
            'id': updated_menu.meta.id,
            'title': updated_menu.meta.title,
            'icon': updated_menu.meta.icon,
            'r_svg_name': updated_menu.meta.r_svg_name,
            'is_show_menu': updated_menu.meta.is_show_menu,
            'is_show_parent': updated_menu.meta.is_show_parent,
            'is_keepalive': updated_menu.meta.is_keepalive,
            'frame_url': updated_menu.meta.frame_url,
            'frame_loading': updated_menu.meta.frame_loading,
            'transition_enter': updated_menu.meta.transition_enter,
            'transition_leave': updated_menu.meta.transition_leave,
            'is_hidden_tag': updated_menu.meta.is_hidden_tag,
            'fixed_tag': updated_menu.meta.fixed_tag,
            'dynamic_level': updated_menu.meta.dynamic_level,
            'created_at': updated_menu.meta.created_at,
            'updated_at': updated_menu.meta.updated_at
        } if updated_menu.meta else None
        
        # 获取关联模型ID列表
        model_ids = [model.id for model in updated_menu.model] if updated_menu.model else []
        
        profile = MenuProfile(
            id=updated_menu.id,
            name=updated_menu.name,
            rank=updated_menu.sort,
            path=updated_menu.path,
            component=updated_menu.component,
            menu_type=updated_menu.menu_type,
            is_active=updated_menu.is_active,
            method=updated_menu.method,
            parent_id=updated_menu.parent_id,
            model_ids=model_ids,
            created_at=updated_menu.created_at,
            updated_at=updated_menu.updated_at,
            meta=meta_profile
        )
        
        return BaseResponse(
            code=1000,
            detail="菜单更新成功",
            data=profile
        )
    except Exception as e:
        logger.error(f"更新菜单失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="更新菜单失败"
        )


@router.delete("/{menu_id}", response_model=BaseResponse[None])
async def delete_menu(
    menu_id: int,
    db: Session = Depends(get_db),
    current_user: UserInfo = Depends(require_permission("menu:delete"))
):
    """删除菜单"""
    menu_service = MenuService(db)
    
    # 检查是否可以删除
    can_delete, message = menu_service.check_can_delete(menu_id)
    if not can_delete:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message
        )
    
    # 删除菜单
    result = menu_service.delete_menu(menu_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="删除菜单失败"
        )
    
    return BaseResponse(
        code=1000,
        detail="菜单删除成功",
        data=None
    )


@router.post("/batch-delete", response_model=BaseResponse[None])
async def batch_delete_menus(
    request: MenuBatchDeleteRequest,
    db: Session = Depends(get_db),
    current_user: UserInfo = Depends(require_permission("menu:delete"))
):
    """批量删除菜单"""
    menu_service = MenuService(db)
    
    # 检查每个菜单是否可以删除
    for menu_id in request.pks:
        can_delete, message = menu_service.check_can_delete(menu_id)
        if not can_delete:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"菜单ID {menu_id}: {message}"
            )
    
    # 批量删除
    success_count = 0
    for menu_id in request.pks:
        if menu_service.delete_menu(menu_id):
            success_count += 1
    
    if success_count != len(request.pks):
        logger.warning(f"批量删除菜单部分失败: 成功{success_count}/{len(request.pks)}")
    
    return BaseResponse(
        code=1000,
        detail=f"菜单批量删除成功，成功删除{success_count}个菜单",
        data=None
    )