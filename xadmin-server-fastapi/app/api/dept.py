"""
部门管理API路由
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import require_permission, get_current_active_user
from app.schemas.base import BaseResponse, ListResponse, BatchDeleteRequest
from app.schemas.dept import (
    DeptProfile, DeptCreate, DeptUpdate, DeptListParams, DeptBatchDeleteRequest
)
from app.services.dept import DeptService
from app.models.user import UserInfo, DeptInfo
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("", response_model=ListResponse[List[DeptProfile]])
async def get_dept_list(
    params: DeptListParams = Depends(),
    db: Session = Depends(get_db),
    current_user: UserInfo = Depends(require_permission("dept:read"))
):
    """获取部门列表"""
    dept_service = DeptService(db)
    
    # 构建过滤条件
    filters = {}
    if params.search:
        filters['search'] = params.search
    if params.is_active is not None:
        filters['is_active'] = params.is_active
    if params.code:
        filters['code'] = params.code
    if params.mode_type is not None:
        filters['mode_type'] = params.mode_type
    if params.auto_bind is not None:
        filters['auto_bind'] = params.auto_bind
    if params.name:
        filters['name'] = params.name
    if params.description:
        filters['description'] = params.description
    if params.pk:
        filters['pk'] = params.pk
    
    result = dept_service.get_dept_list(params, filters)
    
    # 转换为响应格式
    dept_profiles = []
    for dept in result['results']:
        # 获取父部门信息
        parent_info = None
        if dept.parent:
            parent_info = {
                'id': dept.parent.id,
                'name': dept.parent.name,
                'code': dept.parent.code
            }
        
        profile = DeptProfile(
            id=dept.id,
            name=dept.name,
            code=dept.code,
            parent_id=dept.parent_id,
            is_active=dept.is_active,
            rank=dept.sort,
            mode_type=dept.mode_type,
            auto_bind=dept.auto_bind,
            description=dept.description,
            created_at=dept.created_at,
            updated_at=dept.updated_at,
            user_count=len(dept.users) if dept.users else 0
        )
        dept_profiles.append(profile)
    
    return ListResponse(
        code=1000,
        detail="success",
        data={
            "results": dept_profiles,
            "total": result['total'],
            "page": result['page'],
            "size": result['size'],
            "pages": result['pages']
        }
    )


@router.post("", response_model=BaseResponse[DeptProfile])
async def create_dept(
    dept_data: DeptCreate,
    db: Session = Depends(get_db),
    current_user: UserInfo = Depends(require_permission("dept:create"))
):
    """创建部门"""
    dept_service = DeptService(db)
    
    # 检查部门编码是否已存在
    if dept_service.check_code_exists(dept_data.code):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="部门编码已存在"
        )
    
    # 检查父部门是否有效
    if dept_data.parent_id:
        parent_dept = dept_service.get_by_id(dept_data.parent_id)
        if not parent_dept:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="父部门不存在"
            )
    
    # 创建部门
    try:
        created_dept = dept_service.create_dept(dept_data.model_dump())
        profile = DeptProfile(
            id=created_dept.id,
            name=created_dept.name,
            code=created_dept.code,
            parent_id=created_dept.parent_id,
            is_active=created_dept.is_active,
            rank=created_dept.sort,
            mode_type=created_dept.mode_type,
            auto_bind=created_dept.auto_bind,
            description=created_dept.description,
            created_at=created_dept.created_at,
            updated_at=created_dept.updated_at,
            user_count=0
        )
        return BaseResponse(
            code=1000,
            detail="部门创建成功",
            data=profile
        )
    except Exception as e:
        logger.error(f"创建部门失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="创建部门失败"
        )


@router.get("/{dept_id}", response_model=BaseResponse[DeptProfile])
async def get_dept_detail(
    dept_id: int,
    db: Session = Depends(get_db),
    current_user: UserInfo = Depends(require_permission("dept:read"))
):
    """获取部门详情"""
    dept_service = DeptService(db)
    dept = dept_service.get_by_id(dept_id)
    
    if not dept:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="部门不存在"
        )
    
    # 获取父部门信息
    parent_info = None
    if dept.parent:
        parent_info = {
            'id': dept.parent.id,
            'name': dept.parent.name,
            'code': dept.parent.code
        }
    
    profile = DeptProfile(
        id=dept.id,
        name=dept.name,
        code=dept.code,
        parent_id=dept.parent_id,
        is_active=dept.is_active,
        rank=dept.sort,
        mode_type=dept.mode_type,
        auto_bind=dept.auto_bind,
        description=dept.description,
        created_at=dept.created_at,
        updated_at=dept.updated_at,
        user_count=len(dept.users) if dept.users else 0
    )
    
    return BaseResponse(
        code=1000,
        detail="success",
        data=profile
    )


@router.put("/{dept_id}", response_model=BaseResponse[DeptProfile])
async def update_dept(
    dept_id: int,
    dept_data: DeptUpdate,
    db: Session = Depends(get_db),
    current_user: UserInfo = Depends(require_permission("dept:update"))
):
    """更新部门"""
    dept_service = DeptService(db)
    
    # 检查部门是否存在
    existing_dept = dept_service.get_by_id(dept_id)
    if not existing_dept:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="部门不存在"
        )
    
    # 检查部门编码是否已存在（排除自己）
    if dept_data.code and dept_service.check_code_exists(dept_data.code, dept_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="部门编码已存在"
        )
    
    # 检查父部门是否有效
    if dept_data.parent_id:
        if dept_data.parent_id == dept_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="不能将自己设置为父部门"
            )
        
        parent_dept = dept_service.get_by_id(dept_data.parent_id)
        if not parent_dept:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="父部门不存在"
            )
        
        # 检查父部门是否有效（避免循环引用）
        if not dept_service.check_parent_valid(dept_id, dept_data.parent_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="父部门设置无效，不能形成循环引用"
            )
    
    # 更新部门
    try:
        updated_dept = dept_service.update_dept(dept_id, dept_data.model_dump(exclude_unset=True))
        if not updated_dept:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="更新部门失败"
            )
        
        profile = DeptProfile(
            id=updated_dept.id,
            name=updated_dept.name,
            code=updated_dept.code,
            parent_id=updated_dept.parent_id,
            is_active=updated_dept.is_active,
            rank=updated_dept.sort,
            mode_type=updated_dept.mode_type,
            auto_bind=updated_dept.auto_bind,
            description=updated_dept.description,
            created_at=updated_dept.created_at,
            updated_at=updated_dept.updated_at,
            user_count=len(updated_dept.users) if updated_dept.users else 0
        )
        
        return BaseResponse(
            code=1000,
            detail="部门更新成功",
            data=profile
        )
    except Exception as e:
        logger.error(f"更新部门失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="更新部门失败"
        )


@router.delete("/{dept_id}", response_model=BaseResponse[None])
async def delete_dept(
    dept_id: int,
    db: Session = Depends(get_db),
    current_user: UserInfo = Depends(require_permission("dept:delete"))
):
    """删除部门"""
    dept_service = DeptService(db)
    
    # 检查是否可以删除
    can_delete, message = dept_service.check_can_delete(dept_id)
    if not can_delete:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message
        )
    
    # 删除部门
    result = dept_service.delete_dept(dept_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="删除部门失败"
        )
    
    return BaseResponse(
        code=1000,
        detail="部门删除成功",
        data=None
    )


@router.post("/batch-delete", response_model=BaseResponse[None])
async def batch_delete_depts(
    request: DeptBatchDeleteRequest,
    db: Session = Depends(get_db),
    current_user: UserInfo = Depends(require_permission("dept:delete"))
):
    """批量删除部门"""
    dept_service = DeptService(db)
    
    # 检查每个部门是否可以删除
    for dept_id in request.pks:
        can_delete, message = dept_service.check_can_delete(dept_id)
        if not can_delete:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"部门ID {dept_id}: {message}"
            )
    
    # 批量删除
    success_count = 0
    for dept_id in request.pks:
        if dept_service.delete_dept(dept_id):
            success_count += 1
    
    if success_count != len(request.pks):
        logger.warning(f"批量删除部门部分失败: 成功{success_count}/{len(request.pks)}")
    
    return BaseResponse(
        code=1000,
        detail=f"部门批量删除成功，成功删除{success_count}个部门",
        data=None
    )